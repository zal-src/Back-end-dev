import cv2
import pytesseract
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# 🔧 (เฉพาะ Windows) ตั้ง path ของ tesseract.exe หากยังไม่ได้ตั้ง
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ------------------------- ฟังก์ชันหลัก -----------------------------

def correct_image_orientation(img):
    """หมุนภาพให้ถูกแนวโดยอัตโนมัติ"""
    try:
        osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
        angle = osd.get("rotate", 0)
        print(f"[INFO] Image angle detected: {angle} degrees")

        if angle == 180:
            print("[ACTION] Rotating 180 degrees to correct upside-down image.")
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 90:
            print("[ACTION] Rotating 270 degrees (90 CW)")
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 270:
            print("[ACTION] Rotating 90 degrees (270 CW)")
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        else:
            print("[ACTION] No rotation needed.")
    except Exception as e:
        print("[WARNING] Could not determine orientation. Skipping rotation.", e)
    return img


def detect_student_id(region, num_digits=10, choices=10, top_offset=140):
    """ตรวจรหัสนักศึกษาจากกระดาษคำตอบโดยนับพิกเซลดำ"""
    h, w = region.shape
    usable_h = h - top_offset
    col_w = w // num_digits
    row_h = usable_h // choices
    student_id = ""

    for d in range(num_digits):
        col = region[top_offset:top_offset + usable_h, d * col_w:(d + 1) * col_w]
        scores = []
        for r in range(choices):
            y1, y2 = r * row_h, (r + 1) * row_h
            cell = col[y1:y2, :]
            scores.append(cv2.countNonZero(cell))
        scores = np.array(scores)
        digit = "?" if scores.max() < 50 else str(scores.argmax())
        student_id += digit
    return student_id


# ------------------------- ส่วน GUI -----------------------------

class OMRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OMR Student ID Reader (with Debug)")
        self.root.geometry("800x700")
        self.image_path = None
        self.student_id = None

        # ปุ่มเลือกภาพ
        self.btn_load = tk.Button(root, text="📂 เลือกภาพ", command=self.load_image, font=("TH Sarabun New", 18))
        self.btn_load.pack(pady=10)

        # แสดงภาพที่โหลด
        self.label_image = tk.Label(root)
        self.label_image.pack(pady=10)

        # ปุ่มประมวลผล
        self.btn_process = tk.Button(root, text="🔍 ตรวจรหัสนักศึกษา", command=self.process_image, font=("TH Sarabun New", 18))
        self.btn_process.pack(pady=10)

        # แสดงผลรหัส
        self.label_student_id = tk.Label(root, text="📘 Student ID: (ยังไม่ตรวจ)", font=("TH Sarabun New", 18))
        self.label_student_id.pack(pady=20)

    def load_image(self):
        """เลือกและแสดงภาพ"""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
        if not file_path:
            return
        self.image_path = file_path

        # แสดงภาพใน GUI
        img = Image.open(file_path)
        img.thumbnail((600, 400))
        img_tk = ImageTk.PhotoImage(img)
        self.label_image.configure(image=img_tk)
        self.label_image.image = img_tk

        self.label_student_id.config(text="📘 Student ID: (พร้อมตรวจ)")

    def process_image(self):
        """ตรวจรหัสนักศึกษา + บันทึก debug"""
        if not self.image_path:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกภาพก่อน!")
            return

        img = cv2.imread(self.image_path)
        if img is None:
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบภาพ!")
            return

        # ✅ หมุนภาพอัตโนมัติ
        img = correct_image_orientation(img)

        # 🔍 แปลงและ threshold
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # 💾 บันทึก debug
        cv2.imwrite("debug_full_threshold.jpg", th)

        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            boxes.append((area, x, y, w, h))
        boxes = sorted(boxes, key=lambda x: x[0], reverse=True)

        sid = ""
        if len(boxes) >= 2:
            _, x, y, w, h = boxes[1]

            # 🟩 DEBUG: วาดกรอบ
            debug_img = img.copy()
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.imwrite("debug_id_box.jpg", debug_img)

            # ✂️ ครอป
            id_crop = img[y:y + h, x:x + w]
            cv2.imwrite("debug_id_crop.jpg", id_crop)

            gray_id = cv2.cvtColor(id_crop, cv2.COLOR_BGR2GRAY)
            blur_id = cv2.GaussianBlur(gray_id, (5, 5), 0)
            thresh_id = cv2.threshold(blur_id, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            cv2.imwrite("debug_id_thresh.jpg", thresh_id)

            # 🔢 อ่านรหัสนักศึกษา
            sid = detect_student_id(thresh_id)
            self.student_id = sid
            print("📌 รหัสนักศึกษา:", sid)
            self.label_student_id.config(text=f"📘 Student ID: {sid}")

        else:
            sid = "❌ ไม่พบกล่องรหัสนักศึกษา"
            print(sid)
            self.label_student_id.config(text=sid)

        messagebox.showinfo("ผลการตรวจ", f"รหัสนักศึกษา: {sid}")


# ------------------------- เริ่มโปรแกรม -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = OMRApp(root)
    root.mainloop()
