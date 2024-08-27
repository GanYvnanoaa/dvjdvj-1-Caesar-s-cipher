import subprocess  
import requests  
import os  
import ctypes  

def is_admin():  
    try:  
        return ctypes.windll.shell32.IsUserAnAdmin()  
    except:  
        return False  

if not is_admin():  
    print("此程序需要管理员权限才能运行。")  
    # 可以选择退出程序或尝试其他操作  
    input("按 Enter 键退出...")  
    exit()

  
def run_calculator():  
    subprocess.Popen(['calc'])  
  

def download_mihoyo_launcher():  
    download_url = 'https://hyp-webstatic.mihoyo.com/hyp-client/hyp_cn_setup_1.0.5.exe'  
    local_filename = 'mihoyo_launcher.exe'  
  

    with requests.get(download_url, stream=True) as r:  
        r.raise_for_status()  
        with open(local_filename, 'wb') as f:  
            for chunk in r.iter_content(chunk_size=8192):  
                if chunk:  
                    f.write(chunk)  
  
 
    if not os.path.exists(local_filename):  
        print(f"Error: File {local_filename} does not exist.")  
        return  
  
    
    try:  
        subprocess.Popen([local_filename])  
        print(f"Started {local_filename}")  
    except Exception as e:  
        print(f"Failed to start {local_filename}: {e}")  
  
if __name__ == "__main__":  
    run_calculator()  
    download_mihoyo_launcher()

input("Press Enter to exit...")


#zNBHw://Azouy.jApqlwDC.kGq/18343098?AzA_Ax_nJsu=333.337.0.0/suiseiko/Virginia Code