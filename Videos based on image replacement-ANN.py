import cv2
import numpy as np
import os
import faiss  # 引入FAISS库
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import VideoFileClip
import queue
import threading

# 获取用户输入
video_path = input("请输入视频文件路径: ")
output_dir = input("请输入输出文件目录: ")
output_name = input("请输入输出文件名: ")
images_dir = input("请输入图片库所在路径: ")
block_size = int(input("请输入处理视频的像素块大小: "))

# 读取视频
cap = cv2.VideoCapture(video_path)

# 检查视频是否成功打开
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# 设置像素块大小
block_size = block_size

# 读取文件夹中的图片并计算其平均颜色
image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
image_colors = []
image_arrays = []  # 存储调整大小后的图像数组

for img_path in image_files:
    img = cv2.imread(img_path)
    img_resized = cv2.resize(img, (block_size, block_size))  # 使用OpenCV调整大小
    avg_color = img_resized.mean(axis=(0, 1)).astype(np.float32)
    image_colors.append(avg_color)
    image_arrays.append(img_resized)  # 存储调整大小后的图像

# 构建FAISS ANN索引
d = avg_color.shape[0]  # 特征维度
nb = len(image_colors)  # 数据库大小
index = faiss.IndexFlatL2(d)  # 使用L2距离
index.add(np.array(image_colors).reshape(-1, d))  # 添加数据到索引

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 确保输出目录存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 设置输出路径和名称
out_path_no_audio = os.path.join(output_dir, f"{output_name}_no_audio_optimized_ann.mp4")
final_output_path = os.path.join(output_dir, f"{output_name}_with_audio_optimized_ann.mp4")

# 初始化输出视频写入器（注意：这里应该使用与输入视频相同的帧率和尺寸）
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或者使用 'XVID' 等其他编解码器
out = cv2.VideoWriter(out_path_no_audio, fourcc, fps, (frame_width, frame_height))

def process_frame(frame, index, image_arrays, block_size):
    new_frame = frame.copy()
    for y in range(0, frame.shape[0], block_size):
        for x in range(0, frame.shape[1], block_size):
            block = frame[y:y+block_size, x:x+block_size]
            if block.shape != (block_size, block_size, 3):  # 避免在边界处出现不完整的块
                continue
            block_color = block.mean(axis=(0, 1)).astype(np.float32).reshape(1, -1)

            # 使用FAISS进行近似最近邻搜索
            k = 1
            distances, indices = index.search(block_color, k)
            closest_img_array = image_arrays[indices[0][0]]

            # 替换像素块（注意：这里我们已经将图像调整为block_size，所以不需要调整大小）
            new_frame[y:y+block_size, x:x+block_size] = closest_img_array

    return new_frame

# 处理视频帧，使用多线程
frame_queue = queue.Queue(maxsize=10)  # 设置一个最大队列大小以避免内存溢出

def read_frames():
    ret, frame = cap.read()
    while ret:
        frame_queue.put((ret, frame))
        ret, frame = cap.read()
    frame_queue.put((False, None))  # 发送一个结束信号

# 启动帧读取线程
read_thread = threading.Thread(target=read_frames)
read_thread.start()

with ThreadPoolExecutor(max_workers=4) as executor, tqdm(total=frame_count, desc="Processing frames", unit="frame") as pbar:
    future_to_frame = {}
    while len(future_to_frame) < frame_count:
        ret, frame = frame_queue.get()
        if not ret:
            break  # 如果读取到结束信号，则停止处理
        future = executor.submit(process_frame, frame, index, image_arrays, block_size)
        future_to_frame[future] = None  # 我们不需要跟踪具体的帧索引，因为它们是按顺序处理的

        # 当有任务完成时，更新进度条并写入输出视频
        completed_future = next(iter(as_completed(future_to_frame)))
        result = completed_future.result()
        if result is not None:
            out.write(result)
        del future_to_frame[completed_future]  # 从字典中删除已完成的任务
        pbar.update(1)

# 等待帧读取线程结束
read_thread.join()

# 释放资源
out.release()
cap.release()

# 使用moviepy合并音频
original_video_clip = VideoFileClip(video_path)
processed_video_clip = VideoFileClip(out_path_no_audio)
final_video_clip = processed_video_clip.set_audio(original_video_clip.audio)
final_video_clip.write_videofile(final_output_path, codec='libx264', audio_codec='aac')

print(f"处理完成，输出文件位于: {final_output_path}")