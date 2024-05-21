import os
from rembg import remove
from PIL import Image, ImageEnhance
import pandas as pd
from tqdm import tqdm

class ImageProcessor:
    def __init__(self, input_path, output_path, excel_file):
        self.input_path = input_path
        self.output_path = output_path
        self.excel_file = excel_file
        self.desired_size = (1200, 1200)
        self.MAX_SIZE = 1100

    def is_image(self, file_path):
        # Проверка, является ли файл изображением по расширению
        image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.bmp')
        return file_path.lower().endswith(image_extensions)

    def process_image(self):
        data = []
        total_images = sum(
            1 for file in os.listdir(self.input_path) if self.is_image(os.path.join(self.input_path, file)))
        processed_images = 0  # Количество обработанных изображений
        with tqdm(total=total_images, desc="Прогресс обработки изображений") as pbar:
            for pict in os.listdir(self.input_path):
                if pict.endswith('.jpeg') or pict.endswith('.JPG') or pict.endswith('.CR2'):
                    #print(f'[+] Обрабатываю изображение: "{pict}"...')
                    # Открытие изображения
                    image = Image.open(os.path.join(self.input_path, pict))

                    # Удаление фона
                    output = remove(image)

                    bbox = output.getbbox()
                    output = output.crop(bbox)

                    width, height, occupancy = self.analyze_image(output)
                    # print("Заполенение = {}".format(occupancy))# Анализ размера и занятой площади изображения

                    # Если изображение занимает мало места, увеличиваем его
                    if occupancy < 0.5:
                        self.set_max_sixe(1000)
                    else:
                        self.set_max_sixe(1000)

                    output = self.resize_image(output)

                    enhancer = ImageEnhance.Sharpness(output)
                    output = enhancer.enhance(10)

                    enhancer = ImageEnhance.Color(output)
                    output = enhancer.enhance(2)

                    # Создание белого фона с альфа-каналом
                    white_bg = Image.new("RGBA", self.desired_size, (255, 255, 255, 255))

                    # Вырезание изображения с фона
                    bbox = output.getbbox()
                    output = output.crop(bbox)

                    output = self.resize_image(output)

                    enhancer = ImageEnhance.Sharpness(output)
                    output = enhancer.enhance(1.8)

                    x_offset = (self.desired_size[0] - output.size[0]) // 2
                    y_offset = (self.desired_size[1] - output.size[1]) // 2
                    white_bg.paste(output, (x_offset, y_offset), output)

                    # Конвертация изображения в формат RGB
                    white_bg = white_bg.convert("RGB")

                    # Сохранение результата в формате JPEG
                    output_filename = f'{pict.split(".j")[0]}.jpg'
                    output_filepath = os.path.join(self.output_path, output_filename)
                    white_bg.save(output_filepath, 'JPEG')

                    # Добавление информации об обработанном изображении в Excel
                    filename_without_extension = pict[:-8]
                    #print(filename_without_extension)
                    path_for_excel = output_filepath.replace("/", "\\")  # Замена символов "/" на "\"
                    path_for_excel = path_for_excel.split("\\srvfsz\\")[1]  # Удаление части пути до папки "srvfsz" и пробелов
                    data.append([filename_without_extension, f'Z:\\{path_for_excel}'])

                    processed_images += 1
                    pbar.update(1)

            if os.path.exists(self.excel_file):
                df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
                df.to_excel(self.excel_file, index=False)
            else:
                with pd.ExcelWriter(self.excel_file, engine='xlsxwriter') as writer:
                    df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
                    df.to_excel(writer, index=False)

    def resize_image(self, image):
        # Изменение размера изображения
        width, height = image.size
        max_dimension = max(width, height)
        if max_dimension != self.get_max_size():
            scale = self.get_max_size() / max_dimension
            new_width = int(width * scale)
            new_height = int(height * scale)
            return image.resize((new_width, new_height), Image.LANCZOS)
        else:
            return image

    def analyze_image(self, image):
        # Анализ размера и занятой площади изображения
        width, height = image.size
        area = width * height
        non_transparent_pixels = 0
        for pixel in image.getdata():
            if pixel[3] != 0:  # Проверка непрозрачности
                non_transparent_pixels += 1
        occupancy = non_transparent_pixels / area
        return width, height, occupancy

    def set_max_sixe(self, number):
        self._MAX_SIZE_MASK = number

    def get_max_size(self):
        return self._MAX_SIZE_MASK

    def get_target_path(self):
        while not os.path.isdir(self.input_path):
            #print(f'Папка "{self.input_path}" не найдена\n')
        #print(f"\nРаботаем с папкой {self.input_path}\n")
            return self.input_path

    def start_processing(self):
        print("Стартуем")
        self.process_image()
        print('\n[+] Обработка изображений завершена и данные записаны в файл Excel!')


user_input = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C"
user_output = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные'
excel_file = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные/Таблица для загрузки фото в 1C.xlsx"

processor = ImageProcessor(user_input, user_output, excel_file)
processor.start_processing()
