import os
import re
import shutil
import xml.etree.ElementTree as ET


# 1.用于查询数据集内指定标签序号，复制出查询的内容
def count_starting_numbers(folder_path, image_folder_path, save_path, txt_save_path):
    # 初始化统计字典
    global file_path
    count_dict = {}
    # 初始化文件名字典
    number_to_files = {}

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # 仅处理txt文件
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                # 逐行读取文件内容
                for line in file:
                    # 使用正则表达式匹配开头的数字
                    match = re.match(r'^\d+', line)
                    if match:
                        number = int(match.group())  # 提取匹配的数字
                        # 更新统计字典
                        if number in count_dict:
                            count_dict[number] += 1
                        else:
                            count_dict[number] = 1
                        # 更新文件名字典
                        if number in number_to_files:
                            number_to_files[number].append(filename)
                        else:
                            number_to_files[number] = [filename]

    # 打印统计结果
    for number, count in count_dict.items():
        print(f"类别：{number}出现了{count} 次")

    # 输入要查找的数字
    target_number = int(input("请输入要查找的类别编号: "))  # 在这里选择你想查询的数字
    if target_number in number_to_files:
        print(f"类别编号 {target_number} 出现在以下文件中:")
        for file in number_to_files[target_number]:
            print(file)

        store_content = input("是否要存储查询的内容？ (yes/no): ")
        if store_content.lower() == "yes":
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            for file in number_to_files[target_number]:
                output_filename = f"number_{target_number}_files.txt"
                output_file_path = os.path.join(save_path, output_filename)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(f"数字 {target_number} 出现的文件名列表:\n")
                    for filename in number_to_files[target_number]:
                        output_file.write(f"{filename}\n")
                print(f"查询内容已存储到文件: {output_file_path}")
                # 复制对应的图片文件
                image_name = file.split('.')[0] + '.jpg'  # 假设图片文件名与txt文件名对应
                image_path = os.path.join(image_folder_path, image_name)
                if os.path.exists(image_path):
                    shutil.copy(image_path, save_path)
                    print(f"已复制图片文件: {image_name}")
                else:
                    print(f"未找到对应的图片文件: {image_name}")

                # 复制对应的txt文件
                txt_path = os.path.join(folder_path, file)
                if os.path.exists(txt_path):
                    shutil.copy(txt_path, txt_save_path)
                    print(f"已复制文本文件: {file}")
                else:
                    print(f"未找到对应的文本文件: {file}")
        else:
            print("结束进程")
    else:
        print(f"类别编号 {target_number} 不存在于任何文件中。")


# 2.用于将数据集标签的名称从指定的位数开始进行删减，例如prefix_length=10，则从名称第10位开始删除名称内容截止到后缀名
def rename_txt_files(input_folder, output_folder, prefix_length=1):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            # 匹配文件名中的内容并修改
            new_filename = re.sub(rf'^(.{{{prefix_length}}}).*?(\.txt)$', r'\1\2', filename)
            # 拼接输入和输出文件路径
            input_filepath = os.path.join(input_folder, filename)
            output_filepath = os.path.join(output_folder, new_filename)
            # 复制文件到输出文件夹并重命名
            shutil.copyfile(input_filepath, output_filepath)
            print(f'Renamed and copied {filename} to {new_filename}')


# 3.用于删除空内容的txt标签
def check_and_delete_empty_txt_files(folder_path):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):  # 只检查以 .txt 结尾的文件
            file_path = os.path.join(folder_path, filename)
            # 检查文件是否为空
            if os.path.getsize(file_path) == 0:
                # 如果文件为空，则删除文件
                os.remove(file_path)
                print(f"Deleted empty file: {filename}")


