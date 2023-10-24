import cv2 #opencv
import urllib.request #para abrir y leer URL
import numpy as np
import serial
#PROYECTO CONTROL ADAPTATIVO 

url = 'http://192.168.137.2/cam-lo.jpg'
#url = 'http://192.168.1.6/'
winName = 'CAM'
cv2.namedWindow(winName,cv2.WINDOW_AUTOSIZE)
scale_percent = 80 # percent of original size    #para procesamiento de imagen

try:
    esp32=serial.Serial('COM6',115200)
except:
    print('Cannot conect to the port')

azulBajo = np.array([100,100,20],np.uint8)
azulAlto = np.array([125,255,255],np.uint8)

while(1):
    imgResponse = urllib.request.urlopen (url) #abrimos el URL
    imgNp = np.array(bytearray(imgResponse.read()),dtype=np.uint8)
    img = cv2.imdecode (imgNp,-1) #decodificamos
    # cv2.imshow('img',img) # mostramos la imagen
    frame = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # vertical
    #     cv2.imshow('frame',frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frameHSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frameHSV,azulBajo,azulAlto)
    
    contornos, hierarchy= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    # #cv2.drawContours(frame, contornos, -1, (255,0,0), 3)
    for c in contornos:
      area = cv2.contourArea(c)
      if area > 3000:
        M = cv2.moments(c)
        if (M["m00"]==0): M["m00"]=1
        x = int(M["m10"]/M["m00"])
        y = int(M['m01']/M['m00'])
        cv2.circle(frame, (x,y), 7, (0,255,0), -1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,0),1,cv2.LINE_AA)
        nuevoContorno = cv2.convexHull(c)
        cv2.drawContours(frame, [nuevoContorno], 0, (255,0,0), 3)
        esp32.write(('1\n').encode())
        
                  
    #cv2.imshow('maskAzul',mask)
    esp32.write(('0\n').encode())
    cv2.imshow('frame',frame)


    #cv2.imshow('maskRed',maskRed) # mostramos la imagen

    #esperamos a que se presione ESC para terminar el programa
    tecla = cv2.waitKey(5) & 0xFF
    if tecla == 27:
        break
cv2.destroyAllWindows()