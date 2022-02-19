
import requests
import cv2
import numpy as np
import imutils
import time
import json
import threading
import socket

from time import sleep
import websocket
import socket
import threading
import json
import keyboard

KILL_SWITCH_KEY = 'q'
DATA_OUT_IP = "127.0.0.1"
DATA_OUT_PORT = 6789

def estimatePos(gyroQuat,linearAcc):
    return gyroQuat + linearAcc

def getCommaSeperatedValue(pos):
    posString = [ str(x) for x in pos ]
    posStringCommaSperated = ",".join(posString)
    return posStringCommaSperated

def get_correct_orientation():
    pass

def estimatePos(gyro,linear,gravity):
    return gyro + linear + gravity

class SensorServerMobileFeed:
    def __init__(self):

        self.KILL_SWITCH_KEY = 'q'
        self.DATA_IN_IP = "192.168.1.48"
        self.DATA_IN_PORT = "8081"
        self.DATA_OUT_IP = "127.0.0.1"
        self.DATA_OUT_PORT = 6789
        self.GYRO_FEED = []
        self.LINEAR_FEED = []
        self.GRAVITY_FEED = []
        self.gyroWS = None
        

    #@staticmethod
    def on_open(self, ws):
        print("gyro socket open")


    def on_message(self, ws, message):
        if ws.__dict__["url"] == "ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.game_rotation_vector":
            self.GYRO_FEED = json.loads(message)["values"]

        if ws.__dict__["url"] == "ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.gravity":
            self.GRAVITY_FEED = json.loads(message)["values"]

        if ws.__dict__["url"] == "ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.linear_acceleration":
            self.LINEAR_FEED = json.loads(message)["values"]

    def on_error(self, ws, error):
        print("error bro")
        print("### gyro socket error ###")
        print(error)


    def on_close(self, ws, close_code, reason):
        print("### gyro socket closed ###")
        print("close code : ", close_code)
        print("reason : ", reason  )


    def get_gyro_feed(self):
        gyroWS = websocket.WebSocketApp("ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.game_rotation_vector",
                            on_open=self.on_open,
                            on_message=self.on_message,
                            on_error=self.on_error,
                            on_close=self.on_close)
        gyroWS.run_forever()
        

    def get_linear_feed(self):
        linearAccWS = websocket.WebSocketApp("ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.linear_acceleration",
                            on_open=self.on_open,
                            on_message=self.on_message,
                            on_error=self.on_error,
                            on_close=self.on_close)
        linearAccWS.run_forever()


    def get_gravity_feed(self):
        gravityWS = websocket.WebSocketApp("ws://"+ self.DATA_IN_IP + ":" + self.DATA_IN_PORT +"/sensor/connect?type=android.sensor.gravity",
                            on_open=self.on_open,
                            on_message=self.on_message,
                            on_error=self.on_error,
                            on_close=self.on_close)
        gravityWS.run_forever()


    def run(self):
        current_time = time.time()
        print("yayyy")

        gyroListeningThread = threading.Thread(target=sen_obj.get_gyro_feed,daemon=True)
        gyroListeningThread.start()

        linearAccListeningThread = threading.Thread(target=sen_obj.get_linear_feed,daemon=True)
        linearAccListeningThread.start()

        gravityListeningThread = threading.Thread(target=sen_obj.get_gravity_feed,daemon=True)
        gravityListeningThread.start()

sen_obj = SensorServerMobileFeed()
print("[INFO] Starting the feed...")
sen_obj.run()

clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    pos = estimatePos(sen_obj.GYRO_FEED,sen_obj.LINEAR_FEED,sen_obj.GRAVITY_FEED)
    msg = getCommaSeperatedValue(pos)
    print(msg)
    clientSock.sendto(msg.encode('utf-8'), (DATA_OUT_IP, DATA_OUT_PORT))