# 4.用于将txt格式标签转换为xml格式
def convert_txt_to_xml(yolo_labels_dir, xml_labels_dir, image_width, image_height):
    # Create output directory if not exists
    if not os.path.exists(xml_labels_dir):
        os.makedirs(xml_labels_dir)

    for filename in os.listdir(yolo_labels_dir):
        if filename.endswith('.txt'):
            xml_filename = filename.replace('.txt', '.xml')
            xml_path = os.path.join(xml_labels_dir, xml_filename)
            with open(os.path.join(yolo_labels_dir, filename), 'r') as f:
                lines = f.readlines()
                root = ET.Element("annotation")
                folder = ET.SubElement(root, "folder")
                folder.text = "images"  # You may need to change this according to your folder structure
                filename_xml = ET.SubElement(root, "filename")
                filename_xml.text = filename.replace('.txt', '.jpg')  # Assuming images have jpg extension
                for line in lines:
                    class_id, x_center, y_center, width, height = map(float, line.strip().split())
                    class_id = int(class_id)
                    x_center *= image_width  # Image width
                    y_center *= image_height  # Image height
                    width *= image_width
                    height *= image_height

                    object_xml = ET.SubElement(root, "object")
                    name_xml = ET.SubElement(object_xml, "name")
                    name_xml.text = str(class_id)
                    bbox_xml = ET.SubElement(object_xml, "bndbox")
                    xmin_xml = ET.SubElement(bbox_xml, "xmin")
                    xmin_xml.text = str(int(x_center - width / 2))
                    ymin_xml = ET.SubElement(bbox_xml, "ymin")
                    ymin_xml.text = str(int(y_center - height / 2))
                    xmax_xml = ET.SubElement(bbox_xml, "xmax")
                    xmax_xml.text = str(int(x_center + width / 2))
                    ymax_xml = ET.SubElement(bbox_xml, "ymax")
                    ymax_xml.text = str(int(y_center + height / 2))

                tree = ET.ElementTree(root)
                tree.write(xml_path)
                print(f"Converted {filename} to {xml_filename}")


# 5.用于将xml格式标签转换为txt格式
def extract_coordinates(xml_path, w, h):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    coordinates = []

    for obj in root.findall('.//object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        xmin = bndbox.find('xmin').text
        ymin = bndbox.find('ymin').text
        xmax = bndbox.find('xmax').text
        ymax = bndbox.find('ymax').text

        if name == "bus":
            classify = 0
        elif name == "van":
            classify = 1
        elif name == "car":
            classify = 2
        else:
            continue
        xmin = int(xmin)
        xmax = int(xmax)
        ymin = int(ymin)
        ymax = int(ymax)
        cx = round((xmin + (xmax - xmin) / 2) / w, 3)
        cy = round((ymin + (ymax - ymin) / 2) / h, 3)
        w1 = round((xmax - xmin) / w, 3)
        h1 = round((ymax - ymin) / h, 3)

        coordinates.append((f'{classify}', f'{cx}', f'{cy}', f'{w1}', f'{h1}'))

    return coordinates


def convert_xml_to_txt(input_folder, output_folder, w, h):
    # 确保输出文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(input_folder, filename)
            coordinates = extract_coordinates(xml_path, w, h)

            # 创建对应的TXT文件
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(output_folder, txt_filename)

            # 将坐标信息写入TXT文件
            with open(txt_path, 'w') as txt_file:
                for coord in coordinates:
                    txt_file.write(' '.join(coord) + '\n')
                    print(f"Converted {filename} to {txt_filename}")


if __name__ == "__main__":
    # 传入文件夹路径调用函数进行统计
    txt_folder_path = r"path/to/txt/input"
    txt_save_path = r"path/to/txt/output"
    xml_folder_path = r"path/to/xml/input"
    xml_save_path = r"path/to/xml/output"
    image_folder_path = r"path/to/image/intput"
    image_save_path = r"path/to/image/output"

    count_starting_numbers(txt_folder_path, image_folder_path, image_save_path, txt_save_path)

    # prefix_length = 17  # 可以根据需要修改第几位开始的字符的长度
    # rename_txt_files(txt_folder_path, txt_save_path, prefix_length)

    # check_and_delete_empty_txt_files(txt_save_path)

    width = 4640  # 输入图片实际宽度
    height = 3488  # 输入图片实际高度

    # convert_txt_to_xml(txt_folder_path, xml_save_path, width, height)

    # convert_xml_to_txt(xml_folder_path, txt_save_path, width, height)
