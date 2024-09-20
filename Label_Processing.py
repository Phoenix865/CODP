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
def convert_xml_to_txt(xml_folder, txt_folder, classes):
    if not os.path.exists(txt_folder):
        os.makedirs(txt_folder)

    for xml_file in os.listdir(xml_folder):
        if xml_file.endswith('.xml'):
            xml_path = os.path.join(xml_folder, xml_file)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()

                image_width = int(root.find('size/width').text)
                image_height = int(root.find('size/height').text)

                if image_width == 0 or image_height == 0:
                    print(f'Error processing {xml_file}: Image width or height is zero')
                    continue

                txt_filename = os.path.splitext(xml_file)[0] + '.txt'
                txt_path = os.path.join(txt_folder, txt_filename)

                with open(txt_path, 'w') as txt_file:
                    for obj in root.findall('object'):
                        class_name = obj.find('name').text
                        if class_name not in classes:
                            continue
                        class_id = classes.index(class_name)

                        bndbox = obj.find('bndbox')
                        xmin = float(bndbox.find('xmin').text)
                        ymin = float(bndbox.find('ymin').text)
                        xmax = float(bndbox.find('xmax').text)
                        ymax = float(bndbox.find('ymax').text)

                        center_x = (xmin + xmax) / 2.0 / image_width
                        center_y = (ymin + ymax) / 2.0 / image_height
                        width = (xmax - xmin) / image_width
                        height = (ymax - ymin) / image_height

                        txt_file.write(f'{class_id} {center_x:.6f} {center_y:.6f} {width:.6f} {height:.6f}\n')

                print(f'Processed {xml_file}')

            except (ET.ParseError, AttributeError, TypeError, ValueError) as e:
                print(f'Error processing {xml_file}: {e}')
                continue


# 6.用于删除内容为空的txt格式标签
def delete_empty_txt_files(folder):
    for txt_file in os.listdir(folder):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(folder, txt_file)
            try:
                if os.path.getsize(txt_path) == 0:
                    os.remove(txt_path)
                    print(f'Deleted empty file: {txt_file}')
            except Exception as e:
                print(f'Error processing {txt_file}: {e}')


# 7.用于修改txt格式标签类别序号
def process_txt_files(folder, target_char, replace_char):
    for txt_file in os.listdir(folder):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(folder, txt_file)
            try:
                with open(txt_path, 'r') as file:
                    lines = file.readlines()

                modified_lines = []
                modified = False
                for line in lines:
                    if line.strip() and line[0] == target_char:
                        modified_lines.append(replace_char + line[1:])
                        modified = True
                    else:
                        modified_lines.append(line)

                if modified:
                    with open(txt_path, 'w') as file:
                        file.writelines(modified_lines)

                print(f'Processed {txt_file}')

            except Exception as e:
                print(f'Error processing {txt_file}: {e}')


# 8.用于修改文件名
def rename_files_in_folder(folder, suffix):
    for filename in os.listdir(folder):
        # 获取文件的完整路径
        old_file_path = os.path.join(folder, filename)

        # 检查是否为文件（排除文件夹）
        if os.path.isfile(old_file_path):
            # 分离文件名和扩展名
            name, ext = os.path.splitext(filename)
            # 创建新的文件名
            new_filename = f"{name}{suffix}{ext}"
            # 获取新的文件路径
            new_file_path = os.path.join(folder, new_filename)

            # 重命名文件
            os.rename(old_file_path, new_file_path)
            print(f"Renamed {filename} to {new_filename}")


# 9.用于删除txt格式标签里指定类别
def process_txt_files2(folder, target_chars):
    for txt_file in os.listdir(folder):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(folder, txt_file)
            try:
                with open(txt_path, 'r') as file:
                    lines = file.readlines()

                modified_lines = [line for line in lines if not (line.strip() and line[0] == target_chars)]

                with open(txt_path, 'w') as file:
                    file.writelines(modified_lines)

                print(f'Processed {txt_file}')

            except Exception as e:
                print(f'Error processing {txt_file}: {e}')


# 10.用于删除文件夹里指定类型的文件
def delete_files_of_type(folder_path, file_extension):
    """
    删除指定文件夹中的所有指定类型的文件。

    Parameters:
        folder_path (str): 目标文件夹的路径。
        file_extension (str): 要删除的文件类型（扩展名），例如'.xml'。
    """
    # 遍历文件夹中的所有文件
    for file in os.listdir(folder_path):
        # 检查文件是否是指定类型的文件
        if file.endswith(file_extension):
            # 构建文件的完整路径
            file_path = os.path.join(folder_path, file)
            # 删除文件
            os.remove(file_path)
            print(f"Deleted {file}")


