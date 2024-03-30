import os
import rawpy
from rembg import remove
from PIL import Image, ImageEnhance, ImageFile

# Установка максимального размера файла изображения для обработки
ImageFile.MAX_IMAGE_PIXELS = None

desired_size = (500, 500)
USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'

def remove_background_and_process(input_path, output_path):
    for filename in os.listdir(input_path):
        if filename.lower().endswith('.cr2'):
            print(f'[+] Обработка RAW-файла: "{filename}"...')
            # Обработка RAW-файла
            with rawpy.imread(os.path.join(input_path, filename)) as raw:
                rgb = raw.postprocess()
                raw_img = Image.fromarray(rgb)
                # Удаление фона
                output = remove(raw_img)
        elif filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            print(f'[+] Обработка JPEG/PNG-файла: "{filename}"...')
            # Обработка JPEG/PNG-файла
            output = Image.open(os.path.join(input_path, filename))
            # Удаление фона
            output = remove(output)
        else:
            print(f'[!] Неподдерживаемый формат файла: "{filename}"')
            continue

        # Увеличение контрастности
        enhancer = ImageEnhance.Contrast(output)
        output = enhancer.enhance(1.2)  # Увеличиваем контрастность в 1.2 раза

        # Увеличение резкости
        enhancer = ImageEnhance.Sharpness(output)
        output = enhancer.enhance(1.5)  # Увеличиваем резкость в 1.5 раза

        # Увеличение разрешения
        output = output.resize(desired_size, Image.LANCZOS)

        # Создание белого фона
        white_bg = Image.new("RGB", desired_size, (255, 255, 255))

        # Расчет размеров для размещения изображения по центру
        image_width, image_height = output.size
        min_dimension = min(image_width, image_height)
        target_dimension = int(min_dimension / 0.6)  # 60% от минимальной стороны
        target_size = (target_dimension, target_dimension)

        # Расчет координат для размещения изображения по центру белого фона
        x_offset = (desired_size[0] - target_size[0]) // 2
        y_offset = (desired_size[1] - target_size[1]) // 2

        # Изменение размера изображения с сохранением пропорций
        output.thumbnail(target_size)

        # Вставка изображения на белый фон
        white_bg.paste(output, (x_offset, y_offset))

        # Сохранение результата
        white_bg.save(os.path.join(output_path, f'{os.path.splitext(filename)[0]}.jpg'), 'JPEG')
        print(f'[+] Обработка для "{filename}" завершена!')

def get_input_path(user_input):
    while not os.path.isdir(user_input):
        print(f'Папка "{user_input}" не найдена\n')
    print(f"\nРаботаем с папкой {user_input}\n")
    return user_input

def main(user_input, user_output):
    print("Погнали")
    remove_background_and_process(get_input_path(user_input), user_output)
    print('\n[+] Обработка изображений завершена!')

main(USER_INPUT, USER_OUTPUT)
