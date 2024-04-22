import os
import re
import cv2
import shutil
import random
from PIL import Image, ExifTags
import xml.etree.ElementTree as ET


# 1.用于将数据集图片的名称从指定的位数开始进行删减，例如prefix_length=10，则从名称第10位开始删除名称内容截止到后缀名
def rename_img_files(input_folder, output_folder, prefix_length=1):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith('.img'):
            # 匹配文件名中的内容并修改
            new_filename = re.sub(rf'^(.{{{prefix_length}}}).*?(\.img)$', r'\1\2', filename)
            # 拼接输入和输出文件路径
            input_filepath = os.path.join(input_folder, filename)
            output_filepath = os.path.join(output_folder, new_filename)
            # 复制文件到输出文件夹并重命名
            shutil.copyfile(input_filepath, output_filepath)
            print(f'Renamed and copied {filename} to {new_filename}')


# 2.用于将数据集图片重新命名，先指定一个基本名称，再增加序号遍历
def rename_img_files2(folder_path, base_name, start_index=1):
    # 遍历文件夹中的所有文件
    for idx, filename in enumerate(sorted(os.listdir(folder_path))):
        # 仅处理图片文件
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # 构建新的文件名
            new_filename = f"{base_name}_{start_index + idx:03d}{os.path.splitext(filename)[1]}"
            # 生成新的文件路径
            new_filepath = os.path.join(folder_path, new_filename)
            # 旧的文件路径
            old_filepath = os.path.join(folder_path, filename)
            # 重命名文件
            os.rename(old_filepath, new_filepath)
            print(f"Renamed {filename} to {new_filename}")


# 3.用于将数据集图片转换成jpg格式
def convert_to_jpg(input_folder, output_folder):
    # 如果输出文件夹不存在，则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)

        # 确保文件是图片文件
        if os.path.isfile(filepath) and any(
                filename.lower().endswith(ext) for ext in ['.png', '.jpeg', '.gif', '.bmp', '.jpg', '.JPG']):
            try:
                # 打开图像文件
                with Image.open(filepath) as img:
                    # 将文件保存为.jpg格式
                    output_filepath = os.path.join(output_folder, os.path.splitext(filename)[0] + '.jpg')
                    img.convert('RGB').save(output_filepath)
                    print(f"Converted {filename} to JPG")
            except Exception as e:
                print(f"Failed to convert {filename}: {str(e)}")


# 4.用于删除数据集里没有对应标签的图片
def delete_jpg_without_txt(jpg_folder, txt_folder):
    """
    删除jpg文件夹中没有对应txt文件的jpg文件。

    Parameters:
        jpg_folder (str): jpg文件夹的路径。
        txt_folder (str): txt文件夹的路径。
    """
    # 遍历jpg文件夹中的文件
    for jpg_file in os.listdir(jpg_folder):
        if jpg_file.endswith('.jpg'):
            # 提取jpg文件名
            jpg_name = os.path.splitext(jpg_file)[0]

            # 构建对应的txt文件路径
            txt_file = os.path.join(txt_folder, jpg_name + '.txt')

            # 如果txt文件不存在，则删除jpg文件
            if not os.path.exists(txt_file):
                jpg_path = os.path.join(jpg_folder, jpg_file)
                os.remove(jpg_path)
                print(f"Deleted {jpg_file} because corresponding .txt file doesn't exist.")


# 5.用于删除数据集里没有对应图片的标签
def delete_txt_without_jpg(jpg_folder, txt_folder):
    """
    删除txt文件夹中没有对应jpg文件的txt文件。

    Parameters:
        jpg_folder (str): jpg文件夹的路径。
        txt_folder (str): txt文件夹的路径。
    """
    # 遍历jpg文件夹中的文件
    for jpg_file in os.listdir(txt_folder):
        if jpg_file.endswith('.txt'):
            # 提取jpg文件名
            jpg_name = os.path.splitext(jpg_file)[0]

            # 构建对应的txt文件路径
            txt_file = os.path.join(jpg_folder, jpg_name + '.jpg')

            # 如果txt文件不存在，则删除jpg文件
            if not os.path.exists(txt_file):
                jpg_path = os.path.join(txt_folder, jpg_file)
                os.remove(jpg_path)
                print(f"Deleted {jpg_file} because corresponding .txt file doesn't exist.")


# 6.用于对数据集图片进行镜像翻转
def mirror_images(input_folder, output_folder):
    # 确保输出文件夹存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)

        # 检查文件是否为图片
        if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            try:
                # 打开图片
                image = Image.open(input_path)
                # 镜像翻转
                mirrored_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                # 保存镜像翻转后的图片到输出文件夹
                output_path = os.path.join(output_folder, filename)
                mirrored_image.save(output_path)
                print(f"Processed: {filename}")
            except OSError as e:
                print(f"Error processing {filename}: {e}")


