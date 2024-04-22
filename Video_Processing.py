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
            output_file = os.path.join(output_folder, f'frame_{frame_count:04d}.png')
            # 保存帧为图片
            Image.fromarray(frame).save(output_file)
        frame_count += 1


if __name__ == '__main__':
    # 调用函数进行转换
    convert_to_mp4('input.avi', '/path/to/output_folder/')  # 替换 'input.avi' 为你的 AVI 文件路径，'/path/to/output_folder/' 为输出 MP4 文件夹路径

    extract_frames('input.avi', '/path/to/output_frames/',
                   frame_interval=10)  # 提取每10帧为图片，替换 'input.avi' 为你的 AVI 文件路径，'/path/to/output_frames/' 为输出图片文件夹路径


