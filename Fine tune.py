import cv2  
import numpy as np  
import os  
import pygame  
import sys  
import time  
  
pygame.mixer.init()  
  
audio_file = '1246578027-1-192.mp3'  
try:  
    pygame.mixer.music.load(audio_file)  
except pygame.error as e:  
    print(f"无法加载音频文件: {e}")  
    sys.exit(1)  
  
ASCII_CHARS = [' ', '.', ',', ':', ';', '+', '*', '?', '%', 'S', '#', '&']  
  
def resize_image(image, new_width=100):  
    height, width = image.shape[:2]  
    aspect_ratio = height / width  
    new_height = int(aspect_ratio * new_width * 0.55)  
    resized_image = cv2.resize(image, (new_width, new_height))  
    return resized_image  
  
def grayify(image):  
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
  
def pixels_to_ascii(image):  
    ascii_str = ""  
    for pixel_value in image:  
        ascii_str += ASCII_CHARS[pixel_value // 25]  
    return ascii_str  
  
def image_to_ascii(image, new_width=100):  
    image = resize_image(image, new_width)  
    image = grayify(image)  
    ascii_image = "\n".join([pixels_to_ascii(row) for row in image])  
    return ascii_image  
  
def play_video_ascii(video_path, new_width=100):  
    cap = cv2.VideoCapture(video_path)  
    if not cap.isOpened():  
        print("Error: 无法打开视频文件")  
        return  
  
    pygame.mixer.music.play()  # 只在开始时播放音频  
    last_ascii_frame = None  
    last_change_time = time.time()  
    no_change_threshold = 6  # 秒  
  
    try:  
        while True:  
            ret, frame = cap.read()  
            if not ret:  
                break  
            ascii_frame = image_to_ascii(frame, new_width)  
  
            # 检查是否有变化  
            if last_ascii_frame is not None and ascii_frame == last_ascii_frame:  
                current_time = time.time()  
                if current_time - last_change_time >= no_change_threshold:  
                    print("")  
                    break  
            else:  
                last_change_time = time.time()  
  
            last_ascii_frame = ascii_frame  
  
            os.system('cls' if os.name == 'nt' else 'clear')  
            print(ascii_frame)  
            cv2.waitKey(int(100000/ 61000000))  # 设置为60 fps  但为被保证音画同步暴力拉高帧率
    except KeyboardInterrupt:  
        pass  
    finally:  
        cap.release()  
        pygame.mixer.music.stop()  # 确保音频在退出时停止播放  
  
if __name__ == "__main__":  
    video_path = "1246578027-1-192.mp4"  
    play_video_ascii(video_path, new_width=100)  
    while pygame.mixer.music.get_busy():  
        pygame.time.Clock().tick(10)  # 保持主循环运行直到音频播放完毕 