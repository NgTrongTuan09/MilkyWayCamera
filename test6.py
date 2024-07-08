import subprocess
import os
import time
import tkinter as tk
from PIL import Image, ImageTk
import threading
import cv2

# Đường dẫn đầy đủ đến adb
adb_path = r'D:\project_milkyway\platform-tools\adb.exe'

def run_adb_command(command):
    try:
        process = subprocess.Popen(f'{adb_path} {command}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f"Lệnh thất bại: {stderr.decode('utf-8')}")
        return stdout.decode('utf-8')
    except FileNotFoundError:
        raise Exception("ADB không được tìm thấy. Vui lòng kiểm tra lại đường dẫn và cài đặt ADB.")

def tap_screen(x, y):
    try:
        run_adb_command(f'shell input tap {x} {y}')
        display_status(f"Đã nhấn vào tọa độ ({x}, {y}) trên màn hình.")
    except Exception as e:
        display_status(f"Lỗi: {e}")

def pull_latest_photo():
    try:
        os.makedirs('images', exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        # Kéo ảnh mới nhất từ thiết bị về máy tính
        output = run_adb_command('shell "ls -t /sdcard/DCIM/Camera/*.jpg"')
        latest_photo = output.splitlines()[0].strip()
        run_adb_command(f'pull {latest_photo} images/{timestamp}.jpg')
        display_status("Đã lưu ảnh mới nhất vào máy tính.")
        
        # Xóa ảnh trên thiết bị sau khi kéo về máy tính
        run_adb_command(f'shell rm {latest_photo}')
        display_status("Đã xóa ảnh trên thiết bị.")
        
        return f'images/{timestamp}.jpg'
    except Exception as e:
        print(f"Lỗi: {e}")

def capture_photos():
    try:
        global capture_flag
        while capture_flag:
            tap_screen(550, 1990)
            time.sleep(16.4)
            image_path = pull_latest_photo()
            if image_path:
                display_image(image_path)
                image_paths.append(image_path)
                update_photo_count()  # Cập nhật số lượng ảnh đã chụp
    except KeyboardInterrupt:
        display_status("Đã dừng chụp ảnh theo lịch trình.")

def start_capture():
    global capture_flag
    capture_flag = True
    threading.Thread(target=capture_photos).start()

def stop_capture():
    global capture_flag
    capture_flag = False
    create_video_from_images()

def display_image(image_path):
    image = Image.open(image_path)
    image.thumbnail((600, 600))  # Tăng kích thước nhãn
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo

def create_video_from_images():
    try:
        os.makedirs('video', exist_ok=True)
        video_name = f"video/output_{time.strftime('%Y%m%d_%H%M%S')}.mp4"  # Đổi định dạng thành .mp4
        frame = cv2.imread(image_paths[0])
        height, width, layers = frame.shape
        video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width, height))  # Sử dụng định dạng mp4
        
        for image in image_paths:
            video.write(cv2.imread(image))
        
        cv2.destroyAllWindows()
        video.release()
        print(f"Đã tạo video và lưu tại {video_name}")
        display_status(f"Đã tạo video và lưu tại {video_name}")
    except Exception as e:
        print(f"Lỗi khi tạo video: {e}")
        display_status(f"Lỗi khi tạo video: {e}")

def display_status(message):
    current_status = status_label.cget("text")
    new_status = message + "\n" + current_status
    status_label.config(text=new_status)

def update_photo_count():
    photo_count_label.config(text=f"Số ảnh đã chụp: {len(image_paths)}")

# Tạo cửa sổ GUI
root = tk.Tk()
root.title("Ứng dụng chụp ảnh")
root.geometry("1000x650")  # Thay đổi kích thước cửa sổ

# Tạo khung cho hình ảnh
image_frame = tk.Frame(root)
image_frame.pack(side=tk.RIGHT, padx=20, pady=20)

# Tạo label để hiển thị hình ảnh
image_label = tk.Label(image_frame)
image_label.pack()

# Tạo khung cho các nút bấm và bộ đếm ảnh
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, padx=20, pady=20)

# Tạo các nút bấm với kích thước lớn hơn
button_font = ("Helvetica", 16)

start_button = tk.Button(button_frame, text="Start", command=start_capture, width=10, height=2, font=button_font)
start_button.pack(side=tk.LEFT, padx=(0, 10))

stop_button = tk.Button(button_frame, text="Stop", command=stop_capture, width=10, height=2, font=button_font)
stop_button.pack(side=tk.LEFT)

# Tạo label để hiển thị số lượng ảnh đã chụp
photo_count_label = tk.Label(button_frame, text="Số ảnh đã chụp: 0", font=("Helvetica", 16))
photo_count_label.pack(side=tk.LEFT, padx=(10, 0))

# Tạo label để hiển thị trạng thái
status_label = tk.Label(root, text="", anchor="w", justify="left")
status_label.config(font=("Helvetica", 15))
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))

# Khởi tạo biến cờ để kiểm soát việc chụp ảnh
capture_flag = False

# Khởi tạo danh sách lưu trữ đường dẫn hình ảnh
image_paths = []

# Chạy cửa sổ GUI
root.mainloop()
