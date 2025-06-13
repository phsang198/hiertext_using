import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from recognize import recognize

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

icon_path = os.path.join(base_path, 'icon.ico')

class ObjectRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCRS")
        self.root.geometry("1100x600")
        self.root.configure(bg="#f0f0f0")

        # Main Frame
        main_frame = tk.Frame(root, bg="#d9d9d9", bd=2, relief=tk.RIDGE)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,0))

        # Left frame (Input Image)
        self.input_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.SOLID, width=500, height=500)
        self.input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        self.input_frame.pack_propagate(False)
        self.input_canvas = tk.Canvas(self.input_frame, bg="#ffffff", highlightthickness=0)
        self.input_canvas.pack(fill=tk.BOTH, expand=True)
        self.input_canvas.create_text(250, 250, text="Input Image", fill="gray", font=("Arial", 14), tags="label")

        # Right frame (Result Image)
        self.result_frame = tk.Frame(main_frame, bg="#ffffff", bd=2, relief=tk.SOLID, width=500, height=500)
        self.result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        self.result_frame.pack_propagate(False)
        self.result_canvas = tk.Canvas(self.result_frame, bg="#ffffff", highlightthickness=0)
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
        self.result_canvas.create_text(250, 250, text="Result Image", fill="gray", font=("Arial", 14), tags="label")

        # Bottom Frame for Buttons (outside main_frame, below both image frames)
        button_frame = tk.Frame(root, bg="#f0f0f0")
        button_frame.pack(side=tk.BOTTOM, pady=(0, 8))

        # Open File Button (left)
        self.open_button = tk.Button(button_frame, text="Open Image", font=("Arial", 11, "bold"), fg="white", bg="#007BFF",
                                    activebackground="#0056b3", relief=tk.RAISED, width=18, command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=40, pady=10)

        # Recognize Button (right)
        self.recognize_button = tk.Button(button_frame, text="Recognize", font=("Arial", 11, "bold"), fg="white", bg="#28a745",
                                          activebackground="#1e7e34", relief=tk.RAISED, width=18, command=self.recognize_objects)
        self.recognize_button.pack(side=tk.LEFT, padx=40, pady=10)

        # Initialize variables
        self.current_image_path = None
        self.input_photo_image = None
        self.result_photo_image = None

        # Thêm biến zoom và pan cho input/result
        self.input_zoom = 1.0
        self.input_pan = [0, 0]
        self.input_img_orig = None
        self.input_img_disp = None
        self.input_img_id = None
        self.input_drag_data = None

        self.result_zoom = 1.0
        self.result_pan = [0, 0]
        self.result_img_orig = None
        self.result_img_disp = None
        self.result_img_id = None
        self.result_drag_data = None

        # Bind sự kiện zoom/pan cho input
        self.input_canvas.bind('<ButtonPress-1>', self.start_input_pan)
        self.input_canvas.bind('<B1-Motion>', self.do_input_pan)
        self.input_canvas.bind('<MouseWheel>', self.input_zoom_event)
        self.input_canvas.bind('<Configure>', lambda e: self.update_input_canvas())
        # Bind sự kiện zoom/pan cho result
        self.result_canvas.bind('<ButtonPress-1>', self.start_result_pan)
        self.result_canvas.bind('<B1-Motion>', self.do_result_pan)
        self.result_canvas.bind('<MouseWheel>', self.result_zoom_event)
        self.result_canvas.bind('<Configure>', lambda e: self.update_result_canvas())

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.current_image_path = file_path
            self.load_input_image(file_path)
            self.clear_result_image()

    def load_input_image(self, image_path):
        try:
            image = Image.open(image_path)
            self.input_img_orig = image.copy()
            self.input_zoom = 1.0
            self.input_pan = [0, 0]
            self.update_input_canvas()
            filename = os.path.basename(image_path)
            self.root.title(f"OCRS - {filename}")
        except Exception as e:
            self.input_canvas.delete("all")
            self.input_canvas.create_text(250, 250, text=f"Error loading image: {e}", fill="red", font=("Arial", 14), tags="label")

    def update_input_canvas(self):
        self.input_canvas.delete("all")
        if self.input_img_orig is None:
            self.input_canvas.create_text(250, 250, text="Input Image", fill="gray", font=("Arial", 14), tags="label")
            return
        w, h = self.input_img_orig.size
        canvas_w = self.input_canvas.winfo_width()
        canvas_h = self.input_canvas.winfo_height()
        # Responsive: Nếu canvas thay đổi kích thước, scale lại nếu đang ở trạng thái fit
        if self.input_pan == [0, 0] or getattr(self, '_input_fit', True):
            scale_w = canvas_w / w
            scale_h = canvas_h / h
            fit_zoom = min(scale_w, scale_h, 1.0)
            self.input_zoom = fit_zoom
            self.input_pan = [canvas_w // 2, canvas_h // 2]
            self._input_fit = True
        pan_x, pan_y = self.input_pan
        zoom = self.input_zoom
        new_w, new_h = int(w * zoom), int(h * zoom)
        img = self.input_img_orig.resize((new_w, new_h), Image.LANCZOS)
        self.input_img_disp = ImageTk.PhotoImage(img)
        self.input_img_id = self.input_canvas.create_image(pan_x, pan_y, anchor=tk.CENTER, image=self.input_img_disp)

    def start_input_pan(self, event):
        self.input_drag_data = (event.x, event.y, self.input_pan[0], self.input_pan[1])

    def do_input_pan(self, event):
        if self.input_drag_data:
            x0, y0, pan_x0, pan_y0 = self.input_drag_data
            dx = event.x - x0
            dy = event.y - y0
            self.input_pan = [pan_x0 + dx, pan_y0 + dy]
            self._input_fit = False  # Đã pan thủ công thì không auto fit nữa
            self.update_input_canvas()

    def input_zoom_event(self, event):
        if self.input_img_orig is None:
            return
        factor = 1.1 if event.delta > 0 else 0.9
        self.input_zoom *= factor
        self._input_fit = False  # Đã zoom thủ công thì không auto fit nữa
        self.update_input_canvas()

    def clear_result_image(self):
        self.result_canvas.delete("all")
        self.result_canvas.create_text(250, 250, text="Result Image", fill="gray", font=("Arial", 14), tags="label")
        self.result_img_orig = None
        self.result_img_disp = None
        self.result_img_id = None
        self.result_zoom = 1.0
        self.result_pan = [0, 0]

    def recognize_objects(self):
        if not self.current_image_path:
            messagebox.showinfo("Info", "Please open an image file first.")
            return
        try:
            # Call the function from recognize.py
            results = recognize(self.current_image_path)
            # Nếu kết quả là đường dẫn ảnh kết quả, hiển thị ảnh đó
            if isinstance(results, str) and os.path.isfile(results):
                self.load_result_image(results)
            else:
                # Nếu trả về text, hiển thị text lên ảnh kết quả
                self.result_canvas.create_text(250, 250, text=str(results), fill="black", font=("Arial", 12), tags="label")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to recognize objects: {e}")

    def load_result_image(self, image_path):
        try:
            image = Image.open(image_path)
            self.result_img_orig = image.copy()
            self.result_zoom = 1.0
            self.result_pan = [0, 0]
            self.update_result_canvas()
        except Exception as e:
            self.result_canvas.delete("all")
            self.result_canvas.create_text(250, 250, text=f"Error loading result image: {e}", fill="red", font=("Arial", 14), tags="label")

    def update_result_canvas(self):
        self.result_canvas.delete("all")
        if self.result_img_orig is None:
            self.result_canvas.create_text(250, 250, text="Result Image", fill="gray", font=("Arial", 14), tags="label")
            return
        w, h = self.result_img_orig.size
        canvas_w = self.result_canvas.winfo_width()
        canvas_h = self.result_canvas.winfo_height()
        if self.result_pan == [0, 0] or getattr(self, '_result_fit', True):
            scale_w = canvas_w / w
            scale_h = canvas_h / h
            fit_zoom = min(scale_w, scale_h, 1.0)
            self.result_zoom = fit_zoom
            self.result_pan = [canvas_w // 2, canvas_h // 2]
            self._result_fit = True
        pan_x, pan_y = self.result_pan
        zoom = self.result_zoom
        new_w, new_h = int(w * zoom), int(h * zoom)
        img = self.result_img_orig.resize((new_w, new_h), Image.LANCZOS)
        self.result_img_disp = ImageTk.PhotoImage(img)
        self.result_img_id = self.result_canvas.create_image(pan_x, pan_y, anchor=tk.CENTER, image=self.result_img_disp)

    def start_result_pan(self, event):
        self.result_drag_data = (event.x, event.y, self.result_pan[0], self.result_pan[1])

    def do_result_pan(self, event):
        if self.result_drag_data:
            x0, y0, pan_x0, pan_y0 = self.result_drag_data
            dx = event.x - x0
            dy = event.y - y0
            self.result_pan = [pan_x0 + dx, pan_y0 + dy]
            self._result_fit = False
            self.update_result_canvas()

    def result_zoom_event(self, event):
        if self.result_img_orig is None:
            return
        factor = 1.1 if event.delta > 0 else 0.9
        self.result_zoom *= factor
        self._result_fit = False
        self.update_result_canvas()

def main():
    root = tk.Tk()
    app = ObjectRecognitionApp(root)
    root.iconbitmap(icon_path)
    root.mainloop()

if __name__ == "__main__":
    main()
