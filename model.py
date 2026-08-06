import torch
import torch.nn as nn
import numpy as np

from functools import partial

import math

import misc

from timm.models.layers import trunc_normal_
from timm.models.layers import DropPath

#from extensions.chamfer_dist import ChamferDistanceL1, ChamferDistanceL2
from mamba_ssm.modules.mamba_simple import Mamba

try:
    from mamba_ssm.ops.triton.layernorm import RMSNorm, layer_norm_fn, rms_norm_fn
except ImportError:
    RMSNorm, layer_norm_fn, rms_norm_fn = None, None, None

#from knn_cuda import KNN
from block import Block

class KNN(nn.Module):
    """Drop-in for knn_cuda.KNN with transpose_mode=True."""
    def __init__(self, k, transpose_mode=True):
        super().__init__()
        self.k = k

    @torch.no_grad()
    def forward(self, ref, query):
        # ref: (B, N, C), query: (B, M, C) -> dist, idx both (B, M, k)
        dist = torch.cdist(query, ref)          # (B, M, N)
        d, idx = dist.topk(self.k, dim=-1, largest=False)
        return d, idx

class Encoder(nn.Module):
    def __init__(self, encoder_channel):
        super().__init__()
        self.encoder_channel = encoder_channel
        self.first_conv = nn.Sequential(
            nn.Conv1d(3, 128, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Conv1d(128, 256, 1)
        ).to(device="cuda")
        self.second_conv = nn.Sequential(
            nn.Conv1d(512, 512, 1),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Conv1d(512, self.encoder_channel, 1)
        ).to(device="cuda")

    def forward(self, point_groups):
        bs, g, n, _ = point_groups.shape
        point_groups = point_groups.reshape(bs * g, n, 3)
        feature = self.first_conv(point_groups.transpose(2, 1))
        feature_global = torch.max(feature, dim=2, keepdim=True)[0]
        feature = torch.cat([feature_global.expand(-1, -1, n), feature], dim=1)
        feature =  self.second_conv(feature)
        feature_global = torch.max(feature, dim=2, keepdim=False)[0]
        return feature_global.reshape(bs, g, self.encoder_channel)
    
class Group(nn.Module):
    def __init__(self, num_group, group_size):
        super().__init__()
        self.num_group = num_group
        self.group_size = group_size
        self.knn = KNN(k=self.group_size, transpose_mode=True)

    def forward(self,  xyz):
        batch_size, num_points, _ = xyz.shape
        center = misc.fps(xyz, self.num_group)

        _, idx = self.knn(xyz, center)
        assert idx.size(1) == self.num_group
        assert idx.size(2) == self.group_size
        # print(torch.arange(0, batch_size, device=xyz.device).view(-1, 1, 1) * num_points)
        idx_base = torch.arange(0, batch_size, device=xyz.device).view(-1, 1, 1) * num_points
        # print(idx)
        # print(idx.shape)
        idx = idx + idx_base
        # print(idx)
        # print(idx.shape)
        # print(idx.view(-1))
        # print(idx.view(-1).shape)
        idx = idx.view(-1)
        # print(batch_size)
        # print(num_points)
        # print(idx.size(1))
        # print(xyz)
        # print(xyz.shape)
        # print(xyz.view(batch_size * num_points, -1)[[2000,3000,4000,5000],:])
        # print(xyz.view(batch_size * num_points, -1)[5,:])
        # print(xyz.view(batch_size * num_points, -1).shape)
        neighborhood = xyz.view(batch_size * num_points, -1)[idx, :]
        # print(neighborhood.shape)
        # last dimension changed to 4 from 3 to add in intensity value
        neighborhood = neighborhood.view(batch_size, self.num_group, self.group_size, 3).contiguous()

        neighborhood = neighborhood - center.unsqueeze(2)
        return neighborhood, center
    

def _init_weights(
        module,
        n_layer,
        initializer_range=0.02,
        rescale_prenorm_residual=True,
        n_residuals_per_layer=1
    ):
    if isinstance(module, nn.Linear):
        if module.bias is not None:
            if not getattr(module.bias, "_no_reint", False):
                nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Embedding):
        nn.init.normal_(module.weight, std=initializer_range)

    if rescale_prenorm_residual:
        for name, p in module.named_parameters():
            if name in ["out_proj.weight", "fc2.weight"]:
                nn.init.kaiming_uniform_(p, a=math.sqrt(5))
                with torch.no_grad():
                    p /= math.sqrt(n_residuals_per_layer * n_layer)



