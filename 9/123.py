import cv2  
import numpy as np  
import os  
from sklearn.neighbors import KDTree  
from concurrent.futures import ProcessPoolExecutor, as_completed  
from tqdm import tqdm  
  
# 读取视频  
video_path = 'C:\\Users\\Genshin\\Desktop\\9\\1246578027-1-192.mp4'  
cap = cv2.VideoCapture(video_path)  
  
# 检查视频是否成功打开  
if not cap.isOpened():  
    print("Error: Could not open video.")  
    exit()  
  
# 设置像素块大小  
block_size = 10  
  
# 读取文件夹中的图片并计算其平均颜色  
images_dir = 'C:\\Users\\Genshin\\Desktop\\8'  
image_files = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]  
image_colors = []  
image_arrays = []  # 存储调整大小后的图像数组  
  
for img_path in image_files:  
    img = cv2.imread(img_path)  
    img_resized = cv2.resize(img, (block_size, block_size))  # 使用OpenCV调整大小  
    avg_color = img_resized.mean(axis=(0, 1)).astype(np.float32)  
    image_colors.append(avg_color)  
    image_arrays.append(img_resized)  # 存储调整大小后的图像  
  
# 构建KD树  
tree = KDTree(np.array(image_colors))  
  
# 获取视频的总帧数、帧率和尺寸  
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  
fps = cap.get(cv2.CAP_PROP_FPS)  
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  
  
# 初始化输出视频写入器  
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
out_path = 'output_video.mp4'  
out = cv2.VideoWriter(out_path, fourcc, fps, (frame_width, frame_height))  
  
# 处理视频帧的函数  
def process_frame(frame_index, cap, tree, image_arrays, block_size):  
    ret, frame = cap.read()  
    if not ret:  
        return None  
      
    processed_frame = frame.copy()  
    for y in range(0, frame_height, block_size):  
        for x in range(0, frame_width, block_size):  
            block = frame[y:y+block_size, x:x+block_size]  
            block_color = block.mean(axis=(0, 1)).astype(np.float32).reshape(1, -1)  
              
            # 使用KD树进行颜色匹配  
            _, indices = tree.query(block_color, k=1)  
            closest_img_array = image_arrays[indices[0][0]]  
              
            # 替换像素块  
            processed_frame[y:y+block_size, x:x+block_size] = closest_img_array  
      
    return processed_frame  
  
# 使用ProcessPoolExecutor并行处理帧  
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor, tqdm(total=frame_count, desc="Processing frames", unit="frame") as pbar:  
    future_to_frame = {executor.submit(process_frame, i, cap, tree, image_arrays, block_size): i for i in range(frame_count)}  
    for future in as_completed(future_to_frame):  
        frame_index = future_to_frame[future]  
        result = future.result()  
        if result is not None:  
            out.write(result)  
        pbar.update(1)  
  
# 释放资源  
out.release()  
cap.release()
