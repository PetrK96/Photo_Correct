from PIL import Image, ImageFilter

file_name = "/Users/petrkulikov/spare_parts/IMG_4120.jpeg"

with Image.open(file_name) as img_part:
    img_part.load()

red, green, blue = img_part.split()

threshold = 150

img_part_threshold = green.point(lambda x: 255 if x > threshold else 0)
img_part_threshold = img_part_threshold.convert("1")
#img_part_threshold.show()


def erode(cycles, image):
    for _ in range(cycles):
        image = image.filter(ImageFilter.MaxFilter(3))
    return image


def dilate(cycles, image):
    for _ in range(cycles):
        image = image.filter(ImageFilter.MinFilter(3))
    return image


eroded_img_part_threshold = erode(2, img_part_threshold)
eroded_img_part_threshold.show()

dilated_img_part_threshold = dilate(66, eroded_img_part_threshold)
dilated_img_part_threshold.show()


eroded_img_part_threshold = erode(80, dilated_img_part_threshold)
eroded_img_part_threshold.show()