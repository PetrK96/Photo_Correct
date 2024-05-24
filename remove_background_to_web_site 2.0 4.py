import os
import shutil
from PIL import Image, ImageEnhance
import openpyxl  # Импортируем модуль для работы с Excel-файлами
from tqdm import tqdm
from CarveKit_CUDA import remove_background
from CarveKit_CPU import remove_bg
import platform

def get_os():
    system = platform.system()
    if system == "Darwin":
        device = "CPU"
        input_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
        output_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные"
        excel_file = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Список запчастей для ренейма.xlsx"
        processed_images_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти без фона"
        original_images_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти исходные"
    else:
        device = "CUDA"
        input_path = r"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото запчасти"  # Папка с исходными изображениями
        output_path = r"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото обработанные"  # Папка для сохранения обработанных изображений
        excel_file = r"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото обработанные\Список запчастей для ренейма.xlsx"   # Путь к Excel-файлу с данными
        processed_images_path = r"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото обработанные\Фото запчасти без фона"  # Папка для сохранения изображений без фона
        original_images_path = r"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото обработанные\Фото запчасти исходные"  # Папка для сохранения исходных изображений

    return input_path, output_path, excel_file, processed_images_path, original_images_path, device


class ImageProcessor:
    def __init__(self, input_path, output_path, excel_file, processed_images_path, original_images_path, device):
        self.input_path = input_path
        self.output_path = output_path
        self.excel_file = excel_file
        self.processed_images_path = processed_images_path
        self.original_images_path = original_images_path
        self.desired_size = (500, 500)
        self._MAX_SIZE_MASK = 400
        self.mapping = self.load_mapping()
        self.device = device

    def load_mapping(self):
        mapping = {}
        wb = openpyxl.load_workbook(self.excel_file)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            filename_without_ext = row[1]  # Извлекаем имя файла без расширения
            mapping[filename_without_ext] = row[0]
        return mapping

    def download_image(self, filename):
        src = os.path.join(self.input_path, filename)
        dest = os.path.join(self.original_images_path, filename)
        shutil.copy2(src, dest)

    def is_exist(self, file_name, list):
        return file_name not in list




    def process_images(self):
        existed_imgs = os.listdir(original_images_path)
        total_images = len([file_name for file_name in os.listdir(self.input_path) if (self.is_image_exist(file_name, list=existed_imgs))])
        processed_images = 0
        with tqdm(total=total_images, desc="Прогресс обработки изображений") as pbar:
            for file in os.listdir(self.input_path):
                if self.is_image(file):
                    if file not in existed_imgs:
                        filename_without_ext, ext = os.path.splitext(file)
                        if filename_without_ext in self.mapping:
                            new_filename = str(self.mapping[filename_without_ext])
                            self.download_image(file)
                            self.process_image(os.path.join(self.original_images_path, file), new_filename)
                            processed_images += 1
                            pbar.update(1)
                        else:
                            self.download_image(file)
                            self.process_image(os.path.join(self.original_images_path, file), filename_without_ext)
                            processed_images += 1
                            pbar.update(1)
        print("\nОбработка завершена.")

    def process_image(self, file_path, new_filename):
        image = Image.open(file_path)
        if self.device == "CPU":
            output = remove_bg(file_path)
        else:
            output = remove_background(file_path)
        width, height, occupancy = self.analyze_image(output)
        if occupancy < 0.05:
            self.set_max_size(300)
        else:
            self.set_max_size(450)
        enhancer = ImageEnhance.Sharpness(output)
        output = enhancer.enhance(2)
        enhancer = ImageEnhance.Color(output)
        output = enhancer.enhance(2)
        processed_image_path = os.path.join(self.processed_images_path, f'{new_filename}.png')
        output.save(processed_image_path, 'PNG')
        bbox = output.getbbox()
        output = output.crop(bbox)
        output = self.resize_image(output)
        output = self.insert_on_white_background(output)
        output = output.convert("RGB")
        output.save(os.path.join(self.output_path, f'{new_filename}.jpg'), 'JPEG')

    def set_max_size(self, number):
        self._MAX_SIZE_MASK = number

    def get_max_size(self):
        return self._MAX_SIZE_MASK

    def resize_image(self, image):
        width, height = image.size
        max_dimension = max(width, height)
        if max_dimension > self.get_max_size():
            scale = self.get_max_size() / max_dimension
            new_width = int(width * scale)
            new_height = int(height * scale)
            return image.resize((new_width, new_height), Image.LANCZOS)
        else:
            return image

    def is_image_exist(self, file_path, list):
        # Проверка, является ли файл изображением по расширению
        image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.bmp')
        return file_path not in list and file_path.lower().endswith(image_extensions)

    def is_image(self, file_path):
        image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.bmp')
        return file_path.lower().endswith(image_extensions)




    def analyze_image(self, image):
        width, height = image.size
        area = width * height
        non_transparent_pixels = 0
        for pixel in image.getdata():
            if pixel[3] != 0:
                non_transparent_pixels += 1
        occupancy = non_transparent_pixels / area
        return width, height, occupancy

    def insert_on_white_background(self, image):
        white_bg = Image.new("RGBA", self.desired_size, (255, 255, 255, 255))
        image_resized = image
        bbox = image_resized.getbbox()
        image_resized = image_resized.crop(bbox)
        x_offset = (self.desired_size[0] - image_resized.size[0]) // 2
        y_offset = (self.desired_size[1] - image_resized.size[1]) // 2
        white_bg.paste(image_resized, (x_offset, y_offset), image_resized)
        return white_bg

input_path, output_path, excel_file, processed_images_path, original_images_path, device = get_os()

processor = ImageProcessor(input_path, output_path, excel_file, processed_images_path, original_images_path, device="CUDA")
processor.process_images()