# 7.用于将数据集的图片和对应标签随机按指定比例分离
def split_files(image_folder, txt_folder, new_image_folder, new_txt_folder, split_percentage):
    # 获取图片和txt文件列表
    image_files = os.listdir(image_folder)
    txt_files = os.listdir(txt_folder)

    # 确保两个文件夹中的文件数量相同
    assert len(image_files) == len(txt_files)

    # 计算需要移动的文件数量
    num_files_to_move = int(len(image_files) * split_percentage)

    # 随机选择需要移动的文件
    files_to_move = random.sample(list(zip(image_files, txt_files)), num_files_to_move)

    # 移动文件
    for image_file, txt_file in files_to_move:
        # 打印每一对文件信息
        print("Moving:", image_file, "and", txt_file)
        # 构建原始文件路径
        image_src = os.path.join(image_folder, image_file)
        txt_src = os.path.join(txt_folder, txt_file)

        # 构建目标文件路径
        image_dest = os.path.join(new_image_folder, image_file)
        txt_dest = os.path.join(new_txt_folder, txt_file)

        # 移动文件
        shutil.move(image_src, image_dest)
        shutil.move(txt_src, txt_dest)

    print("按比例分割完成")


# 8.用于将数据集图片按指定宽和高像素进行等比例放大和缩放，短边缺失区域用指定颜色补全
def resize_and_pad_images(input_folder, output_folder, target_resolution=(4640, 3488), fill_color=(0, 0, 0)):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 获取文件路径
        input_filepath = os.path.join(input_folder, filename)
        output_filepath = os.path.join(output_folder, filename)

        # 仅处理图片文件
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # 打开图片
            with Image.open(input_filepath) as img:
                # 清除图片的旋转信息
                img = autorotate(img)
                # 计算按比例放大后的大小
                width_ratio = target_resolution[0] / img.width
                height_ratio = target_resolution[1] / img.height
                resize_ratio = min(width_ratio, height_ratio)
                new_width = round(img.width * resize_ratio)
                new_height = round(img.height * resize_ratio)
                # 使用 LANCZOS 方法缩放图片，保持比例
                resized_img = img.resize((new_width, new_height), resample=Image.LANCZOS)
                # 创建新的空白画布
                new_img = Image.new("RGB", target_resolution, fill_color)
                # 计算将图片放在中心的坐标
                offset = ((target_resolution[0] - new_width) // 2, (target_resolution[1] - new_height) // 2)
                # 将缩放后的图片粘贴到新的画布中心
                new_img.paste(resized_img, offset)
                # 保存修改后的图片到输出文件夹
                new_img.save(output_filepath)
                print(f"Resized and padded {filename} to {target_resolution}")


def autorotate(image):
    """
    清除图片的旋转信息
    """
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass
    return image


# 9.用于查看数据集内所有图片的路径和名称
def image_display_path(folder_path):
    # 获取文件夹内所有图片文件的路径和名称
    image_paths_and_names = []

    # 遍历文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                image_path = os.path.join(root, file)
                image_paths_and_names.append(image_path)

    # 输出图片的路径和名称
    for image_path in image_paths_and_names:
        print(image_path)


# 10.用于根据yolo格式的txt标签对数据集内对应图片的目标进行裁剪
def crop_objects_txt(input_folder, label_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 处理每个图像和其对应的标签文件
    for image_name in os.listdir(input_folder):
        if image_name.endswith(".jpg"):
            image_path = os.path.join(input_folder, image_name)
            label_path = os.path.join(label_folder, os.path.splitext(image_name)[0] + ".txt")
            if os.path.exists(label_path):
                crop_objects_for_image(image_path, label_path, output_folder)
            else:
                print("Label file not found for:", image_name)


def crop_objects_for_image(image_path, label_path, output_folder):
    # 读取图像
    image = cv2.imread(image_path)
    height, width = image.shape[:2]

    # 读取标签文件
    with open(label_path, 'r') as file:
        lines = file.readlines()

    # 解析标签信息
    for line in lines:
        class_id, x_center, y_center, w, h = map(float, line.split())
        x_min = int((x_center - w / 2) * width)
        y_min = int((y_center - h / 2) * height)
        x_max = int((x_center + w / 2) * width)
        y_max = int((y_center + h / 2) * height)

        # 裁剪目标
        cropped_object = image[y_min:y_max, x_min:x_max]

        # 输出裁剪后的图片到另一个文件夹
        output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_crop_" + str(int(class_id)) + ".jpg"
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, cropped_object)

        # 打印处理的图片名称
        print("Processed:", output_filename)


# 11.用于根据xml格式标签对数据集内对应图片的目标进行裁剪
def crop_objects_xml(xml_folder, image_folder, output_folder):
    for xml_file in os.listdir(xml_folder):
        if not xml_file.endswith('.xml'):
            continue

        # 解析 XML 文件
        tree = ET.parse(os.path.join(xml_folder, xml_file))
        root = tree.getroot()

        # 获取图像文件名
        image_filename = root.find('filename').text
        image_path = os.path.join(image_folder, image_filename)

        # 加载图像
        image = cv2.imread(image_path)

        for obj in root.findall('object'):
            # 获取目标坐标
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)

            # 裁剪图像
            cropped_image = image[ymin:ymax, xmin:xmax]

            # 确保输出文件夹存在
            os.makedirs(output_folder, exist_ok=True)

            # 保存裁剪后的图像
            output_filename = os.path.splitext(xml_file)[0] + '_' + obj.find('name').text + '.jpg'
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, cropped_image)


