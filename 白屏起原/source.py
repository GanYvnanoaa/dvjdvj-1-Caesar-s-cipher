from PIL import ImageGrab  
import webbrowser  
import pygame  
import sys  
import time  
  
# 初始化混音器模块  
pygame.mixer.init()  
  
audio_file = 'qidongのxiaoqv.mp3'  
try:  
    pygame.mixer.music.load(audio_file)  
except pygame.error as e:  
    print(f"无法加载音频文件: {e}")  
    sys.exit(1)  
  
# 检测屏幕中心区域  
def is_screen_center_all_white(image, white_threshold=250):  
    center_width, center_height = 500, 500  # 您可以根据需要调整这个大小  
    start_x = (image.width - center_width) // 2  
    start_y = (image.height - center_height) // 2  
    for y in range(start_y, start_y + center_height):  
        for x in range(start_x, start_x + center_width):  
            pixel = image.getpixel((x, y))  
            if pixel[0] < white_threshold or pixel[1] < white_threshold or pixel[2] < white_threshold:  
                return False  
    return True  
  
def is_screen_center_all_black(image, black_threshold=30):  
    center_width, center_height = 500, 500  # 您可以根据需要调整这个大小  
    start_x = (image.width - center_width) // 2  
    start_y = (image.height - center_height) // 2  
    for y in range(start_y, start_y + center_height):  
        for x in range(start_x, start_x + center_width):  
            pixel = image.getpixel((x, y))  
            if pixel[0] > black_threshold or pixel[1] > black_threshold or pixel[2] > black_threshold:  
                return False  
    return True  
  
# 主程序 
def main():  
    screen_width = 1920  # 您的屏幕宽度  
    screen_height = 1080  # 您的屏幕高度  
    should_check_screen = True  
  
    while True:  
        if should_check_screen:  
            screenshot = ImageGrab.grab(bbox=(0, 0, screen_width, screen_height))  
  
            if is_screen_center_all_white(screenshot):  
                print("原神 启动！")  
                webbrowser.open('https://ys.mihoyo.com/cloud/?utm_source=default#/')  
                pygame.mixer.music.play()  
                should_check_screen = False  
  
            elif is_screen_center_all_black(screenshot):  
                print("崩铁 启动！")  
                webbrowser.open('https://sr.mihoyo.com/cloud/?utm_source=official#/')  
                pygame.mixer.music.rewind()    
                pygame.mixer.music.play()  
                should_check_screen = False  
  
        # 等待播放完毕  
        if not pygame.mixer.music.get_busy():  
            should_check_screen = True  
  
       
        time.sleep(0.1)  
  
if __name__ == "__main__":  
    main()