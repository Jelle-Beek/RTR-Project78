#>>>>>>> Objectdetectieprogramma die oranje, blauwe en gele pylonen kan herkennen

import cv2
import time
import numpy as np
import math

#>>>>>>> instellingen

#>>>>>>> Zet gpu_enable op True om gpu te gebruiken. Dit is alleen mogelijk met opencv met cuda en cudnn installatie.

gpu_enable = False

#>>>>>>> 1 van de capture moet altijd gebruikt worden
#>>>>>>> Uncomment dit om webcam te gebruiken. Verandert de 0 naar 1 als het niet werkt

# capture = cv2.VideoCapture(0)

#>>>>>>> Uncomment dit om videobestand te gebruiken
capture = cv2.VideoCapture('Code-Project56/Bronnen/video/video3.mp4')

classNames = ['blauw', 'geel', 'oranje']

#>>>>>>> Zelfgemaakte weights model

# modelConfiguration = 'Code-Project56/Bronnen/weights/yolov3_testing.cfg'
# modelWeights = 'Code-Project56/Bronnen/weights/yolov3_training_final.weights'

#>>>>>> Gebruikte weights model

modelConfiguration = 'Code-Project56/Bronnen/weights/3cones.cfg'
modelWeights = 'Code-Project56/Bronnen/weights/3cones_last3.weights'

#>>>>>> Weights model project 78

# modelConfiguration = 'Code-Project56/Bronnen/weights/test.cfg'
# modelWeights = 'Code-Project56/Bronnen/weights/pretrained_yolo.weights'

#>>>>>> Zet de weights model in de neural network
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)

if gpu_enable:
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
else:
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

#>>>>>> Methode die de gegevens uit de output van de neural network verwerkt
def findObjects(outputs, img):
    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confidence = []
    confidenceThreshold = 0.6
    nmsThreshold = 0.2

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidenceScore = scores[classId]
            if confidenceScore > confidenceThreshold:

                w, h = int(det[2] * wT), int(det[3] * hT)
                x, y = int((det[0] * wT) - w/2), int(det[1] * hT - h/2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confidence.append(float(confidenceScore))

    indices = cv2.dnn.NMSBoxes(bbox, confidence, confidenceThreshold, nmsThreshold)
    
    leftCones = []
    rightCones = []

    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]

        #>>>>>>> Maakt blauwe rechthoek als blauwe pylon wordt gedetecteerd
        if (classIds[i] == 0):
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            leftCones.append((x + 0.5 * w, y+h))

        #>>>>>>> Maakt gele rechthoek als gele pylon wordt gedetecteerd
        elif (classIds[i] == 1):
            cv2.rectangle(img, (x, y), (x + w, y + h), (120, 255, 255), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 255, 255), 2)
            rightCones.append((x + 0.5 * w, y+h))

        #>>>>>>> Maakt rode rechthoek als oranje pylon wordt gedetecteerd
        elif (classIds[i] == 2):
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    calculatePath(leftCones, rightCones, img)