def create_block(
        d_model,
        ssm_cfg=None,
        norm_epsilon=1e-5,
        rms_norm=False,
        residual_in_fp32=False,
        fused_add_norm=False,
        layer_idx=None,
        drop_path=0.,
        device=None,
        dtype=None,
):
    if ssm_cfg is None:
        ssm_cfg = {}
    factory_kwargs = {"device": device, "dtype": dtype}

    mixer_cls = partial(Mamba, layer_idx=layer_idx, **ssm_cfg, **factory_kwargs)
    norm_cls = partial(
        nn.LayerNorm if not rms_norm else RMSNorm, eps=norm_epsilon, **factory_kwargs
    )
    block = Block(
        d_model,
        mixer_cls,
        norm_cls=norm_cls,
        fused_add_norm=fused_add_norm,
        residual_in_fp32=residual_in_fp32,
        drop_path=drop_path,
    )
    block.layer_idx = layer_idx
    return block

class MixerModel(nn.Module):
    def __init__(self,
                 d_model: int,
                 n_layer: int,
                 ssm_cfg=None,
                 norm_epsilon: float = 1e-5,
                 rms_norm: bool = False,
                 initializer_cfg=None,
                 fused_add_norm=False,
                 residual_in_fp32=False,
                 drop_out_in_block: int = 0.,
                 drop_path: int = 0.1,
                 device=None,
                 dtype=None,
        ) -> None:
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.residual_in_fp32 = residual_in_fp32
        self.fused_add_norm = fused_add_norm
        if self.fused_add_norm:
            if layer_norm_fn is None or rms_norm_fn is None:
                raise ImportError("Failed to import Triton LayerNorm / RMSNorm kernels")

            
        self.layers = nn.ModuleList(
            [
                create_block(
                    d_model,
                    ssm_cfg=ssm_cfg,
                    norm_epsilon=norm_epsilon,
                    rms_norm=rms_norm,
                    residual_in_fp32=residual_in_fp32,
                    fused_add_norm=fused_add_norm,
                    layer_idx=i,
                    drop_path=drop_path,
                    **factory_kwargs,
                )
                for i in range(n_layer)
            ]
        )

        self.norm_f = (nn.LayerNorm if not rms_norm else RMSNorm)(
            d_model, eps=norm_epsilon, **factory_kwargs
        )

        self.apply(
            partial(
                _init_weights,
                n_layer=n_layer,
                **(initializer_cfg if initializer_cfg is not None else {})
            )
        )
        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
        self.drop_out_in_block = nn.Dropout(drop_out_in_block) if drop_out_in_block > 0. else nn.Identity()

    def allocate_inference_cache(self, batch_size, max_seqlen, dtype=None, **kwargs):
        return {
            i: layer.allocate_inference_cache(batch_size, max_seqlen, dtype=dtype, **kwargs)
            for i, layer in enumerate(self.layers)
        }
    
    def forward(self, input_ids, pos, inference_params=None):
        hidden_states = input_ids
        residual = None
        hidden_states = hidden_states + pos
        for layer in self.layers:
            hidden_states, residual = layer(
                hidden_states, residual #, inference_params=inference_params
            )
            hidden_states = self.drop_out_in_block(hidden_states)
        if not self.fused_add_norm:
            residual = (hidden_states + residual) if residual is not None else hidden_states
            hidden_states = self.norm_f(residual.to(dtype=self.norm_f.weight.dtype))
        else:
            fused_add_norm_fn = rms_norm_fn if isinstance(self.norm_f, RMSNorm) else layer_norm_fn
            hidden_states = fused_add_norm_fn(
                hidden_states,
                self.norm_f.weight,
                self.norm_f.bias,
                eps=self.norm_f.eps,
                residual=residual,
                prenorm=False,
                residual_in_fp32=self.residual_in_fp32,
            )

        return hidden_states
    
