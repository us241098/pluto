
import requests
import cv2
import numpy as np
import imutils
import time
import json
import threading
import socket

class MobileFeed:
    def __init__(self):
        self.video_url = "http://192.168.29.24:8080/shot.jpg"
        self.sensors_url = "http://192.168.29.24:8080/sensors.json"
        self.video_feed = None
        self.sensors_feed = None

    def get_video_feed(self):
        # Get the video feed from the URL
        video_feed = requests.get(self.video_url)
        # Convert the video feed to numpy array
        np_arr = np.array(bytearray(video_feed.content), dtype=np.uint8)
        # Decode the numpy array to opencv format
        img = cv2.imdecode(np_arr, -1)
        img = imutils.resize(img, width=1000, height=1800)
        # Return the video feed
        self.video_feed = img.tolist()


    def get_sensors_feed(self):
        # Get the sensors feed from the URL
        sensor_data = requests.get(self.sensors_url)
        data = json.loads(sensor_data.text)
        # Return the sensors feed
        accel_list = data["accel"]["data"][-1][1]
        gyro_list = data["gyro"]["data"][-1][1]
        mag_list = data["mag"]["data"][-1][1]
        prox_list = data["proximity"]["data"][-1][1]
        gravity_list = data["gravity"]["data"][-1][1]
        linear_accel_list = data["lin_accel"]["data"][-1][1]
        rotation_vector_list = data["rot_vector"]["data"][-1][1]
        self.sensors_feed = {"accel": accel_list, "gyro": gyro_list, "mag": mag_list, "prox": prox_list, "gravity": gravity_list, "linear_accel": linear_accel_list, "rotation_vector": rotation_vector_list}
        #return accel_list, gyro_list, mag_list, prox_list, gravity_list, linear_accel_list, rotation_vector_list

    def run(self):
        current_time = time.time()
        threading.Thread(target=self.get_sensors_feed()).start()
        threading.Thread(target=self.get_video_feed()).start()
        api_response = { "sensors": self.sensors_feed, "timestamp": current_time}
        print(api_response)
        #api_response = {"timestamp": current_time,"img": img, "accel": accel_list, "gyro": gyro_list, "mag": mag_list, "prox": prox_list, "gravity": gravity_list, "linear_accel": linear_accel_list, "rotation_vector": rotation_vector_list}
        byte_message = bytes(str(api_response), "utf-8")
        opened_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        opened_socket.sendto(byte_message, ("127.0.0.1", 6969))
        print("y")
        #return api_response

    def loop(self):
        while True:
            print("yy")
            self.run()

sen_obj = MobileFeed()
print("[INFO] Starting the feed...")
print(sen_obj.loop())
