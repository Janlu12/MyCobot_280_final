import cv2
import numpy as np
from pymycobot.mycobot import MyCobot  # Import knižnice pre robotické rameno
import time


pociatok = [15.55,(-17.26),(-141.92),79.98,16.17,(-23.73)]

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
    robot_arm.set_gripper_state(1, 50)

def open_gripper():
    robot_arm.set_gripper_state(0, 50)

# Funkcia pre pohyb ramena a manipuláciu s objektmi
def move_robot_to_sort(color):
    print(color)
    try:
        open_gripper()

        
        # Nastavenie polohy pre zdvihnutie objektu
        pickup_angles =  pociatok  # Zmeniť podľa potreby
        robot_arm.send_angles(pickup_angles, 80)
        time.sleep(2)
       
        
        close_gripper()
        time.sleep(2)

        print('stop')
        
        # Zvýšenie výšky pre premiestnenie objektu
        pickup_angles[1] = pickup_angles[1] + 30
        robot_arm.send_angles(pickup_angles, 80)
        time.sleep(2)

        target_angles = pickup_angles.copy()

        pickup_angles[1] = pickup_angles[1] - 30

        # Nastavenie cieľovej polohy podľa farby
        if color == 'red':
            target_angles[0] = 50
        elif color == 'green':
            target_angles[0] = 80
        elif color == 'blue':
            target_angles[0] = 110

        # Presun objektu do cieľovej polohy
        robot_arm.send_angles(target_angles, 80)
        time.sleep(2)
        # Pustenie objektu
        open_gripper()
        time.sleep(2)

        target_angles[0] = 15
        robot_arm.send_angles(target_angles, 80)
        time.sleep(2)

        # Návrat do počiatočnej polohy
        robot_arm.send_angles(pociatok, 80)
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred in move_robot_to_sort: {e}")

try:
    robot_arm.send_angles(pociatok, 80)
    time.sleep(5)
    print("som na zaciatku !")

    while True:
        ret, origframe = cap.read()
        print(origframe.shape) # Print image shape
        cv2.imshow("original", origframe)
        frame = origframe[120:350, 100:200]
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
    robot_arm.release_all_servos()
finally:
    cap.release()
    cv2.destroyAllWindows()
    robot_arm.release_all_servos()