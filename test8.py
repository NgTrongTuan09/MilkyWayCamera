import cv2
import os

# Đường dẫn đến folder chứa các ảnh
folder_path = 'D:\\project_milkyway\\test'
# Đường dẫn đến folder lưu video
video_output_path = 'D:\\project_milkyway\\video_ren\\output_video.mp4'

# Đọc danh sách các ảnh trong folder và sắp xếp theo thứ tự tên
image_files = sorted([img for img in os.listdir(folder_path) if img.endswith(".jpg") or img.endswith(".png")], key=lambda x: int(x.split('.')[0]))

# Đọc ảnh đầu tiên để lấy kích thước khung hình
first_image = cv2.imread(os.path.join(folder_path, image_files[0]))
height, width, layers = first_image.shape
size = (width, height)

# Tạo đối tượng VideoWriter
output_video = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'mp4v'), 8, size)

for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    frame = cv2.imread(image_path)

    # Resize frame nếu cần thiết
    frame = cv2.resize(frame, size)

    output_video.write(frame)

# Giải phóng đối tượng VideoWriter
output_video.release()

print(f"Video đã được tạo thành công tại {video_output_path}!")
