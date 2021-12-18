# importing the necessary libraries
from datetime import datetime

import cv2
import pandas as pd
import pyttsx3
import threading


# functions to play the audio
def voice_alert_1(eng):
    eng.say('Intruder Alert')
    eng.runAndWait()


def voice_alert_2(eng):
    eng.say('Motion Change')
    eng.runAndWait()


static_back = None
# list when moving object appear
motion_list = [None, None]
# time of movement
time = []
# dataframe to record the movement with start and end time
df = pd.DataFrame(columns=["Start", "End"])
# capturing the video
video = cv2.VideoCapture(0)

# Setting parameters for the voice
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[2].id)
engine.setProperty('rate', 200)

# loop to treat stack of images as video
while True:
    # reading image from video
    check, frame = video.read()

    # initializing motion
    motion = 0
    # converting color image to gray_scale image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # converting gray scale image to GaussianBlur
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    if static_back is None:
        static_back = gray
        continue
    # difference between static background and current frame
    diff_frame = cv2.absdiff(static_back, gray)
    # if difference in between static background and current frame is greater than 30
    # white color(255) will apper.
    thresh_frame = cv2.threshold(diff_frame, 30, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
    # finding contour of moving object.
    cnts, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        motion = 1
        (x, y, w, h) = cv2.boundingRect(contour)
        # making green boundary around the moving object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
    # recording status of motion
    motion_list.append(motion)
    motion_list = motion_list[-2:]
    # recording start time of motion
    if motion_list[-1] == 1 and motion_list[-2] == 0:
        time.append(datetime.now())
        t = threading.Thread(target=voice_alert_1, args=(engine,))
        t.start()

    # recording end time of the motion
    if motion_list[-1] == 0 and motion_list[-2] == 1:
        time.append(datetime.now())
        t = threading.Thread(target=voice_alert_2, args=(engine,))
        t.start()
    # displaying gray frame
    cv2.imshow("Gray Frame", gray)
    # displaying difference frame
    cv2.imshow("Difference Frame", diff_frame)
    # displaying the intensity -difference frame
    cv2.imshow("Threshold Frame", thresh_frame)
    # displaying color frame
    cv2.imshow("Color Frame", frame)

    key = cv2.waitKey(1)
    # press q to stop and exit
    if key == ord('q'):
        if motion == 1:
            time.append(datetime.now())
        break
# recording the time of motion in the dataframe
for i in range(0, len(time), 2):
    df = df.append({"Start": time[i], "End": time[i + 1]}, ignore_index=True)
# creating csv to save the timestamps of the motion
df.to_csv("TimeStamps_of_movement.csv")
# stopping the speech
engine.endLoop()
engine.stop()
# releasing the video
video.release()
# destroying all the windows
cv2.destroyAllWindows()
