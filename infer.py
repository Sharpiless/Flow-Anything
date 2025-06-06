import sys

sys.path.append("core")
import argparse
import os
import cv2
import math
import numpy as np
from tqdm import tqdm
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data

from config.parser import parse_args

import datasets
from raft import RAFT
from utils.flow_viz import flow_to_image
from utils.utils import load_ckpt


def create_color_bar(height, width, color_map):
    """
    Create a color bar image using a specified color map.

    :param height: The height of the color bar.
    :param width: The width of the color bar.
    :param color_map: The OpenCV colormap to use.
    :return: A color bar image.
    """
    # Generate a linear gradient
    gradient = np.linspace(0, 255, width, dtype=np.uint8)
    gradient = np.repeat(gradient[np.newaxis, :], height, axis=0)

    # Apply the colormap
    color_bar = cv2.applyColorMap(gradient, color_map)

    return color_bar


def add_color_bar_to_image(image, color_bar, orientation="vertical"):
    """
    Add a color bar to an image.

    :param image: The original image.
    :param color_bar: The color bar to add.
    :param orientation: 'vertical' or 'horizontal'.
    :return: Combined image with the color bar.
    """
    if orientation == "vertical":
        return cv2.vconcat([image, color_bar])
    else:
        return cv2.hconcat([image, color_bar])


def vis_heatmap(name, image, heatmap):
    # theta = 0.01
    # print(heatmap.max(), heatmap.min(), heatmap.mean())
    heatmap = heatmap[:, :, 0]
    heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())
    # heatmap = heatmap > 0.01
    heatmap = (heatmap * 255).astype(np.uint8)
    colored_heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    overlay = image * 0.3 + colored_heatmap * 0.7
    # Create a color bar
    height, width = image.shape[:2]
    color_bar = create_color_bar(
        50, width, cv2.COLORMAP_JET
    )  # Adjust the height and colormap as needed
    # Add the color bar to the image
    overlay = overlay.astype(np.uint8)
    combined_image = add_color_bar_to_image(overlay, color_bar, "vertical")
    cv2.imwrite(name, cv2.cvtColor(combined_image, cv2.COLOR_RGB2BGR))


def get_heatmap(info, args):
    raw_b = info[:, 2:]
    log_b = torch.zeros_like(raw_b)
    weight = info[:, :2].softmax(dim=1)
    log_b[:, 0] = torch.clamp(raw_b[:, 0], min=0, max=args.var_max)
    log_b[:, 1] = torch.clamp(raw_b[:, 1], min=args.var_min, max=0)
    heatmap = (log_b * weight).sum(dim=1, keepdim=True)
    return heatmap


def forward_flow(args, model, image1, image2):
    output = model(image1, image2, iters=args.iters, test_mode=True)
    flow_final = output["flow"][-1]
    info_final = output["info"][-1]
    return flow_final, info_final


def calc_flow(args, model, image1, image2):
    img1 = F.interpolate(
        image1, scale_factor=2**args.scale, mode="bilinear", align_corners=False
    )
    img2 = F.interpolate(
        image2, scale_factor=2**args.scale, mode="bilinear", align_corners=False
    )
    H, W = img1.shape[2:]
    flow, info = forward_flow(args, model, img1, img2)
    flow_down = F.interpolate(
        flow, scale_factor=0.5**args.scale, mode="bilinear", align_corners=False
    ) * (0.5**args.scale)
    info_down = F.interpolate(info, scale_factor=0.5**args.scale, mode="area")
    return flow_down, info_down


@torch.no_grad()
def demo_custom(model, args, device=torch.device("cuda")):
        base = args.input
        out = args.out
        if not os.path.exists(out):
            os.makedirs(out, exist_ok=True)
            
        images_list = sorted(os.listdir(base))
        for i in tqdm(range(len(images_list)-1)):
            image1 = cv2.imread(os.path.join(base, images_list[i]))
            H, W = image1.shape[:2]

            image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
            image2 = cv2.imread(os.path.join(base, images_list[i+1]))

            image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
            timage1 = torch.tensor(image1, dtype=torch.float32).permute(2, 0, 1)
            timage2 = torch.tensor(image2, dtype=torch.float32).permute(2, 0, 1)

            timage1 = timage1[None].to(device)
            timage2 = timage2[None].to(device)

            flow, info = calc_flow(args, model, timage1, timage2)
            flo = flow_to_image(
                flow[0].permute(1, 2, 0).cpu().numpy(), convert_to_bgr=False
            )
            cv2.imwrite(os.path.join(out, images_list[i]), np.vstack([image1[:, :, ::-1], flo]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cfg",
        help="experiment configure file name",
        default="config/eval/spring-M.json",
        type=str,
    )
    parser.add_argument(
        "--model",
        help="checkpoint path",
        default="Tartan-C-T-TSKH-spring540x960-M.pth",
        type=str,
    )
    parser.add_argument(
        "--out",
        help="output path",
        required=True,
        type=str,
    )
    parser.add_argument(
        "--input",
        help="output path",
        required=True,
        type=str,
    )
    args = parse_args(parser)
    model = RAFT(args)
    load_ckpt(model, args.model)
    model = model.cuda()
    model.eval()

    demo_custom(model, args)

if __name__ == "__main__":
    main()
