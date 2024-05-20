import torch
from carvekit.api.high import HiInterface
import os
from rembg import remove
from PIL import Image, ImageEnhance
import pandas as pd
from tqdm import tqdm

class Spare_part_picture():
    def __init__(self, file, output_path, processed_images_path, original_images_path, excel_file):
        # Инициализация путей к папкам и файлам, а также размеров изображений
        self.file = file  #Ссылка на обрабатываемое изображение
        self.output_path = output_path  # Папка для сохранения обработанных изображений
        self.excel_file = excel_file  # Путь к Excel-файлу с данными
        self.processed_images_path = processed_images_path  # Папка для сохранения изображений без фона
        self.original_images_path = original_images_path  # Папка для сохранения исходных изображений
        self.desired_size = (500, 500)  # Размеры изображений
        self._MAX_SIZE_MASK = 400  # Максимальный размер изображения
        self.mapping = self.load_mapping()  # Загрузка соответствия имён файлов из Excel

    def remove_backround(input_file_path):
        interface = HiInterface(object_type="object",  # Can be "object" or "hairs-like".
                                batch_size_seg=5,
                                batch_size_matting=1,
                                device='cuda' if torch.cuda.is_available() else 'cpu',
                                seg_mask_size=640,
                                matting_mask_size=2048,
                                trimap_prob_threshold=231,
                                trimap_dilation=30,
                                trimap_erosion_iters=5,
                                fp16=False)
        images_without_background = interface([input_file_path])
        image_without_background_png = images_without_background[0]

        return image_without_background_png

    def create_white_background(self):
        white_bg = Image.new("RGBA", self.desired_size, (255, 255, 255, 255))
