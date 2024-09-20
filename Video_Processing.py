from moviepy.editor import VideoFileClip
from PIL import Image
import os


# 1.视频格式转换
def convert_to_mp4(input_file, output_folder):
    # 加载视频文件
    video_clip = VideoFileClip(input_file)

    # 构造输出文件的完整路径
    output_file = os.path.join(output_folder, os.path.basename(input_file).split('.')[0] + '.mp4')

    # 设置输出视频的编解码器为 H.264，并导出为 MP4 格式
    video_clip.write_videofile(output_file, codec='libx264')


# 2.视频帧提取
def extract_frames(input_file, output_folder, frame_interval=1):
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)

    # 加载视频文件
    video_clip = VideoFileClip(input_file)

    # 提取每一帧并保存为图片
    frame_count = 0
    for frame in video_clip.iter_frames(fps=video_clip.fps):
        if frame_count % frame_interval == 0:
            # 构造输出文件的完整路径
            output_file = os.path.join(output_folder, f'frame3_{frame_count:04d}.jpg')
            # 保存帧为图片
            Image.fromarray(frame).save(output_file)
        frame_count += 1
        print(f"frame_{frame_count:04d}.png")


def extract_frames_from_folder(input_folder, output_folder, frame_interval=1):
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        raise ValueError(f"输入文件夹 {input_folder} 不存在")

    # 创建输出文件夹（如果不存在）
    os.makedirs(output_folder, exist_ok=True)

    # 遍历输入文件夹中的所有文件
    for file_name in os.listdir(input_folder):
        # 构造完整的文件路径
        input_file = os.path.join(input_folder, file_name)

        # 检查文件是否为视频文件（假设视频文件的扩展名为 .mp4, .avi, .mov, 等）
        if input_file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # 为当前视频创建一个子文件夹
            video_output_folder = os.path.join(output_folder, os.path.splitext(file_name)[0])
            os.makedirs(video_output_folder, exist_ok=True)

            # 提取当前视频的帧
            extract_frames(input_file, video_output_folder, frame_interval)


# 3.摄像头最大分辨率测试
def camera_quality():
    # 常见的分辨率列表，可以根据需要扩展
    resolutions = [
        (1920, 1080),
        (1600, 1200),
        (1280, 720),
        (1024, 768),
        (800, 600),
        (640, 480),
    ]

    # 打开摄像头
    cap = cv2.VideoCapture(0)

    max_width = 0
    max_height = 0

    for width, height in resolutions:
        # 设置分辨率
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # 读取实际设置的分辨率
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 检查是否成功设置
        if actual_width == width and actual_height == height:
            print(f"Supported resolution: {width}x{height}")
            # 更新最大分辨率
            if width * height > max_width * max_height:
                max_width, max_height = width, height

    # 释放摄像头
    cap.release()

    print(f"Maximum supported resolution: {max_width}x{max_height}")


if __name__ == '__main__':
    # 调用函数进行转换
    # convert_to_mp4('path/to/your_files',
    #                'path/to/your_files')
    # 替换 'input.avi' 为你的 AVI 文件路径，'/path/to/output_folder/' 为输出 MP4 文件夹路径

    extract_frames('path/to/your_files',
                   'path/to/your_files', frame_interval=3)
    # 每间隔10帧提取为图片，替换 'input.avi' 为你的 AVI 文件路径，'/path/to/output_frames/' 为输出图片文件夹路径

    # 使用示例
    # input_folder = 'path/to/your_files'
    # output_folder = 'path/to/your_files'
    # extract_frames_from_folder(input_folder, output_folder, frame_interval=6)
