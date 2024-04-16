import os
from rembg import remove
from PIL import Image, ImageEnhance

desired_size = (500, 500)
MAX_SIZE = 450
USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'
PATH_WITHOUT_BACKROUND = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти без фона'
PATH_TO_1C = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные/Фото запчасти для 1С'
PATH_FROM_1C = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Фото запчасти для 1С Исходные'
def process_image(input_path, output_path):
    for pict in os.listdir(input_path):
        if pict.endswith('.png') or pict.endswith('.JPG') or pict.endswith('.CR2'):
            print(f'[+] Обрабатываю изображение: "{pict}"...')
            # Открытие изображения
            image = Image.open(os.path.join(input_path, pict))

            # Удаление фона
            output = remove(image)

            # Создание белого фона с альфа-каналом
            white_bg = Image.new("RGBA", desired_size, (255, 255, 255, 255))

            # Вырезание изображения с фона
            bbox = output.getbbox()
            output = output.crop(bbox)

            # Увеличение резкости
            enhancer = ImageEnhance.Sharpness(output)
            output = enhancer.enhance(1.5)  # Увеличиваем резкость в 1.5 раза
            output.save(os.path.join(PATH_WITHOUT_BACKROUND, f'{pict.split(".")[0]}.png'),'PNG')

            # Уменьшение размера изображения с сохранением пропорций
            width, height = output.size
            max_dimension = max(width, height)
            if max_dimension > MAX_SIZE:
                scale = MAX_SIZE / max_dimension
                new_width = int(width * scale)
                new_height = int(height * scale)
                output = output.resize((new_width, new_height), Image.LANCZOS)

            # Вставка вырезанного изображения на белый фон
            x_offset = (desired_size[0] - output.size[0]) // 2
            y_offset = (desired_size[1] - output.size[1]) // 2
            white_bg.paste(output, (x_offset, y_offset), output)

            # Конвертация изображения в формат RGB
            white_bg = white_bg.convert("RGB")

            # Сохранение результата в формате JPEG
            white_bg.save(os.path.join(output_path, f'{pict.split(".")[0]}.jpg'), 'JPEG')

def get_target_path(user_input):
    while not os.path.isdir(user_input):
        print(f'Папка "{user_input}" не найдена\n')
    print(f"\nРаботаем с папкой {user_input}\n")
    return user_input

def main(user_input, user_output):
    print("Стартуем")
    process_image(get_target_path(user_input), user_output)
    print('\n[+] Обработка изображений завершена!')

main(PATH_FROM_1C, PATH_TO_1C) #меняем аргументы, меняем резулат
