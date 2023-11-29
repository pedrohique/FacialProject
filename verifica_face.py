import numpy as np
import sys
import os
import cv2
import base64
import requests


class VideoThread():
    def __init__(self):
        self.key = 1234
        # self.run()
        


    def run(self):
        # capture from web cam
        face_locations = []
        name_img = "foto.jpg"
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        while True:
            ret, cv_img = cap.read()
            if ret:
                rgb_frame = cv_img[:, :, ::-1]
                # face_locations = face_recognition.face_locations(rgb_frame)
                face_locations = face_cascade.detectMultiScale(
                        rgb_frame,     
                        scaleFactor=1.3,
                        minNeighbors=5,     
                        minSize=(20, 20)
                    )
                for top, right, bottom, left in face_locations:
                       # Draw a box around the face
                    cv2.rectangle(cv_img, (left, top), (right, bottom), (0, 0,  
                        255), 2)
                cv2.imshow('window_name', rgb_frame)
                if list(face_locations):
                    cv2.imwrite(name_img, cv_img) 
                    if cap.isOpened():
                        cap.release()
                        break


                if cv2.waitKey(1) & 0xFF == ord('q'):
                    if cap.isOpened():
                        cap.release()
                        break
        self.sendPhotoDigital()

    def sendPhotoDigital(self):
        
        name_img = "foto.jpg"
        base64_img = None 
        if os.path.isfile(name_img):
            file = open(name_img,'rb').read()
            base64_img = base64.b64encode(file)
                
        if base64_img:
            url = 'https://www.mobcontrole.com.br/89bunzl9170_api/api/IdentityFace'

            resp = requests.post(url, data={"matricula": str(self.key),
                                                "data": base64_img
                                                }, auth=('api.authentication', 'ApI2017AppcOntrOlE'), verify=False)
            print(resp.text)
            resp_text = bool(resp.text.replace('"', ''))
            print(resp_text)
            if resp_text:
                print(
                    f'Acesso liberado - Usuario: {self.key}.', 'green')

                    # self.send_arduino(self.data[self.key][1])


            else:
                print(f'Reconhecimento facial não confere para o usuario: {self.key}')

       

# VideoThread()