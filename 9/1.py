import cv2  
import numpy as np  
import os  
from PIL import Image  
from scipy.spatial.distance import cdist  
from tqdm import tqdm  # 导入 tqdm 库以显示进度条  
  
# 读取视频  
video_path = 'C:\\Users\\Genshin\\Desktop\\9\\1246578027-1-192.mp4'  
cap = cv2.VideoCapture(video_path)  
  
# 检查视频是否成功打开  
if not cap.isOpened():  
    print("Error: Could not open video.")  
    exit()  
  
# 设置像素块大小  
block_size = 10  # 例如，10x10 的像素块  
  
# 读取文件夹中的图片并计算其平均颜色  
images_dir = r"C:\Users\Genshin\Desktop\8"  
image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]  
image_colors = []  
for img_path in image_files:  
    img = Image.open(img_path).convert('RGB')  
    avg_color = np.array(img.resize((block_size, block_size))).mean(axis=(0, 1)).astype(np.float32)  
    image_colors.append((img_path, avg_color))  
  
# 获取视频的总帧数  
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  
  
# 初始化输出视频写入器（注意：这里应该根据原视频的帧率来设置fps）  
fps = cap.get(cv2.CAP_PROP_FPS)  # 获取原视频的帧率  
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 设置视频编码格式  
out_path = 'output_video.mp4'  
out = cv2.VideoWriter(out_path, fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))  
  
# 处理视频帧  
output_frames = []  
with tqdm(total=frame_count, desc="Processing frames", unit="frame") as pbar:  
    while cap.isOpened():  
        ret, frame = cap.read()  
        if not ret:  
            break  
  
        height, width, _ = frame.shape  
        for y in range(0, height, block_size):  
            for x in range(0, width, block_size):  
                block = frame[y:y+block_size, x:x+block_size]  
                block_color = np.array(block).mean(axis=(0, 1)).astype(np.float32)  
  
                # 计算颜色距离并找到最接近的图片  
                distances = cdist([block_color], [color for _, color in image_colors], 'euclidean')[0]  
                closest_idx = np.argmin(distances)  
                closest_img_path = image_colors[closest_idx][0]  
  
                # 读取并替换像素块  
                closest_img = Image.open(closest_img_path).convert('RGB')  
                closest_img_resized = closest_img.resize((block_size, block_size))  
                closest_img_array = np.array(closest_img_resized)  
  
                frame[y:y+block_size, x:x+block_size] = closest_img_array  
  
        # 将处理后的帧写入输出视频（或者存储在列表中，最后一起写入，这里选择直接写入以节省内存）  
        out.write(frame)  
        pbar.update(1)  # 更新进度条  
  
# 释放资源  
out.release()  
cap.release()
