import os
import subprocess


def check_connection(network_path, username, password):
    try:
        # Подключение к сетевому пути (если не подключено)
        command = f'net use {network_path} /user:{username} {password}'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Подключение к {network_path} успешно!")
            if os.path.exists(network_path):
                print(f"Директория {network_path} доступна.")
            else:
                print(f"Директория {network_path} не найдена.")
        else:
            print(f"Не удалось подключиться к {network_path}. Код ошибки: {result.returncode}")
            print(f"Сообщение: {result.stderr}")

    except Exception as e:
        print(f"Произошла ошибка при попытке подключения: {e}")


# Указание пути
network_path = r'"\\srvfsz\Z\2.4 Сервисная служба (Общая)\Фото запчасти"'
username = 'kpn'
password = 'Plomba21'

#check_connection(network_path, username, password)

excel_file = r'"//srvfsz/Z/2.4 Сервисная служба (Общая)/Фото обработанные/Список запчастей для ренейма.xlsx"'
print(excel_file[:-1])