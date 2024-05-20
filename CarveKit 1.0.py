import os
from carvekit.api.high import HiInterface
from carvekit.ml.wrap import SegformerB0, U2Net
from carvekit.trimap.generator import TrimapGenerator
from carvekit.pipelines.postprocessing import FBA
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np


# Предобработка изображений
def increase_contrast(image, factor=2.0):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def reduce_noise(image):
    open_cv_image = np.array(image)
    open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
    denoised_image = cv2.fastNlMeansDenoisingColored(open_cv_image, None, 10, 10, 7, 21)
    return Image.fromarray(cv2.cvtColor(denoised_image, cv2.COLOR_BGR2RGB))


def convert_to_grayscale(image):
    return image.convert("L")


def apply_blur(image, radius=2):
    return image.filter(ImageFilter.GaussianBlur(radius))


def crop_image(image):
    return image.crop(image.getbbox())


# Инициализация CarveKit
segmentation_model = U2Net()
trimap_generator = TrimapGenerator()
postprocessing_model = FBA()

interface = HiInterface(
    segmentation_model=segmentation_model,
    trimap_generator=trimap_generator,
    postprocessing_model=postprocessing_model
)

input_folder = 'path_to_input_images'
output_folder = 'path_to_output_images'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for image_name in os.listdir(input_folder):
    if image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        input_path = os.path.join(input_folder, image_name)
        output_path = os.path.join(output_folder, image_name)

        # Открытие изображения
        input_image = Image.open(input_path).convert("RGB")

        # Применение предобработок
        processed_image = increase_contrast(input_image)
        processed_image = reduce_noise(processed_image)
        processed_image = convert_to_grayscale(processed_image)
        processed_image = apply_blur(processed_image)
        processed_image = crop_image(processed_image)

        # Удаление фона с помощью CarveKit
        output_images = interface([processed_image])
        output_image = output_images[0]

        # Сохранение результата
        output_image.save(output_path)

print("Фон успешно удален из всех изображений.")
