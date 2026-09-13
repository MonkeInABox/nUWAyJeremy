"""
The shuttle bus driving model (PointMamba backbone + speed/steering heads).
 
Mirrors driveModel.py (the PointCAM version) so the two can be swept and
compared with the same methodology. Pulled into its own module for the same
reason as the PointCAM version: keeps training-only side effects out of
anything that just wants to import the model.
 
Depends on modelMamba.py (your original PointMamba model, copied verbatim),
which in turn needs block.py and misc.py sitting alongside it -- those
aren't something I generated, they're your original PointMamba dependencies
and need to already exist in this directory.
"""
 
import torch
from torch import nn
 
from modelMamba import PointMamba
 
 
class drivePointMamba(nn.Module):
    def __init__(
            self,
            *,
            trans_dim=512,
            depth=12,
            cls_dim=1000,
            group_size=32,
            num_group=64,
            encoder_dims=512,
            rms_norm=False,
            drop_path=0.1,
            drop_out=0.1,
            drop_out_block=0.1,
            use_cls_token=False,
            freeze_encoder=False,
    ):
        super().__init__()
 
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
 
        self.vision_model = PointMamba(
                 trans_dim=trans_dim,
                 depth=depth,
                 cls_dim=cls_dim,
                 group_size=group_size,
                 num_group=num_group,
                 encoder_dims=encoder_dims,
                 rms_norm=rms_norm,
                 drop_path=drop_path,
                 drop_out=drop_out,
                 drop_out_block=drop_out_block,
                 use_cls_token=use_cls_token,
        )
 
        # Not present in the original script -- added so freeze_encoder can
        # be swept the same way it is for the PointCAM version, as a direct
        # comparison point (does freezing cost/save the same thing on both
        # architectures?).
        self.freeze_encoder = freeze_encoder
        if self.freeze_encoder:
            self.vision_model.eval()
            for p in self.vision_model.parameters():
                p.requires_grad = False
 
        self.mlp_head1 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim / 2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4),  int(cls_dim / 8)),
                nn.LayerNorm(int(cls_dim / 8)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 8), 1)).to(device=self.device)
 
        self.mlp_head2 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim / 2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4),  int(cls_dim / 8)),
                nn.LayerNorm(int(cls_dim / 8)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 8), 1)).to(device=self.device)
 
    def train(self, mode: bool = True):
        super().train(mode)
        if self.freeze_encoder:
            self.vision_model.eval()
        return self
 
    def forward(self, front_cloud, rear_cloud):
        full_lidar = torch.concat([front_cloud, rear_cloud], axis=1).float()
 
        if self.freeze_encoder:
            with torch.no_grad():
                x = self.vision_model(full_lidar)
        else:
            x = self.vision_model(full_lidar)
 
        b, n = x.shape
 
        speed = self.mlp_head1(x)
        angle = self.mlp_head2(x)
        return speed[:, 0], angle[:, 0]
