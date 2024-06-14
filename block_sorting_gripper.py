import cv2
import numpy as np
from pymycobot.mycobot import MyCobot  # Import knižnice pre robotické rameno

# Funkcia pre detekciu farby
def detect_color(hsv, lower_bound, upper_bound):
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    return mask

# Inicializácia kamery
cap = cv2.VideoCapture(0)

# Inicializácia robotického ramena
# Pripojenie ramena k PC pomocou USB portu
robot_arm = MyCobot("COM3", 115200) # Príklad pripojenia cez USB port OS Windows

# Funkcie pre manipuláciu s uchopovačom
def close_gripper():
    robot_arm.set_gripper_state(0, 50)

def open_gripper():
    robot_arm.set_gripper_state(1, 50)

# Funkcia pre pohyb ramena a manipuláciu s objektmi
def move_robot_to_sort(color):
    try:
        open_gripper()
       
        if color == 'red':
            coords = [100, 200, 50, 0, 0, 0]
        elif color == 'green':
            coords = [150, 250, 50, 0, 0, 0]
        elif color == 'blue':
            coords = [200, 300, 50, 0, 0, 0]

        robot_arm.send_coords(coords, 80, 0)
        close_gripper()
       
        coords[2] = 100  # Zvýšenie výšky
        robot_arm.send_coords(coords, 80, 0)
       
        open_gripper()
    except Exception as e:
        print(f"An error occurred in move_robot_to_sort: {e}")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
       
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
       
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask_red = detect_color(hsv, lower_red, upper_red)
       
        lower_green = np.array([36, 100, 100])
        upper_green = np.array([86, 255, 255])
        mask_green = detect_color(hsv, lower_green, upper_green)
       
        lower_blue = np.array([94, 80, 2])
        upper_blue = np.array([126, 255, 255])
        mask_blue = detect_color(hsv, lower_blue, upper_blue)
       
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
       
        for contour in contours_red:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                move_robot_to_sort('red')
       
        for contour in contours_green:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                move_robot_to_sort('green')
       
        for contour in contours_blue:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                move_robot_to_sort('blue')
       
        cv2.imshow('Frame', frame)
       
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program interrupted by user.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    robot_arm.release_all_servos()
