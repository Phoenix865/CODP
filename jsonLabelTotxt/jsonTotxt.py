import json
import os
import cv2

file_name_list = {}

with open("./data.json2", 'r', encoding='utf-8') as fr:
    data_list = json.load(fr)

file_name = ''
label = 0
[x1, y1, x2, y2] = [0, 0, 0, 0]

for data_dict in data_list:
    for k, v in data_dict.items():
        if k == "category":
            label = v
        if k == "bbox":
            [x1, y1, x2, y2] = v
        if k == "name":
            file_name = v[9:-4]

    if not os.path.exists('./data1/'):
        os.mkdir('./data1/')

    image_path = './3_images/' + file_name + '.jpg'
    print(image_path)
    img = cv2.imread(image_path)

    if img is None:
        print(f"Warning: Could not read image file {image_path}")
        continue

    size = img.shape  # (h, w, channel)
    dh = 1. / size[0]
    dw = 1. / size[1]
    x = (x1 + x2) / 2.0
    y = (y1 + y2) / 2.0
    w = x2 - x1
    h = y2 - y1
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh

    # 保留6位小数
    x = format(x, ".6f")
    y = format(y, ".6f")
    w = format(w, ".6f")
    h = format(h, ".6f")

    content = f"{label - 1} {x} {y} {w} {h}\n"

    if not content:
        print(file_name)

    with open('./data1/' + file_name + '.txt', 'a+', encoding='utf-8') as fw:
        fw.write(content)
