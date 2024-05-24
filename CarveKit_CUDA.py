from PIL import Image, ImageEnhance
import cv2
# from carvekit.api.interface import Interface
# from carvekit.ml.wrap.fba_matting import FBAMatting
# from carvekit.ml.wrap.tracer_b7 import TracerUniversalB7
# from carvekit.pipelines.postprocessing import MattingMethod
# from carvekit.pipelines.preprocessing import PreprocessingStub
# from carvekit.trimap.generator import TrimapGenerator

import torch
from carvekit.api.high import HiInterface




def enhance_contrast(input_image_path, method='pil', contrast_factor=1.12, clip_limit=2.0, tile_grid_size=(8, 8)):
    if method == 'pil':
        # Метод PIL для изменения контраста
        image = Image.open(input_image_path)
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(contrast_factor)
    elif method == 'opencv':
        # Метод OpenCV для изменения контраста
        image = cv2.imread(input_image_path)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        enhanced_image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        enhanced_image = Image.fromarray(cv2.cvtColor(enhanced_image, cv2.COLOR_BGR2RGB))

    return enhanced_image


def remove_background(file_path):
    # # Используем GPU для обработки
    # device = 'cuda'
    #
    # # Настройка компонентов с параметрами для максимального качества
    # seg_net = TracerUniversalB7(device=device, batch_size=1, fp16=False)  # Точная сегментация
    # fba = FBAMatting(device=device, input_tensor_size=3072, batch_size=1, fp16=False)  # Высокое разрешение
    # trimap = TrimapGenerator(prob_threshold=240, kernel_size=55, erosion_iters=30)  # Настройки тримапа
    #
    #
    # preprocessing = PreprocessingStub()
    #
    # postprocessing = MattingMethod(matting_module=fba, trimap_generator=trimap, device=device)
    #
    # interface = Interface(pre_pipe=preprocessing, post_pipe=postprocessing, seg_pipe=seg_net)
    #
    #
    # image = enhance_contrast(file_path)
    # img_wo_bg = interface([image])[0]
    #
    # return img_wo_bg
    #Нужно вручную включать тот или иной способ обработки, верхний способ пока что не настроен
    interface = HiInterface(object_type="object",  # Can be "object" or "hairs-like".
                            batch_size_seg=1,
                            batch_size_matting=1,
                            device='cuda',
                            seg_mask_size=640,
                            matting_mask_size=2048,
                            trimap_prob_threshold=235,
                            trimap_dilation=30,
                            trimap_erosion_iters=30,
                            fp16=False)

    image_enhanced = enhance_contrast(file_path)
    image_wo_BG = interface([image_enhanced])
    img_wo_bg = image_wo_BG[0]
    return img_wo_bg