# 11.用于删除除指定编号以外的类别
def process_txt_files3(folder, target_chars):
    for txt_file in os.listdir(folder):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(folder, txt_file)
            try:
                with open(txt_path, 'r') as file:
                    lines = file.readlines()

                # 修改条件，保留以 target_chars 中任意一个字符开头的行
                modified_lines = [line for line in lines if line.strip() and line[0] in target_chars]

                with open(txt_path, 'w') as file:
                    file.writelines(modified_lines)

                print(f'Processed {txt_file}')

            except Exception as e:
                print(f'Error processing {txt_file}: {e}')


# 12.用于将当前文件夹里的标签内容添加到另一个文件夹的标签
def append_txt_files(src_folder, dest_folder, dest_file=None):
    for src_file in os.listdir(src_folder):
        if src_file.endswith('.txt'):
            src_path = os.path.join(src_folder, src_file)
            dest_path = os.path.join(dest_folder, src_file)

            if os.path.exists(dest_path):
                try:
                    with open(src_path, 'r') as file:
                        lines = file.readlines()

                    with open(dest_path, 'a') as file:
                        for line in lines:
                            file.write(line)

                    print(f'Appended content from {src_file} to {dest_file}')

                except Exception as e:
                    print(f'Error processing {src_file}: {e}')
            else:
                print(f'Skipped {src_file}, no matching file in destination folder')


# 13.用于将当前文件夹里的标签内容指定编号交换顺序
def swap_content_by_prefix(folder, target_chars):
    for txt_file in os.listdir(folder):
        if txt_file.endswith('.txt'):
            txt_path = os.path.join(folder, txt_file)
            try:
                with open(txt_path, 'r') as file:
                    lines = file.readlines()

                modified_lines = []

                # 临时存储两个编号的内容
                content_a, content_b = None, None

                # 遍历每一行，寻找指定编号开头的行
                for line in lines:
                    stripped_line = line.strip()  # 去除前后空白字符
                    if stripped_line and stripped_line[0] == target_chars[0]:
                        content_a = stripped_line[1:].strip()  # 保存第一个编号后的内容
                    elif stripped_line and stripped_line[0] == target_chars[1]:
                        content_b = stripped_line[1:].strip()  # 保存第二个编号后的内容

                    # 当找到两个编号的内容后，交换它们
                    if content_a is not None and content_b is not None:
                        # 重写行，保持编号不变，但交换后面的内容
                        for i, line in enumerate(lines):
                            if line.startswith(target_chars[0]):
                                modified_lines.append(f'{target_chars[0]} {content_b}\n')
                            elif line.startswith(target_chars[1]):
                                modified_lines.append(f'{target_chars[1]} {content_a}\n')
                            else:
                                modified_lines.append(line)
                        break  # 一旦交换完成，停止处理

                # 将修改后的行写回文件
                with open(txt_path, 'w') as file:
                    file.writelines(modified_lines)

                print(f'Processed and swapped content in {txt_file}')

            except Exception as e:
                print(f'Error processing {txt_file}: {e}')


if __name__ == "__main__":
    # 传入文件夹路径调用函数进行统计
    txt_folder_path = 'path/to/your_files'
    txt_save_path = 'path/to/your_files'
    xml_folder_path = 'path/to/your_files'
    xml_save_path = 'path/to/your_files'
    image_folder_path = 'path/to/your_files'
    image_save_path = 'path/to/your_files'

    # count_starting_numbers(txt_folder_path, image_folder_path, image_save_path, txt_save_path)

    # prefix_length = 17  # 可以根据需要修改第几位开始的字符的长度
    # rename_txt_files(txt_folder_path, txt_save_path, prefix_length)

    # check_and_delete_empty_txt_files(txt_save_path)

    width = 4640  # 输入图片实际宽度
    height = 3488  # 输入图片实际高度

    # convert_txt_to_xml(txt_folder_path, xml_save_path, width, height)

    classes = ['people', 'vest', 'boot', 'glove', 'hat']  # 将实际的类别替换为相应的类别名称
    # convert_xml_to_txt(xml_folder_path, txt_save_path, classes)

    # delete_empty_txt_files(txt_folder_path)

    # 需要被更改的字符
    target_char = '2'
    # 要被修改成的字符
    replace_char = '5'
    # process_txt_files(txt_folder_path, target_char, replace_char)

    # 自定义的后缀
    suffix = '_a'
    # rename_files_in_folder(image_folder_path, suffix)

    # 要删除的字符
    target_char2 = '1'
    # process_txt_files2(txt_folder_path, target_char2)

    file_extension = '.xml'  # 你可以将其修改为任何需要的文件类型
    # delete_files_of_type(txt_folder_path, file_extension)

    # 要保留的字符
    target_char3 = '0'
    # process_txt_files3(txt_folder_path, target_char3)

    # append_txt_files(txt_folder_path, txt_save_path)

    target_char4 = '0', '1'
    # swap_content_by_prefix(txt_folder_path, target_char4)
