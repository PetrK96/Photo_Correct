import cv2
import numpy as np
import os

USER_INPUT = "/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото запчасти"
USER_OUTPUT = '/Volumes/srvfsz/2.4 Сервисная служба (Общая)/Фото обработанные'

class ImageProcessor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def remove_background_chromakey(self, img):
        # Преобразуем изображение в LAB цветовое пространство
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        
        # Извлекаем канал 'A'
        a_channel = lab[:,:,1]

        # Пороговая обработка канала 'A'
        _, mask = cv2.threshold(a_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Размываем пороговую маску
        blur = cv2.GaussianBlur(mask, (0, 0), sigmaX=5, sigmaY=5, borderType=cv2.BORDER_DEFAULT)
        
        # Растягиваем значения, чтобы 255 стало 255, а 127.5 стало 0
        mask = cv2.normalize(blur, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

        # Добавляем маску к изображению как альфа-канал
        result = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        result[:, :, 3] = mask

        return result

    def process_images(self):
        for filename in os.listdir(self.input_path):
            if filename.endswith('.jpg') or filename.endswith('.JPG') or filename.endswith('.jpeg'):
                file_path = os.path.join(self.input_path, filename)
                print(f"Обработка изображения: {file_path}")

                # Загрузка изображения
                print("Загрузка изображения...")
                image = cv2.imread(file_path)

                # Удаление фона с использованием chromakey
                print("Удаление фона с использованием chromakey...")
                image_with_alpha = self.remove_background_chromakey(image)

                # Проверка формы изображения
                if image_with_alpha.shape[2] != 4:
                    raise ValueError("Форма изображения неверная. Ожидался альфа-канал.")

                # Преобразование размера
                print("Преобразование размера...")
                image_with_alpha = cv2.resize(image_with_alpha, (500, 500))

                # Создание белого фона
                print("Создание белого фона...")
                white_bg = np.ones((500, 500, 4), dtype=np.uint8) * 255

                # Вставка изображения на белый фон
                print("Вставка изображения на белый фон...")
                x_offset = (white_bg.shape[1] - image_with_alpha.shape[1]) // 2
                y_offset = (white_bg.shape[0] - image_with_alpha.shape[0]) // 2
                white_bg[y_offset:y_offset + image_with_alpha.shape[0], 
                         x_offset:x_offset + image_with_alpha.shape[1]] = image_with_alpha

                # Сохранение обработанного изображения
                print("Сохранение обработанного изображения...")
                output_file_path = os.path.join(self.output_path, filename)
                cv2.imwrite(output_file_path, white_bg)

                print(f"Обработка завершена: {output_file_path}\n")

                # Ожидание нажатия клавиши пользователем
                cv2.waitKey(0)

# Создаем экземпляр класса ImageProcessor и обрабатываем изображения
processor = ImageProcessor(USER_INPUT, USER_OUTPUT)
processor.process_images()

