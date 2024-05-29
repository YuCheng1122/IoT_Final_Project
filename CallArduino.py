import serial
from time import sleep

sleep(6)

COM_PORT = 'COM3'  # 請自行修改序列埠名稱
BAUD_RATES = 9600
ser = serial.Serial(COM_PORT, BAUD_RATES)


try:
    #switch = 1
    while True:
        print('Motor_Fast')
        ser.write(b'Motor_Fast\n')  # 訊息必須是位元組類型
         
        

        sleep(3)  # 暫停3秒，再執行接收回應訊息的迴圈

        while ser.in_waiting:
            mcu_feedback = ser.readline().decode()  # 接收回應訊息並解碼
            print('response', mcu_feedback)

except KeyboardInterrupt:
    ser.close()
    print('Call Arduino end！')

# try:
#     switch = 1
#     while True:
#         if switch == 1:
#             print('傳送開燈指令')
#             ser.write(b'motor fast\n')  # 訊息必須是位元組類型
#             switch = 2
#         elif switch == 2:
#             print('傳送關燈指令')
#             ser.write(b'LED_OFF\n')
#             switch = 1

#         sleep(3)  # 暫停3秒，再執行接收回應訊息的迴圈

#         while ser.in_waiting:
#             mcu_feedback = ser.readline().decode()  # 接收回應訊息並解碼
#             print('控制板回應：', mcu_feedback)

# except KeyboardInterrupt:
#     ser.close()
#     print('再見！')
