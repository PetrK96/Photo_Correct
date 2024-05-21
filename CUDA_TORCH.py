import torch
from carvekit.api.high import HiInterface

# Check doc strings for more information
interface = HiInterface(object_type="object",  # Can be "object" or "hairs-like".
                        batch_size_seg=4000,
                        batch_size_matting=1,
                        device='cuda',
                        seg_mask_size=320,  # Use 640 for Tracer B7 and 320 for U2Net
                        matting_mask_size=3072,
                        trimap_prob_threshold=253,
                        trimap_dilation=30,
                        trimap_erosion_iters=250,
                        fp16=False)

image = interface(['201-2102-2454.JPG'])
img_wo_bg = image[0]
img_wo_bg.save('CUDA2.png')