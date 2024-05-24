import os

def rename_part(file_name, adding_name, changed_symbols):
    new_file_name = file_name.replace(changed_symbols, adding_name)
    return new_file_name


user_input = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти/запчасти для переименования/parts"

for file in os.listdir(user_input):
    if file.startswith('зч.'):
        new_name = rename_part(file, "10",changed_symbols="зч.")
        os.rename(user_input+'/'+file, user_input+'/'+new_name)
    elif file.startswith('z.'):
        new_name = rename_part(file, "20",changed_symbols="z.")
        os.rename(user_input+'/'+file, user_input+'/'+new_name)

