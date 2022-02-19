# get gyro data from phone with web sockets

from time import sleep
import websocket
import socket
import threading
import json
import keyboard

# config consts 
KILL_SWITCH_KEY = 'q'
DATA_IN_IP = "192.168.1.10"
DATA_IN_PORT = "8080"
DATA_OUT_IP = "127.0.0.1"
DATA_OUT_PORT = 6789

gyroListeningThread = None
linearAccListeningThread = None
gyroWS = None
linearAccWS = None
gyroQuat = [0,0,0,0]
linearAcc = [0,0,0]

def startGyroListener():
    global gyroWS
    def on_open(ws):
        print("gyro socket open")

    def on_message(ws, message):
        global gyroQuat
        gyroQuat = json.loads(message)["values"]

    def on_error(ws, error):
        print("### gyro socket error ###")
        print(error)

    def on_close(ws, close_code, reason):
        print("### gyro socket closed ###")
        print("close code : ", close_code)
        print("reason : ", reason  )

    gyroWS = websocket.WebSocketApp("ws://"+ DATA_IN_IP + ":" + DATA_IN_PORT +"/sensor/connect?type=android.sensor.game_rotation_vector",
                        on_open=on_open,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_close)
    gyroWS.run_forever()

def startLinearAccListener():
    global linearAccWS
    def on_open(ws):
        print("linearAcc socket open")

    def on_message(ws, message):
        global linearAcc
        linearAcc = json.loads(message)["values"]

    def on_error(ws, error):
        print("### linear Acc socket error ###")
        print(error)

    def on_close(ws, close_code, reason):
        print("### linear Acc socket closed ###")
        print("close code : ", close_code)
        print("reason : ", reason  )

    linearAcc = websocket.WebSocketApp("ws://"+ DATA_IN_IP + ":" + DATA_IN_PORT +"/sensor/connect?type=android.sensor.linear_acceleration",
                        on_open=on_open,
                        on_message=on_message,
                        on_error=on_error,
                        on_close=on_close)
    linearAcc.run_forever()

def getCommaSeperatedValue(pos):
    posString = [ str(x) for x in pos ]
    posStringCommaSperated = ",".join(posString)
    return posStringCommaSperated

def estimatePos(gyroQuat,linearAcc):
    return gyroQuat + linearAcc

if __name__ == "__main__":

    gyroListeningThread = threading.Thread(target=startGyroListener,daemon=True)
    gyroListeningThread.start()
    linearAccListeningThread = threading.Thread(target=startLinearAccListener,daemon=True)
    linearAccListeningThread.start()
    
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while not keyboard.is_pressed(KILL_SWITCH_KEY):
        pos = estimatePos(gyroQuat,linearAcc)
        msg = getCommaSeperatedValue(pos)
        clientSock.sendto(msg.encode('utf-8'), (DATA_OUT_IP, DATA_OUT_PORT))