class PointMamba(nn.Module):
    def __init__(self, 
                 trans_dim=384,
                 depth=12,
                 cls_dim = 40,
                 group_size= 32,
                 num_group= 64,
                 encoder_dims= 384,
                 rms_norm= False,
                 drop_path= 0.3,
                 drop_out= 0.,
                 drop_out_block= 0.,
                 use_cls_token=False,
                #  config=None, 
                 **kwargs):
        super(PointMamba, self).__init__()
        # self.config = config

        self.trans_dim = trans_dim
        self.depth = depth
        self.cls_dim = cls_dim


        self.group_size = group_size
        self.num_group = num_group
        self.encoder_dims = encoder_dims

        self.group_divider = Group(num_group=self.num_group, group_size=self.group_size)

        self.encoder = Encoder(encoder_channel=self.encoder_dims)

        self.use_cls_token = use_cls_token
        self.drop_path = drop_path
        self.rms_norm = rms_norm
        self.drop_out_in_block = drop_out_block

        if self.use_cls_token:
            self.cls_token = nn.Parameter(torch.zeros(1, 1, self.trans_dim))
            self.cls_pos = nn.Parameter(torch.randn(1, 1, self.trans_dim))
            trunc_normal_(self.cls_token, std=.02)
            trunc_normal_(self.cls_pos, std=.02)

        self.pos_embed = nn.Sequential(
            nn.Linear(3, 128),
            nn.GELU(),
            nn.Linear(128, self.trans_dim)
        ).to(device="cuda")

        self.blocks = MixerModel(d_model=self.trans_dim,
                                 n_layer=self.depth,
                                 rms_norm=self.rms_norm,
                                 drop_out_in_block=self.drop_out_in_block,
                                 drop_path=self.drop_path).to(device="cuda")
        
        self.norm = nn.LayerNorm(self.trans_dim).to(device="cuda")

        self.HEAD_CHANEL = 1
        if self.use_cls_token:
            self.HEAD_CHANEL += 1

        self.cls_head_finetune = nn.Sequential(
            nn.Linear(self.trans_dim * self.HEAD_CHANEL, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, self.cls_dim)
        ).to(device="cuda")

        self.build_loss_func()

        self.drop_out = nn.Dropout(drop_out)

    def build_loss_func(self):
        self.loss_ce = nn.CrossEntropyLoss()

    def get_loss_acc(self, ret, gt):
        loss = self.loss_ce(ret, gt.long())
        pred = ret.argmax(-1)
        acc = (pred == gt).sum() / float(gt.size(0))
        return loss, acc * 100
    
    def load_model_from_ckpt(self, bert_ckpt_path):
        if bert_ckpt_path is not None:
            ckpt = torch.load(bert_ckpt_path)
            base_ckpt = {k.replace("module.", ""): v for k, v in ckpt['base_model'].items()}

            for k in list(base_ckpt.keys()):
                if k.startswith('MAE_encoder'):
                    base_ckpt[k[len('MAE_encoder.'):]] = base_ckpt[k]
                    del base_ckpt[k]
                elif k.startswith('base_model'):
                    base_ckpt[k[len('base_model.'):]] = base_ckpt[k]
                    del base_ckpt[k]

            incompatible = self.load_state_dict(base_ckpt, strict=False)

            if incompatible.missing_keys:
                print(f'[Mamba] missing_keys: {incompatible.missing_keys}')

            if incompatible.unexpected_keys:
                print(f'[Mamba] unexpected_keys: {incompatible.unexpected_keys}')

            print(f'[Mamba] Successful Loading the ckpt from {bert_ckpt_path}')
        else:
            print('Training from scratch!!!')
            self.apply(self._init_weights)

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=.02)
            if isinstance(m, nn.Linear) and m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)
        elif isinstance(m, nn.Conv1d):
            trunc_normal_(m.weight, std=.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
                

    def forward(self, pts):
        # print(pts.shape)
        neighborhood, center = self.group_divider(pts)
        group_input_tokens = self.encoder(neighborhood)
        center = center.to(device="cuda")
        pos = self.pos_embed(center)

        center_x = center[:, :, 0].argsort(dim=-1)[:, :, None]
        center_y = center[:, :, 1].argsort(dim=-1)[:, :, None]
        center_z = center[:, :, 2].argsort(dim=-1)[:, :, None]
        group_input_tokens_x = group_input_tokens.gather(dim=1, index=torch.tile(center_x, (
            1, 1, group_input_tokens.shape[-1]
        )))
        group_input_tokens_y = group_input_tokens.gather(dim=1, index=torch.tile(center_y, (
            1, 1, group_input_tokens.shape[-1]
        )))
        group_input_tokens_z = group_input_tokens.gather(dim=1, index=torch.tile(center_z, (
            1, 1, group_input_tokens.shape[-1]
        )))
        pos_x = pos.gather(dim=1, index=torch.tile(center_x, (1, 1, pos.shape[-1])))
        pos_y = pos.gather(dim=1, index=torch.tile(center_y, (1, 1, pos.shape[-1])))
        pos_z = pos.gather(dim=1, index=torch.tile(center_z, (1, 1, pos.shape[-1])))
        group_input_tokens = torch.cat([group_input_tokens_x, group_input_tokens_y, group_input_tokens_z],
                                       dim=1)
        pos = torch.cat([pos_x, pos_y, pos_z], dim=1)

        x = group_input_tokens

        x = self.drop_out(x)
        x = self.blocks(x, pos)
        x = self.norm(x)
        # print(x.shape)
        concat_f = x[:, :].mean(1)
        ret = self.cls_head_finetune(concat_f)
        return ret