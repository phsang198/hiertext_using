import os
import subprocess
import sys

# Thêm hàm get base path giống như trong main.py
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Sử dụng base_path thay vì __file__
base_path = get_base_path()
exepath = os.path.join(base_path, 'tool', 'ocrs')

def execute_command(command):
    command = f'cd /D "{exepath}" && {command}'
    try:
        subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True,
            check=True
        )
        return True
    except Exception as e:
        print(f"Error executing command: {str(e)}\n")
        return False


def recognize(imagepath):
    # Lấy thư mục cha của ảnh đầu vào
    input_dir = os.path.dirname(os.path.abspath(imagepath))
    parent_dir = os.path.dirname(input_dir)
    # Lấy tên file không có phần mở rộng
    basename = os.path.basename(imagepath)
    name, _ = os.path.splitext(basename)
    # Đường dẫn thư mục output cùng cấp với input
    output_dir = os.path.join(parent_dir, 'output', name)
    os.makedirs(output_dir, exist_ok=True)

    txt_path = os.path.join(output_dir, 'content.txt')
    json_path = os.path.join(output_dir, 'content.json')
    png_path = os.path.join(output_dir, 'annotated.png')


    cmd_txt = f'ocrs "{imagepath}" -o "{txt_path}"'
    cmd_json = f'ocrs "{imagepath}" --json -o "{json_path}"'
    cmd_png = f'ocrs "{imagepath}" --png -o "{png_path}"'

    check = execute_command(cmd_txt) & execute_command(cmd_json) & execute_command(cmd_png)
    if not check:
        return "Error executing OCR commands."
    return png_path

print(recognize("F:\\OutSource\\CHK34\\Intel DA\\DEMO\\image\\input\\img4.png"))