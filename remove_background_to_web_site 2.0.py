import os
import shutil
from rembg import remove  # Импортируем функцию для удаления фона
from PIL import Image, ImageEnhance, ImageFilter  # Импортируем модуль для работы с изображениями
import openpyxl # Импортируем модуль для работы с Excel-файлами

class ImageProcessor:
    def __init__(self, input_path, output_path, excel_file, processed_images_path, original_images_path):
        # Инициализация путей к папкам и файлам, а также размеров изображений
        self.input_path = input_path  # Папка с исходными изображениями
        self.output_path = output_path  # Папка для сохранения обработанных изображений
        self.excel_file = excel_file  # Путь к Excel-файлу с данными
        self.processed_images_path = processed_images_path  # Папка для сохранения изображений без фона
        self.original_images_path = original_images_path  # Папка для сохранения исходных изображений
        self.desired_size = (500, 500)  # Размеры изображений
        self.MAX_SIZE = 450 # Максимальный размер изображения
        self.mapping = self.load_mapping()  # Загрузка соответствия имён файлов из Excel

    def load_mapping(self):
        # Загрузка соответствия имён файлов из Excel
        mapping = {}
        wb = openpyxl.load_workbook(self.excel_file)
        sheet = wb.active
        for row in sheet.iter_rows(min_row=2, values_only=True):
            filename, _ = os.path.splitext(row[1])  # Получаем имя файла из Excel
            mapping[filename] = row[0]  # Записываем соответствие в словарь
        return mapping

    def process_images(self):
        # Обработка изображений
        print("\nНачинаю обработку изображений...\n")
        #print("Словарь имен файлов из Excel:")
        #for old_filename, new_filename in self.mapping.items():
        #   print(f"{old_filename} -> {new_filename}")

        total_images = 0  # Общее количество изображений
        processed_images = 0  # Количество обработанных изображений
        for pict in os.listdir(self.input_path):
            file_path = os.path.join(self.input_path, pict)
            if os.path.isfile(file_path) and self.is_image(file_path):
                total_images += 1
                filename, ext = os.path.splitext(pict)
                filename = filename  # Убираем последние три символа (расширение и еще один символ)
                new_filename = self.mapping.get(filename, None)  # Получаем новое имя из словаря

                if new_filename is not None:
                    print(f"Проверка файла: {filename}, новое имя: {new_filename}")

                try:
                    self.process_image(file_path, new_filename)
                    processed_images += 1
                except Exception as e:
                    print(f'Ошибка при обработке изображения {file_path}: {e}')

        print(f'Обработано изображений: {processed_images} из {total_images}')

    def is_image(self, file_path):
        # Проверка, является ли файл изображением по расширению
        image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.bmp')
        return file_path.lower().endswith(image_extensions)

    def process_image(self, file_path, new_filename):
        # Обработка отдельного изображения
        # Копирование исходного файла в папку с исходными изображениями
        shutil.copy2(file_path, self.original_images_path)

        # Открытие изображения
        image = Image.open(file_path)

        # Удаление фона
        output = remove(image)

        enhancer = ImageEnhance.Sharpness(output)
        output = enhancer.enhance(4)

        enhancer = ImageEnhance.Color(output)
        output = enhancer.enhance(1.3)


        # Сохранение изображения без фона в формате RGBA
        if new_filename is not None:
            processed_image_path = os.path.join(self.processed_images_path, f'{new_filename}.png')
            output.save(processed_image_path, 'PNG')
        else:
            # Если новое имя не найдено в словаре, сохраняем изображение с текущим именем
            new_filename = os.path.splitext(os.path.basename(file_path))[0]
            output.save(os.path.join(self.processed_images_path, f'{new_filename}.png'), 'PNG')
        #processed_image_path = os.path.join(self.processed_images_path, f'{new_filename}.png')
        #output.save(processed_image_path, 'PNG')

        # Анализ размера и занятой площади изображения
        width, height, occupancy = self.analyze_image(output)

        # Если изображение занимает мало места, увеличиваем его
        if occupancy < 0.5:
            output = self.enlarge_image(output)

        # Получаем bbox и обрезаем изображение до него
        bbox = output.getbbox()
        output = output.crop(bbox)

        # Уменьшение изображения
        output = self.resize_image(output)

        # Вставка изображения на белый фон
        output = self.insert_on_white_background(output)

        # Конвертация изображения без фона в формат RGB
        output = output.convert("RGB")

        if new_filename is not None:
            # Сохранение переименованного изображения в формате JPEG
            output.save(os.path.join(self.output_path, f'{new_filename}.jpg'), 'JPEG')
        else:
            # Если новое имя не найдено в словаре, сохраняем изображение с текущим именем
            new_filename = os.path.splitext(os.path.basename(file_path))[0]
            output.save(os.path.join(self.output_path, f'{new_filename}.jpg'), 'JPEG')

        print(f'[+] Обработан и сохранен файл: {file_path}\n')

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

    def resize_image(self, image):
        # Изменение размера изображения
        width, height = image.size
        max_dimension = max(width, height)
        if max_dimension > self.MAX_SIZE:
            scale = self.MAX_SIZE / max_dimension
            new_width = int(width * scale)
            new_height = int(height * scale)
            return image.resize((new_width, new_height), Image.LANCZOS)
        else:
            return image

    def enlarge_image(self, image):
        # Увеличение изображения
        width, height = image.size
        new_size = (int(width * 1.5), int(height * 1.5))  # Увеличиваем размер на 50%
        return image.resize(new_size, Image.LANCZOS)

    def insert_on_white_background(self, image):
        # Создание белого фона с альфа-каналом в формате RGBA
        white_bg = Image.new("RGBA", self.desired_size, (255, 255, 255, 255))

        # Уменьшение изображения
        image_resized = image

        # Получаем bbox и обрезаем изображение до него
        bbox = image_resized.getbbox()
        image_resized = image_resized.crop(bbox)

        # Вычисляем новые координаты для центрирования обрезанного изображения
        x_offset = (self.desired_size[0] - image_resized.size[0]) // 2
        y_offset = (self.desired_size[1] - image_resized.size[1]) // 2

        # Вставка обрезанного изображения на белый фон
        white_bg.paste(image_resized, (x_offset, y_offset), image_resized)

        return white_bg

def main():
    # Основная функция программы
    input_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"  # Папка с исходными изображениями
    output_path = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'  # Папка для сохранения обработанных изображений
    excel_file = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Список запчастей для ренейма.xlsx'  # Путь к Excel-файлу с данными
    processed_images_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти без фона"  # Папка для сохранения изображений без фона
    original_images_path = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти исходные"  # Папка для сохранения исходных изображений

    processor = ImageProcessor(input_path, output_path, excel_file, processed_images_path, original_images_path)
    processor.process_images()

if __name__ == "__main__":
    main()