'''
官方给出的csv中的
{
 "meta":{},
 "id":"88eb919f-6f12-486d-9223-cd0c4b581dbf",
 "items":
[
     {"meta":{"rectStartPointerXY":[622,2728],"pointRatio":0.5,"geometry":[622,2728,745,3368],"type":"BBOX"},"id":"e520a291-bbf7-4032-92c6-dc84a1fc864e","properties":{"create_time":1620610883573,"accept_meta":{},"mark_by":"LABEL","is_system_map":false},"labels":{"鏍囩":"ground"}}
     {"meta":{"pointRatio":0.5,"geometry":[402.87,621.81,909,1472.01],"type":"BBOX"},"id":"2c097366-fbb3-4f9d-b5bb-286e70970eba","properties":{"create_time":1620610907831,"accept_meta":{},"mark_by":"LABEL","is_system_map":false},"labels":{"鏍囩":"safebelt"}}
     {"meta":{"rectStartPointerXY":[692,1063],"pointRatio":0.5,"geometry":[697.02,1063,1224,1761],"type":"BBOX"},"id":"8981c722-79e8-4ae8-a3a3-ae451300d625","properties":{"create_time":1620610943766,"accept_meta":{},"mark_by":"LABEL","is_system_map":false},"labels":{"鏍囩":"offground"}}
 ],
 "properties":{"seq":"1714"},"labels":{"invalid":"false"},"timestamp":1620644812068
 }
'''

import pandas as pd
import json
import os
from PIL import Image

df = pd.read_csv(r"C:\Users\Administrator\Desktop\safety_belt\3train_rname.csv", header=None)
df_img_path = df[4]
df_img_mark = df[5]
# print(df_img_mark)
# 统计一下类别,并且重新生成原数据集标注文件，保存到json文件中
dict_class = {
    "badge": 0,
    "offground": 0,
    "ground": 0,
    "safebelt": 0
}
dict_lable = {
    "badge": 1,
    "offground": 2,
    "ground": 3,
    "safebelt": 4
}
data_dict_json = []
image_width, image_height = 0, 0
ids = 0
false = False  # 将其中false字段转化为布尔值False
true = True  # 将其中true字段转化为布尔值True
for img_id, one_img in enumerate(df_img_mark):
    # print('img_id',img_id)
    one_img = eval(one_img)["items"]
    # print('one_img',one_img)
    one_img_name = df_img_path[img_id]
    img = Image.open(os.path.join("./", one_img_name))
    # print(os.path.join("./", one_img_name))
    ids = ids + 1
    w, h = img.size
    image_width += w
    # print(image_width)
    image_height += h
    # print(one_img_name)
    i = 1
    for one_mark in one_img:
        # print('%d      '%i,one_mark)

        one_label = one_mark["labels"]['标签']
        # print('%d      '%i,one_label)
        try:
            dict_class[str(one_label)] += 1
            # category = str(one_label)
            category = dict_lable[str(one_label)]
            bbox = one_mark["meta"]["geometry"]
        except:
            dict_class["badge"] += 1  # 标签为"监护袖章(红only)"表示类别"badge"
            # category = "badge"
            category = 1
            bbox = one_mark["meta"]["geometry"]
        i += 1

        one_dict = {}
        one_dict["name"] = str(one_img_name)
        one_dict["category"] = category
        one_dict["bbox"] = bbox
        data_dict_json.append(one_dict)
print(image_height / ids, image_width / ids)
print(dict_class)
print(len(data_dict_json))
print(data_dict_json[0])
with open("./data.json2", 'w') as fp:
    json.dump(data_dict_json, fp, indent=1, separators=(',', ': '))  # 缩进设置为1，元素之间用逗号隔开 ， key和内容之间 用冒号隔开
    fp.close()
