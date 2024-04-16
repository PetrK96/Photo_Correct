import os
from rembg import remove
from PIL import Image, ImageEnhance
import pandas as pd 

USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные'
EXCEL_FILE = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/Для 1C обработанные/Таблица для загрузки фото в 1С.xlsx"
desired_size = (1200, 1200)
MAX_SIZE = 1000

def process_image(input_path, output_path, excel_file):
    data = []
    for pict in os.listdir(input_path):
        if pict.endswith('.jpeg') or pict.endswith('.JPG') or pict.endswith('.CR2'):
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
            
            width, height = output.size
            max_dimension = max(width, height)
            if max_dimension > MAX_SIZE:
                scale = MAX_SIZE / max_dimension
                new_width = int(width * scale)
                new_height = int(height * scale)
                output = output.resize((new_width, new_height), Image.LANCZOS)
                
            x_offset = (desired_size[0] - output.size[0]) // 2
            y_offset = (desired_size[1] - output.size[1]) // 2
            white_bg.paste(output, (x_offset, y_offset), output)

            # Увеличение резкости
            enhancer = ImageEnhance.Sharpness(output)
            output = enhancer.enhance(1.2)  # Увеличиваем резкость в 1.5 раза
        

            # Конвертация изображения в формат RGB
            white_bg = white_bg.convert("RGB")

            # Сохранение результата в формате JPEG
            output_filename = f'{pict.split(".")[0]}.jpg'
            output_filepath = os.path.join(output_path, output_filename)
            white_bg.save(output_filepath, 'JPEG')

            # Добавление информации об обработанном изображении в Excel
            filename_without_extension = pict[:-8]
            print(filename_without_extension)
            path_for_excel = output_filepath.replace("/", "\\")  # Замена символов "/" на "\"
            path_for_excel = path_for_excel.split("\\srvfsz\\")[1]  # Удаление части пути до папки "srvfsz" и пробелов
            data.append([filename_without_extension, f'Z:\\{path_for_excel}'])

    if os.path.exists(excel_file):
        df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
        df.to_excel(excel_file, index=False)
    else:
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df = pd.DataFrame(data, columns=['Наименование файла', 'Путь'])
            df.to_excel(writer, index=False)

def get_target_path(user_input):
    while not os.path.isdir(user_input):
        print(f'Папка "{user_input}" не найдена\n')
    print(f"\nРаботаем с папкой {user_input}\n")
    return user_input

def main(user_input, user_output, excel_file):
    print("Стартуем")
    process_image(get_target_path(user_input), user_output, excel_file)
    print('\n[+] Обработка изображений завершена и данные записаны в файл Excel!')

main(USER_INPUT, USER_OUTPUT, EXCEL_FILE)
