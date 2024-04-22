import os
from rembg import remove
from PIL import Image, ImageEnhance
import pandas as pd

class ImageProcessor:
    def __init__(self, input_path, output_path, excel_file):
        self.input_path = input_path
        self.output_path = output_path
        self.excel_file = excel_file
        self.desired_size = (1200, 1200)
        self.MAX_SIZE = 1100

    def process_image(self):
        data = []
        for pict in os.listdir(self.input_path):
            if pict.endswith('.jpeg') or pict.endswith('.JPG') or pict.endswith('.CR2'):
                print(f'[+] Обрабатываю изображение: "{pict}"...')
                # Открытие изображения
                image = Image.open(os.path.join(self.input_path, pict))

                # Удаление фона
                output = remove(image)

                # Создание белого фона с альфа-каналом
                white_bg = Image.new("RGBA", self.desired_size, (255, 255, 255, 255))

                # Вырезание изображения с фона
                bbox = output.getbbox()
                output = output.crop(bbox)

                enhancer = ImageEnhance.Sharpness(output)
                output = enhancer.enhance(1.8)

                width, height = output.size
                max_dimension = max(width, height)
                if max_dimension > self.MAX_SIZE:
                    scale = self.MAX_SIZE / max_dimension
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    output = output.resize((new_width, new_height), Image.LANCZOS)

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
                print(filename_without_extension)
                path_for_excel = output_filepath.replace("/", "\\")  # Замена символов "/" на "\"
                path_for_excel = path_for_excel.split("\\srvfsz\\")[1]  # Удаление части пути до папки "srvfsz" и пробелов
                data.append([filename_without_extension, f'Z:\\{path_for_excel}'])

        if os.path.exists(self.excel_file):
            df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
            df.to_excel(self.excel_file, index=False)
        else:
            with pd.ExcelWriter(self.excel_file, engine='xlsxwriter') as writer:
                df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
                df.to_excel(writer, index=False)

    def get_target_path(self):
        while not os.path.isdir(self.input_path):
            print(f'Папка "{self.input_path}" не найдена\n')
        print(f"\nРаботаем с папкой {self.input_path}\n")
        return self.input_path

    def start_processing(self):
        print("Стартуем")
        self.process_image()
        print('\n[+] Обработка изображений завершена и данные записаны в файл Excel!')


user_input = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C"
user_output = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные'
excel_file = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные/Таблица для загрузки фото в 1С.xlsx"

processor = ImageProcessor(user_input, user_output, excel_file)
processor.start_processing()
