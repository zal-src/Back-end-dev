
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import pytesseract
# ----------------------------
# เรียกใช้ฟังก์ชัน OMR (คัดลอกจากของคุณ)
# ----------------------------
# ตั้ง path ของ tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

box_scale = 0.8
global_box_size = None
FIXED_START_POS = {
    "x": 24,
    "y": 40,
    "radius": 20
}

# ----------------------------
# ฟังก์ชันตรวจและหมุนภาพ
# ----------------------------
def correct_image_orientation(img):
    try:
        osd = pytesseract.image_to_osd(img, output_type=pytesseract.Output.DICT)
        angle = osd.get("rotate", 0)
        if angle == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif angle == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    except Exception as e:
        print("[WARNING] Could not determine orientation:", e)
    return img

def detect_student_id(region, num_digits=10, choices=10, top_offset=140):
    h, w = region.shape
    usable_h = max(0, h - top_offset)
    col_w = max(1, w // num_digits)
    row_h = max(1, usable_h // choices)
    student_id = ""
    for d in range(num_digits):
        col = region[top_offset:top_offset + usable_h, d * col_w:(d + 1) * col_w]
        scores = []
        for r in range(choices):
            y1, y2 = r * row_h, (r + 1) * row_h
            cell = col[y1:y2, :]
            scores.append(cv2.countNonZero(cell))
        scores = np.array(scores)
        digit = "?" if scores.size == 0 or scores.max() < 50 else str(int(scores.argmax()))
        student_id += digit
    return student_id


def find_markers(image, min_area=200):
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    zone_x_min = w * 0.95
    zone_x_max = w
    zone_y_min = 0
    zone_y_max = h * 0.05
    markers = []

    for c in cnts:
        x, y, wc, hc = cv2.boundingRect(c)
        area = wc * hc
        if area > min_area:
            cx, cy = x + wc // 2, y + hc // 2
            if zone_x_min <= cx <= zone_x_max and zone_y_min <= cy <= zone_y_max:
                markers.append((cx, cy))
    return markers

def fix_orientation(image):
    h, w = image.shape[:2]
    target = None
    for i in range(4):
        markers = find_markers(image)
        if not markers:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            continue
        target = max(markers, key=lambda m: (m[0], -m[1]))
        cx, cy = target
        if cx > w * 0.95 and cy < h * 0.05:
            return image, target
        else:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image, target

def deskew_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                            minLineLength=100, maxLineGap=10)
    if lines is None:
        return image

    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if -45 < angle < 45:
            angles.append(angle)

    if len(angles) == 0:
        return image

    median_angle = np.median(angles)
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), median_angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REPLICATE)
    return deskewed



def find_first_circle_center_and_radius(col_img):
    circles = cv2.HoughCircles(col_img, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                               param1=50, param2=30, minRadius=5, maxRadius=30)
    if circles is not None:
        circles = np.uint16(np.around(circles[0, :]))
        circles_sorted = sorted(circles, key=lambda c: (c[1], c[0]))
        return (int(circles_sorted[0][0]), int(circles_sorted[0][1]), int(circles_sorted[0][2]))
    return None

def mark_boxes_grid(col_img, rows=35, cols=5, spacing_col=5, spacing_row=None,
                    debug_name="debug_col.jpg", box_scale=0.8, use_same_box_size=False,
                    start_pos=None):
    global global_box_size
    # col_img expected grayscale (0..255)
    if len(col_img.shape) == 3:
        col_img_gray = cv2.cvtColor(col_img, cv2.COLOR_BGR2GRAY)
    else:
        col_img_gray = col_img
    col_img_color = cv2.cvtColor(col_img_gray, cv2.COLOR_GRAY2BGR)

    if start_pos is not None:
        x_start = start_pos["x"]
        y_start = start_pos["y"]
        radius = start_pos["radius"]
    elif FIXED_START_POS is not None:
        x_start = FIXED_START_POS["x"]
        y_start = FIXED_START_POS["y"]
        radius = FIXED_START_POS["radius"]
    else:
        result = find_first_circle_center_and_radius(col_img_gray)
        if result is None:
            return []
        x_start, y_start, radius = result

    radius = int(radius * box_scale)
    box_size = radius * 2

    if use_same_box_size and global_box_size is not None:
        box_size = global_box_size
        radius = box_size // 2
    else:
        global_box_size = box_size

    if spacing_row is None:
        spacing_row = box_size + spacing_col

    filled_boxes = []
    answer_map = {0:'1',1:'2',2:'3',3:'4',4:'5'}

    for row in range(rows):
        selected_list = []
        for col in range(cols):
            x = int(x_start + col*(box_size+spacing_col))
            y = int(y_start + row*spacing_row)
            y1, y2 = max(0,y-radius), min(col_img_gray.shape[0], y+radius)
            x1, x2 = max(0,x-radius), min(col_img_gray.shape[1], x+radius)
            roi = col_img_gray[y1:y2, x1:x2]
            if roi.size >0:
                fill_ratio = np.sum(roi>127)/roi.size
                if fill_ratio >0.4:
                    selected_list.append(answer_map[col])
        if len(selected_list)==1:
            filled_boxes.append(selected_list[0])
        else:
            filled_boxes.append(None)

    # Optionally save debug image if needed (commented out by default)
    # cv2.imwrite(debug_name, col_img_color)
    return filled_boxes

