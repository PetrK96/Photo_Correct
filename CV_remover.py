import numpy as np
import cv2 as cv
import sys
from PIL import Image

image = cv.imread("/Users/petrkulikov/spare_parts/201-2115-1922.JPG", cv.IMREAD_UNCHANGED)
original_image = image.copy()

gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
blurred = cv.GaussianBlur(gray_image, (21, 51), 3)

edges = cv.Canny(blurred, threshold1=5, threshold2=6)

_, thresholded = cv.threshold(edges, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
mask = cv.morphologyEx(thresholded, cv.MORPH_CLOSE, kernel, iterations=4)

data = mask.tolist()
sys.setrecursionlimit(10**8)
for i in range(len(data)):
    for j in range(len(data[i])):
        if data[i][j] != 255:
            data[i][j] = -1
        else:
            break
    for j in range(len(data[i]) - 1, -1, -1):
        if data[i][j] != 255:
            data[i][j] = -1
        else:
            break

image_array = np.array(data)
image_array[image_array != -1] = 255
image_array[image_array == -1] = 0

mask = np.array(image_array, np.uint8)

result = cv.bitwise_and(original_image, original_image, mask=mask)
result[mask == 0] = 255

cv.imwrite("/Users/petrkulikov/spare_parts/201-2115-1922- removed.png", result)

img = Image.open('/Users/petrkulikov/spare_parts/201-2115-1922- removed.png')
img.convert("RGBA")
datas = img.getdata()

newData = []
for item in datas:
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append(((0,0,0,0)))
    else:
        newData.append(item)

img.putdata(newData)
img.save("/Users/petrkulikov/spare_parts//IMG.png", "PNG")