# 11.用于将数据集图片按指定方向和角度进行旋转（不改变原有图片宽和高）
def rotate_and_crop_images(input_folder, output_folder, angle, direction):
    """
    Rotate and crop images in the specified folder and save them to the output folder.

    Parameters:
    - input_folder: The path to the folder containing input images.
    - output_folder: The path to the folder to save processed images.
    - angle: The angle to rotate the images (in degrees).
    - direction: The direction to rotate the images, either 'left' or 'right'.
    """
    # Ensure direction is valid
    if direction not in ['left', 'right']:
        raise ValueError("Direction must be 'left' or 'right'.")

    # Get a list of image files in the input folder
    image_files = [f for f in os.listdir(input_folder) if
                   f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]

    # Iterate through each image file
    for image_file in image_files:
        input_path = os.path.join(input_folder, image_file)
        output_path = os.path.join(output_folder, image_file)

        # Open the image
        img = Image.open(input_path)

        # Rotate the image
        if direction == 'left':
            rotated_img = img.rotate(angle, expand=True)
        else:
            rotated_img = img.rotate(-angle, expand=True)

        # Crop the image to original dimensions
        width, height = img.size
        rotated_width, rotated_height = rotated_img.size
        left = (rotated_width - width) / 2
        top = (rotated_height - height) / 2
        right = (rotated_width + width) / 2
        bottom = (rotated_height + height) / 2
        cropped_img = rotated_img.crop((left, top, right, bottom))

        # Print processing information
        print(f"Processed {image_file}:")
        print(f"- Rotated Angle: {angle}, Rotated direction: {direction}")
        print(f"- Original size: {img.size}, Rotated and cropped size: {cropped_img.size}")

        # Save the processed image to the output folder
        cropped_img.save(output_path)


# 12.用于将数据集图片按指定方向和角度进行旋转
def rotate_images(input_folder, output_folder, rotation_angle):
    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 获取文件路径
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 检查文件是否为图片
        if os.path.isfile(input_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # 打开图片文件
            img = Image.open(input_path)

            # 旋转图片
            rotated_img = img.rotate(rotation_angle, expand=True)

            # 保存旋转后的图片到输出文件夹
            rotated_img.save(output_path)
            print(f"Processed {filename}:")
            print(f"- Rotated Angle: {rotation_angle}")

            # 关闭图片文件
            img.close()


if __name__ == "__main__":
    # 调用函数并传入文件夹路径
    xml_input_folder = 'path/to/xml_files'
    xml_output_folder = 'path/to/xml_files'
    txt_input_folder = r'path/to/txt_files'
    txt_output_folder = 'path/to/txt_files'
    jpg_input_folder = r'path/to/img_files'
    jpg_output_folder = r'path/to/img_files'

    # prefix_length = 17  # 可以根据需要修改第几位开始的字符的长度
    # rename_img_files(jpg_input_folder, jpg_output_folder, prefix_length)

    base_name = "IMG_20240416"  # 基础名称
    start_index = 377  # 起始索引
    # rename_img_files2(jpg_input_folder, base_name, start_index)

    # convert_to_jpg(jpg_input_folder, jpg_output_folder)

    # delete_jpg_without_txt(jpg_input_folder, txt_input_folder)
    # delete_txt_without_jpg(jpg_input_folder, txt_input_folder)

    # mirror_images(jpg_input_folder, jpg_output_folder)

    split_percentage = 0.3  # 设置分割百分比
    # split_files(jpg_input_folder, txt_input_folder, jpg_output_folder, txt_output_folder, split_percentage)  # 分割文件

    target_resolution = (1920, 1080)  # 指定图片缩放像素
    fill_color = (0, 0, 0)  # 指定目标分辨率和填充颜色，黑色
    # resize_and_pad_images(jpg_input_folder, jpg_output_folder, target_resolution, fill_color)

    # image_display_path(jpg_input_folder)

    # crop_objects_txt(jpg_input_folder, txt_input_folder, jpg_output_folder)

    # crop_objects_xml(xml_input_folder, jpg_input_folder, jpg_output_folder)

    angle = 90  # Specify the angle of rotation
    direction = 'right'  # Specify the direction of rotation ('left' or 'right')
    # rotate_and_crop_images(jpg_input_folder, jpg_output_folder, angle, direction)

    rotation_angle = -90  # 指定旋转的角度（顺时针为正，逆时针为负）
    # rotate_images(jpg_input_folder, jpg_output_folder, rotation_angle)
