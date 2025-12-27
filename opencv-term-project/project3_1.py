import cv2
import pytesseract
import numpy as np

# 🔧 (เฉพาะ Windows) ตั้ง path ของ tesseract.exe หากยังไม่ได้ตั้ง
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ✅ ฟังก์ชันหมุนภาพให้ถูกทิศทาง
def correct_image_orientation(img):
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

# ✅ ฟังก์ชันอ่านรหัสนักศึกษาแบบตรวจจำนวนพิกเซลดำ
def detect_student_id(region, num_digits=10, choices=10, top_offset=140):
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

# 📷 โหลดภาพ
img = cv2.imread("IMG_2.jpg")
if img is None:
    raise FileNotFoundError("ไม่พบภาพ!")

# 🔁 ตรวจและหมุนภาพอัตโนมัติ (ถ้ากลับหัว)
img = correct_image_orientation(img)

# 👉 ทำงานตามปกติ
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, th = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

boxes = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    area = w * h
    boxes.append((area, x, y, w, h))

boxes = sorted(boxes, key=lambda x: x[0], reverse=True)

# ✅ แสดงกล่องใหญ่สุด 2 กล่อง (คำตอบ + รหัส)
for i, (area, x, y, w, h) in enumerate(boxes[:2]):
    crop = img[y:y+h, x:x+w]
    crop_resized = cv2.resize(crop, (800, 600))
    cv2.imshow(f"Box {i+1}", crop_resized)

# ✅ อ่านรหัสนักศึกษาจากกล่องที่ 2 (กล่องรองจากคำตอบ)
if len(boxes) >= 2:
    _, x, y, w, h = boxes[1]
    id_crop = img[y:y+h, x:x+w]
    gray_id = cv2.cvtColor(id_crop, cv2.COLOR_BGR2GRAY)
    blur_id = cv2.GaussianBlur(gray_id, (5, 5), 0)
    thresh_id = cv2.threshold(blur_id, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    sid = detect_student_id(thresh_id)
    print("📌 รหัสนักศึกษา:", sid)
else:
    print("ไม่พบกล่องรหัสนักศึกษา")

cv2.waitKey(0)
cv2.destroyAllWindows()