def find_corners_by_hough(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    if lines is None:
        return None

    verticals, horizontals = [],[]
    for x1,y1,x2,y2 in lines[:,0]:
        if abs(x1-x2)<20:
            verticals.append(x1)
        elif abs(y1-y2)<20:
            horizontals.append(y1)

    if not verticals or not horizontals:
        return None

    x_left, x_right = min(verticals), max(verticals)
    y_top, y_bottom = min(horizontals), max(horizontals)

    return np.array([(x_left,y_top),(x_right,y_top),(x_right,y_bottom),(x_left,y_bottom)],dtype="float32")

def crop_answer_zone(image_path, spacing_col=5, spacing_row1=37, spacing_row2=None, debug=False):
    img = cv2.imread(image_path)
    if img is None:
        return None

    img = cv2.resize(img, (1654, 2339))
    img, marker = fix_orientation(img)
    img = deskew_image(img)

    h, w = img.shape[:2]
    roi_ans = img[int(h*0.329):int(h*0.9), int(w*0.01):int(w*0.95)]

    corners_ans = find_corners_by_hough(roi_ans)
    if corners_ans is None:
        return None

    dst = np.array([[0,0],[1400,0],[1400,2000],[0,2000]], dtype="float32")
    M = cv2.getPerspectiveTransform(corners_ans,dst)
    warp_ans = cv2.warpPerspective(roi_ans,M,(1400,2000))

    gray_ans = cv2.cvtColor(warp_ans, cv2.COLOR_BGR2GRAY)
    blur_ans = cv2.GaussianBlur(gray_ans,(5,5),0)
    thresh_ans = cv2.threshold(blur_ans,0,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    col1 = thresh_ans[120:2335, 40:240]
    col2 = thresh_ans[120:2335, 270:475]

    if debug:
        # original behavior: return marked answers and save debug images
        col1_ans = mark_boxes_grid(col1, rows=35, cols=5, spacing_col=spacing_col,
                                   spacing_row=spacing_row1, debug_name="debug_col1.jpg",
                                   box_scale=box_scale, use_same_box_size=False)
        col2_ans = mark_boxes_grid(col2, rows=35, cols=5, spacing_col=spacing_col,
                                   spacing_row=spacing_row2, debug_name="debug_col2.jpg",
                                   box_scale=box_scale, use_same_box_size=True,
                                   start_pos=FIXED_START_POS)
        all_answers = col1_ans + col2_ans
        return all_answers

    # If not debug: return raw columns for later processing (no debug files)
    return col1, col2

def check_answers(detected_answers, correct_answers):
    total = len(correct_answers)
    score = 0
    for i in range(total):
        detected = detected_answers[i] if i < len(detected_answers) else None
        if detected == correct_answers[i]:
            score += 1
    return score

# ----------------------------
# GUI
# ----------------------------
class SimpleOMRGui:
    def __init__(self, root):
        self.root = root
        self.root.title("OMR Simple with Student ID")
        self.root.geometry("600x300")
        self.image_path = None
        self.correct_answers = []
        self.detected_answers = None
        self.student_id = None

        top = tk.Frame(root, pady=10)
        top.pack(fill=tk.X)

        tk.Button(top, text="เลือกภาพ OMR", width=15, command=self.select_image).pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="เลือก Answer.txt", width=15, command=self.select_answer_file).pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="เริ่มตรวจ", width=12, command=self.run_process).pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="บันทึกรายงาน", width=12, command=self.save_report).pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="ออก", width=8, command=root.quit).pack(side=tk.RIGHT, padx=8)

        mid = tk.Frame(root, pady=12)
        mid.pack(fill=tk.X)
        tk.Label(mid, text="Student ID:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=8)
        self.lbl_sid = tk.Label(mid, text="-", font=("Arial", 12, "bold"))
        self.lbl_sid.grid(row=0, column=1, sticky="w")
        tk.Label(mid, text="Score:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.lbl_score = tk.Label(mid, text="-", font=("Arial", 12, "bold"))
        self.lbl_score.grid(row=1, column=1, sticky="w")
        self.lbl_info = tk.Label(root, text="สถานะ: พร้อม", anchor="w")
        self.lbl_info.pack(fill=tk.X, padx=8, pady=8)

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if not path:
            return
        self.image_path = path
        self.lbl_info.config(text=f"สถานะ: โหลดภาพ {os.path.basename(path)} แล้ว")
        self.lbl_sid.config(text="-")
        self.lbl_score.config(text="-")

    def select_answer_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files","*.*")])
        if not path:
            return
        try:
            self.correct_answers = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    ans = line.strip().upper()
                    if ans:
                        self.correct_answers.append(ans)
            self.lbl_info.config(text=f"สถานะ: โหลดเฉลย ({len(self.correct_answers)} ข้อ)")
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถโหลดไฟล์คำตอบ: {e}")

    def run_process(self):
        if not self.image_path:
            messagebox.showwarning("Warning", "กรุณาเลือกภาพก่อน")
            return
        self.lbl_info.config(text="สถานะ: กำลังประมวลผล...")
        self.root.update_idletasks()
        try:
            img = cv2.imread(self.image_path)
            img = correct_image_orientation(img)
            col1, col2 = crop_answer_zone(self.image_path, spacing_col=5, spacing_row1=53, spacing_row2=53, debug=False)
            col1_ans = mark_boxes_grid(col1, rows=35, cols=5, spacing_col=5, spacing_row=53,
                                      debug_name="debug_col1.jpg", box_scale=box_scale, use_same_box_size=False)
            col2_ans = mark_boxes_grid(col2, rows=35, cols=5, spacing_col=5, spacing_row=53,
                                      debug_name="debug_col2.jpg", box_scale=box_scale, use_same_box_size=True,
                                      start_pos=FIXED_START_POS)
            self.detected_answers = (col1_ans or []) + (col2_ans or [])
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, th = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = sorted([(w*h,x,y,w,h) for (x,y,w,h) in [cv2.boundingRect(c) for c in contours]], reverse=True)
            if len(boxes) >= 2:
                _, x, y, w, h = boxes[1]
                id_crop = img[y:y+h, x:x+w]
                gray_id = cv2.cvtColor(id_crop, cv2.COLOR_BGR2GRAY)
                blur_id = cv2.GaussianBlur(gray_id, (5, 5), 0)
                thresh_id = cv2.threshold(blur_id, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                self.student_id = detect_student_id(thresh_id)
            else:
                self.student_id = "ไม่พบกล่องรหัส"
            score_text = "-"
            if self.correct_answers:
                score = check_answers(self.detected_answers, self.correct_answers)
                score_text = f"{score} / {len(self.correct_answers)}"
            self.lbl_sid.config(text=str(self.student_id))
            self.lbl_score.config(text=score_text)
            self.lbl_info.config(text="สถานะ: เสร็จสิ้น")
        except Exception as e:
            messagebox.showerror("Exception", str(e))
            self.lbl_info.config(text=f"สถานะ: เกิดข้อผิดพลาด: {e}")

    def save_report(self):
        if self.detected_answers is None and self.student_id is None:
            messagebox.showwarning("Warning", "ยังไม่มีข้อมูล ให้รันตรวจก่อน")
            return
        out = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file","*.txt")])
        if not out:
            return
        try:
            with open(out, "w", encoding="utf-8") as f:
                f.write("OMR Simple Report\n")
                f.write("=================\n")
                f.write(f"Image: {os.path.basename(self.image_path) if self.image_path else '-'}\n")
                f.write(f"Student ID: {self.student_id if self.student_id else '-'}\n")
                if self.detected_answers:
                    f.write("Detected answers:\n")
                    for i,a in enumerate(self.detected_answers,1):
                        f.write(f"{i}: {a}\n")
                if self.correct_answers:
                    s = check_answers(self.detected_answers, self.correct_answers)
                    f.write(f"\nScore: {s}/{len(self.correct_answers)}\n")
            messagebox.showinfo("Saved", f"บันทึกรายงานแล้ว: {out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    app = SimpleOMRGui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
