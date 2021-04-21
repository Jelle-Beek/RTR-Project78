#>>>>>>> Objectdetectieprogramma die oranje, blauwe en gele pylonen kan herkennen

import cv2
import time
import numpy as np

#>>>>>>> instellingen

#>>>>>>> Zet gpu_enable op True om gpu te gebruiken. Dit is alleen mogelijk met opencv met cuda en cudnn installatie.

gpu_enable = False

#>>>>>>> 1 van de capture moet altijd gebruikt worden
#>>>>>>> Uncomment dit om webcam te gebruiken. Verandert de 0 naar 1 als het niet werkt

# capture = cv2.VideoCapture(0)

#>>>>>>> Uncomment dit om videobestand te gebruiken
capture = cv2.VideoCapture('./Bronnen/video/video3.mp4')

classNames = ['blauw', 'geel', 'oranje']

#>>>>>>> Zelfgemaakte weights model

# modelConfiguration = 'weights/yolov3_testing.cfg'
# modelWeights = 'weights/yolov3_training_final.weights'

#>>>>>> Gebruikte weights model

modelConfiguration = './Bronnen/weights/3cones.cfg'
modelWeights = './Bronnen/weights/3cones_last3.weights'

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
    confidenceThreshold = 0.4
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
    if (len(leftCones) > 0  and len(rightCones) > 0):
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


        leftRoadBorder = (lowerLeft, upperLeft)
        rightRoadBorder = (lowerRight, upperRight)
    
        # calculate center top & bottom of road
        bottomMiddle = (int((lowerLeft[0] + lowerRight[0]) / 2),int((lowerLeft[1] + lowerRight[1]) / 2))
        topMiddle = (int((upperLeft[0] + upperRight[0]) / 2),int((upperLeft[1] + upperRight[1]) / 2))
        middleRoad = (bottomMiddle, topMiddle)
        middleX = (upperLeft[0] + upperRight[0])/2
        middleY = (upperLeft[1] + upperRight[1])/2
        
        if(lowerLeft != (0,0) and upperLeft != (0,0)):
            lowerLeft = (int(lowerLeft[0]), int(lowerLeft[1]))
            upperLeft = (int(upperLeft[0]), int(upperLeft[1]))
            cv2.line(img, lowerLeft, upperLeft, (0,0,255), 3)
        if(lowerRight != (0,0) and upperRight != (0,0)):
            lowerRight = (int(lowerRight[0]), int(lowerRight[1]))
            upperRight = (int(upperRight[0]), int(upperRight[1]))
            cv2.line(img, lowerRight, upperRight, (0,0,255), 3)
        
        #print(lowerLeft, lowerRight, upperLeft, upperRight)
        if(lowerLeft[0] == upperLeft[0] or lowerRight[0] == upperRight[0] or upperLeft == (0,0) or upperRight == (0,0)):
            cv2.line(img, middleRoad[0], middleRoad[0], (255, 0, 0), 20)
        else:
            cv2.line(img, middleRoad[0], middleRoad[1], (255, 0, 0), 20)


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