def calculatePath(leftCones, rightCones, img) :
    # Obtain road border coordinates
    lowerLeft = (0,0)
    lowerRight = (0,0)
    upperLeft = (0,0)
    upperRight = (0,0)
    carPoint = (700, 550)
    h, w, c = img.shape
    screenLeft = (0, h)
    screenRight = (w, h)

    dx = 0
    dy = 1
    
    # Draw static point for the car
    cv2.circle(img, carPoint, 10, (0, 165, 255), -1)
    
    if (len(leftCones) > 0  and len(rightCones) > 0):
        # Kijkt welke pion de onderste en een na onderste is
        for cone in leftCones:
            if (cone[1] > lowerLeft[1]):
                upperLeft = lowerLeft
                lowerLeft = cone
            elif(cone[1] > upperLeft[1] or upperLeft == (0,0)):
                upperLeft = cone
                
        for cone in rightCones:
            if (cone[1] > lowerRight[1]):
                upperRight = lowerRight
                lowerRight = cone
            elif(cone[1] > upperRight[1] or upperRight == (0,0)):
                upperRight = cone

        if upperLeft == lowerLeft:
            upperLeft = (0,0)
        if upperRight == lowerRight:
            upperRight = (0,0)
    
        # calculate center top & bottom of road
        bottomMiddle = (int((lowerLeft[0] + lowerRight[0]) / 2),int((lowerLeft[1] + lowerRight[1]) / 2))
        topMiddle = (int((upperLeft[0] + upperRight[0]) / 2),int((upperLeft[1] + upperRight[1]) / 2))
        middleRoad = (bottomMiddle, topMiddle)
        
        centerX = topMiddle[0] + ((bottomMiddle[0] - topMiddle[0]) / 2)
        centerY = topMiddle[1] + ((bottomMiddle[1] - topMiddle[1]) / 2)
        center = (int(centerX), int(centerY))
        
        lowerRight = (int(lowerRight[0]), int(lowerRight[1]))
        upperRight = (int(upperRight[0]), int(upperRight[1]))
        lowerLeft = (int(lowerLeft[0]), int(lowerLeft[1]))
        upperLeft = (int(upperLeft[0]), int(upperLeft[1]))
        
        if(lowerLeft != (0,0) and upperLeft != (0,0)):
            cv2.line(img, lowerLeft, upperLeft, (0,0,255), 3)
        if(lowerRight != (0,0) and upperRight != (0,0)):
            cv2.line(img, lowerRight, upperRight, (0,0,255), 3)
            
        # Checkt of er een eerste set pionnen
        if(lowerLeft != (0,0) and lowerRight != (0,0)):
            cv2.line(img, lowerLeft, lowerRight, (250,0,255), 2)
            cv2.circle(img, middleRoad[0], 10, (55,255,0), -1)
            cv2.line(img, screenLeft, lowerLeft, (0,0,255), 3)
            cv2.line(img, screenRight, lowerRight, (0,0,255), 3)

        # Checkt of er een tweede set pionnen
        if(upperLeft != (0,0) and upperRight != (0,0)):
            cv2.line(img, upperLeft, upperRight, (250,0,255), 2)
            cv2.circle(img, middleRoad[1], 10, (55,255,0), -1)

            cv2.line(img, middleRoad[0], middleRoad[1], (55,255,0), 8)
            
            # Bereken het verschil in x en y van de middenpunten
            dx = middleRoad[1][0] - middleRoad[0][0]
            dy = middleRoad[0][1] - middleRoad[1][1]


            print(middleRoad)
            print(dx, dy)
            
            #cv2.circle(img, (center[0],center[1]), 10, (0, 165, 255), -1)
            #cv2.line(img, (center[0],center[1]), carPoint, (0, 165, 255), 8)
            
            cv2.line(img, middleRoad[0], (middleRoad[0][0], 0), (55, 255, 0), 8)

        alpha = math.atan(dx/dy)
        alpha *= 180 / math.pi
            

frame_time = 0
new_frame_time = 0

while True:

    #>>>>> Lees de opname
    success, image = capture.read()

    #>>>>> Zet de image om in blob wat leesbaar is voor de neural network
    blob = cv2.dnn.blobFromImage(image, 1/255, (320, 320), [0, 0, 0], 1, crop = False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    outputNames = [layerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)
    findObjects(outputs, image)

    #>>>>>> berekent de fps en zet het op het beeld
    font = cv2.FONT_HERSHEY_SIMPLEX
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - frame_time)
    frame_time = new_frame_time
    fps = int(fps)
    fps = str(fps)
    cv2.putText(image, fps, (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)

    cv2.imshow('image', image)
    key = cv2.waitKey(0)
    while key not in [ord('q'), ord('f')]:
        key = cv2.waitKey(0)
    #>>>>> Druk 'q' om het programma af te sluiten
    if key == ord('q'):
        break
