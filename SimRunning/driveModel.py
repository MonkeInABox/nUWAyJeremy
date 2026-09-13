"""
Driving model
"""

import numpy as np
import torch
from torch import nn

from pytorch3d.ops import sample_farthest_points

from model import PointCAMBackbone


def fps_downsample(points, n_fps, n_sample):
    _, fps_idx = sample_farthest_points(
        points[..., :3], K=n_fps, random_start_point=True
    )
    fps_idx = fps_idx[:, np.random.choice(n_fps, n_sample, replace=False)]
    return torch.gather(points, 1, fps_idx.unsqueeze(-1).expand(-1, -1, points.shape[-1]))


class drivePointCAM(nn.Module):
    def __init__(
            self,
            *,
            checkpoint_path=None,
            n_patches=64,
            points_per_patch=32,
            freeze_encoder=False,
            drop_path_rate=None,
    ):
        super().__init__()

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.vision_model = PointCAMBackbone(
                checkpoint_path=checkpoint_path,
                n_patches=n_patches,
                points_per_patch=points_per_patch,
                freeze_encoder=freeze_encoder,
                drop_path_rate=drop_path_rate,
        )


        cls_dim = PointCAMBackbone.FEATURE_DIM

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

    def forward(self, front_cloud, rear_cloud):
        full_lidar = torch.concat([front_cloud, rear_cloud], axis=1).float()
        x = self.vision_model(full_lidar)
        b, n = x.shape

        speed = self.mlp_head1(x)
        angle = self.mlp_head2(x)
        return speed[:, 0], angle[:, 0]
