import cv2
import numpy as np

box_scale = 0.8  # scale of box size
global_box_size = None  # keep box size of col1 for col2

# ----------------------------
# กำหนดค่าคงที่สำหรับตำแหน่งตรวจคำตอบ
# ถ้าต้องการใช้ตำแหน่งอัตโนมัติ ให้กำหนดเป็น None
FIXED_START_POS = {
    "x": 24,     # พิกัด X เริ่มต้นของกล่องแรก
    "y": 40,     # พิกัด Y เริ่มต้นของกล่องแรก
    "radius": 20 # รัศมีของกล่องแรก
} 
# ----------------------------

def find_first_circle_center_and_radius(col_img):
    """Find the top-left circle center and radius"""
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
    """
    ตรวจคำตอบแต่ละกล่อง
    - ถ้าข้อไหนระบายเกิน 1 ตัวเลือก จะถูกกำหนดเป็น None
    """
    global global_box_size

    col_img_color = cv2.cvtColor(col_img, cv2.COLOR_GRAY2BGR)

    # ใช้ตำแหน่งเริ่มต้นที่กำหนดเองก่อน
    if start_pos is not None:
        x_start = start_pos["x"]
        y_start = start_pos["y"]
        radius = start_pos["radius"]
    elif FIXED_START_POS is not None:
        x_start = FIXED_START_POS["x"]
        y_start = FIXED_START_POS["y"]
        radius = FIXED_START_POS["radius"]
    else:
        result = find_first_circle_center_and_radius(col_img)
        if result is None:
            print(f"[ERROR] No circles detected in {debug_name}")
            return []
        x_start, y_start, radius = result

    radius = int(radius * box_scale)
    box_size = radius * 2

    # ใช้ขนาดเดียวกับ col1 ถ้ากำหนด
    if use_same_box_size and global_box_size is not None:
        box_size = global_box_size
        radius = box_size // 2
    else:
        global_box_size = box_size

    if spacing_row is None:
        spacing_row = box_size + spacing_col

    filled_boxes = []
    answer_map = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5'}

    for row in range(rows):
        selected_list = []  # เก็บทุกตัวเลือกที่ detect
        for col in range(cols):
            x = int(x_start + col * (box_size + spacing_col))
            y = int(y_start + row * spacing_row)
            cv2.rectangle(col_img_color,
                          (int(x - radius), int(y - radius)),
                          (int(x + radius), int(y + radius)),
                          (0, 255, 0), 2)

            # ตรวจว่าระบายหรือยัง
            y1, y2 = max(0, y - radius), min(col_img.shape[0], y + radius)
            x1, x2 = max(0, x - radius), min(col_img.shape[1], x + radius)
            roi = col_img[y1:y2, x1:x2]

            if roi.size > 0:
                fill_ratio = np.sum(roi > 127) / roi.size
                if fill_ratio > 0.4:
                    selected_list.append(answer_map[col])

        # ถ้ามีมากกว่า 1 ตัวเลือก ให้เป็น None
        if len(selected_list) == 1:
            filled_boxes.append(selected_list[0])
        else:
            filled_boxes.append(None)

    cv2.imwrite(debug_name, col_img_color)
    return filled_boxes

def find_corners_by_hough(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 200, minLineLength=200, maxLineGap=10)
    if lines is None:
        return None

    verticals, horizontals = [], []
    for x1, y1, x2, y2 in lines[:, 0]:
        if abs(x1 - x2) < 20:
            verticals.append(x1)
        elif abs(y1 - y2) < 20:
            horizontals.append(y1)

    if not verticals or not horizontals:
        return None

    x_left, x_right = min(verticals), max(verticals)
    y_top, y_bottom = min(horizontals), max(horizontals)

    return np.array([(x_left, y_top), (x_right, y_top),
                     (x_right, y_bottom), (x_left, y_bottom)], dtype="float32")

def crop_answer_zone(image_path, spacing_col=5, spacing_row1=37, spacing_row2=None, debug=False):
    img = cv2.imread(image_path)
    if img is None:
        print("[ERROR] Image not found")
        return None

    img = cv2.resize(img, (1654, 2339))
    h, w = img.shape[:2]

    roi_ans = img[int(h * 0.329):int(h * 0.9), int(w * 0.01):int(w * 0.95)]
    corners_ans = find_corners_by_hough(roi_ans)
    if corners_ans is None:
        print("[ERROR] Could not find corners to crop answers")
        return None

    dst = np.array([[0, 0], [1400, 0], [1400, 2000], [0, 2000]], dtype="float32")
    M = cv2.getPerspectiveTransform(corners_ans, dst)
    warp_ans = cv2.warpPerspective(roi_ans, M, (1400, 2000))

    if debug:
        cv2.imwrite("debug_warp_ans.jpg", warp_ans)

    gray_ans = cv2.cvtColor(warp_ans, cv2.COLOR_BGR2GRAY)
    blur_ans = cv2.GaussianBlur(gray_ans, (5, 5), 0)
    thresh_ans = cv2.threshold(blur_ans, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    col1 = thresh_ans[120:2335, 40:240]
    col2 = thresh_ans[120:2335, 270:475]

    if debug:
        col1_ans = mark_boxes_grid(col1, rows=35, cols=5, spacing_col=spacing_col,
                                   spacing_row=spacing_row1, debug_name="debug_col1.jpg",
                                   box_scale=box_scale, use_same_box_size=False)

        col2_ans = mark_boxes_grid(col2, rows=35, cols=5, spacing_col=spacing_col,
                                   spacing_row=spacing_row2, debug_name="debug_col2.jpg",
                                   box_scale=box_scale, use_same_box_size=True,
                                   start_pos=FIXED_START_POS)

        all_answers = col1_ans + col2_ans
        return all_answers

    return col1, col2

# ----------------------------
# ฟังก์ชันตรวจคำตอบและนับคะแนน
# ----------------------------
def check_answers(detected_answers, correct_answers):
    total = len(correct_answers)
    score = 0
    result_list = []

    for i in range(total):
        detected = detected_answers[i] if i < len(detected_answers) else None
        correct = correct_answers[i]
        if detected == correct:
            result_list.append("ถูก")
            score += 1
        else:
            result_list.append("ผิด")

    print("\n✅ ผลตรวจคำตอบ:")
    for idx, res in enumerate(result_list, 1):
        print(f"ข้อ {idx}: {res} (Detected: {detected_answers[idx-1]}, Correct: {correct_answers[idx-1]})")

    print(f"\nคะแนนรวม: {score}/{total}")
    return score

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    detected_answers = crop_answer_zone("IMG_1.jpg", spacing_col=5,
                                        spacing_row1=53, spacing_row2=53, debug=True)
    if detected_answers is not None:
        print("✅ Crop completed! Generated debug_col1.jpg and debug_col2.jpg")

    correct_answers = []
    try:
        with open("Answer.txt", "r", encoding="utf-8") as f:
            for line in f:
                ans = line.strip().upper()
                if ans:
                    correct_answers.append(ans)
        print(f"\n[INFO] Loaded {len(correct_answers)} answers from Answer.txt")
    except FileNotFoundError:
        print("[ERROR] File 'Answer.txt' not found.")
        correct_answers = []

    if detected_answers and correct_answers:
        check_answers(detected_answers, correct_answers)
