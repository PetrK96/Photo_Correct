import os
from rembg import remove
from PIL import Image, ImageEnhance

desired_size = (500, 500)
USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'

def remove_bg(input_path, output_path):
    for pict in os.listdir(input_path):
        if pict.endswith('.png') or pict.endswith('.JPG') or pict.endswith('.jpeg'):
            print(f'[+] Удаляю фон: "{pict}"...')
            # Удаление фона
            output = remove(Image.open(os.path.join(input_path, pict)))

            # Увеличение контрастности
            enhancer = ImageEnhance.Contrast(output)
            output = enhancer.enhance(1.2)  # Увеличиваем контрастность в 1.2 раза

            # Увеличение резкости
            enhancer = ImageEnhance.Sharpness(output)
            output = enhancer.enhance(1.5)  # Увеличиваем резкость в 1.5 раза

            # Увеличение яркости
            enhancer = ImageEnhance.Brightness(output)
            output = enhancer.enhance(1.2)  # Увеличиваем яркость в 1.2 раза

            # Увеличение разрешения
            output = output.resize(desired_size, Image.LANCZOS)

            # Создание белого фона
            white_bg = Image.new("RGB", output.size, (255, 255, 255))

            # Установка альфа-канала
            output_with_alpha = output.convert("RGBA")
            white_bg.paste(output_with_alpha, (0, 0), output_with_alpha)

            # Сохранение результата
            white_bg.save(os.path.join(output_path, f'{pict.split(".")[0]}.jpg'), 'JPEG')

def get_target_path(user_input):
    while not os.path.isdir(user_input):
        print(f'Папка "{user_input}" не найдена\n')
    print(f"\nРаботаем с папкой {user_input}\n")
    return user_input

def main(user_input, user_output):
    print("Погнали")
    remove_bg(get_target_path(user_input), user_output)
    print('\n[+] Удаление фона изображений и добавление белого фона завершено!')

main(USER_INPUT, USER_OUTPUT)
