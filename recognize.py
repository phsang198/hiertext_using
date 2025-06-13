import os
import subprocess

# Đường dẫn thư mục tool cùng cấp với file hiện tại
exepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tool/ocrs')


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

    # Đường dẫn file kết quả
    txt_path = os.path.join(output_dir, 'content.txt')
    json_path = os.path.join(output_dir, 'content.json')
    png_path = os.path.join(output_dir, 'annotated.png')

    # Lệnh ocrs
    cmd_txt = f'ocrs "{imagepath}" -o "{txt_path}"'
    cmd_json = f'ocrs "{imagepath}" --json -o "{json_path}"'
    cmd_png = f'ocrs "{imagepath}" --png -o "{png_path}"'

    # Chạy 3 lệnh song song và thu kết quả
    check = execute_command(cmd_txt) & execute_command(cmd_json) & execute_command(cmd_png)
    if not check:
        return "Error executing OCR commands."
    return png_path

# print(recognize("F:\\OutSource\\CHK34\\Intel DA\\DEMO\\image\\input\\img4.png"))