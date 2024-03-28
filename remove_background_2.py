import os
from rembg import remove
from PIL import Image


desired_size = (500, 500)
USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'

def remove_bg(input_path, output_path):
    for pict in os.listdir(input_path):
        if pict.endswith('.png') or pict.endswith('.jpg') or pict.endswith('.jpeg'):
            print(f'[+] Удаляю фон: "{pict}"...')
            output = remove(Image.open(os.path.join(input_path, pict)))
            output = output.resize(desired_size, Image.LANCZOS)
            output.save(os.path.join(output_path, f'{pict.split(".")[0]}.png'))
            
def get_target_path(user_input):
    while not os.path.isdir(user_input):
        print(f'Папка "{user_input}" не найдена\n')
    print(f"\nРаботаем с папкой {user_input}\n")
    return user_input

def main(user_input, user_output):
    print("Погнали")
    remove_bg(get_target_path(user_input), user_output)
    print('\n[+] Удаление фона изображений завершено!')
    
main(USER_INPUT, USER_OUTPUT)
