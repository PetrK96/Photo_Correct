import torch
from carvekit.api.high import HiInterface

# Check doc strings for more information
def remove_bg(file_path):
    interface = HiInterface(object_type="object",  # Can be "object" or "hairs-like".
                            batch_size_seg=1,
                            batch_size_matting=1,
                            device='cuda' if torch.cuda.is_available() else 'cpu',
                            seg_mask_size=640,
                            matting_mask_size=2048,
                            trimap_prob_threshold=231,
                            trimap_dilation=30,
                            trimap_erosion_iters=7,
                            fp16=False)
    images_without_background = interface([file_path])
    img_wo_bg = images_without_background[0]
    return img_wo_bg