import torch
import torch.nn as nn
 
from omegaconf import OmegaConf
 
from pointcam.models import PointCAM
from pointcam.configs import PointCAMConfig
from pointcam.utils.crop import PatchFinder
 
 
class PointCAMBackbone(nn.Module):
 
    FEATURE_DIM = 768  # 2 * encoder.embedding_dim (384 cls + 384 pooled patch feats)
 
    def __init__(
        self,
        checkpoint_path: str = None,
        n_patches: int = 64,
        points_per_patch: int = 32,
        freeze_encoder: bool = False,
        drop_path_rate: float = None,
        cfg=None,
    ):
        super().__init__()
 
        if checkpoint_path is not None:
            print(f'PointCAM Loading pretrained checkpoint from {checkpoint_path}')
            self.pointcam = PointCAM.from_exported_checkpoint(
                checkpoint_path, drop_path_rate=drop_path_rate
            )
        else:
            print('PointCAM No checkpoint given')
            self.pointcam = PointCAM(
                cfg=cfg if cfg is not None else OmegaConf.structured(PointCAMConfig)
            )
 
        self.pointcam = self.pointcam.to(device="cuda")
 
        self.freeze_encoder = freeze_encoder
        if self.freeze_encoder:
            self.pointcam.eval()
            for p in self.pointcam.parameters():
                p.requires_grad = False
 

        self.patch_finder = PatchFinder(n_patches, points_per_patch)
 
    def train(self, mode: bool = True):
        super().train(mode)
        if self.freeze_encoder:
            self.pointcam.eval()
        return self
 
    def forward(self, pts):
        xyz = self.patch_finder(pts.contiguous())
        xyz = xyz.to(pts.device)
 
        if self.freeze_encoder:
            with torch.no_grad():
                features = self.pointcam(xyz)
        else:
            features = self.pointcam(xyz)
 
        return features  # (B, 768)
