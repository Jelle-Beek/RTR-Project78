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

#Pad Annelot
capture = cv2.VideoCapture('/Users/annelotjanssen/Desktop/projectShit/video/video2.mp4')

# Pad Kevin 
#capture = cv2.VideoCapture('/Users/kevin/Documents/Technische Informatica HR/2020-2021/Project78/RTR-Project78-main/phidippides-code/camera_algorithm/video2.mp4')

classNames = ['blauw', 'geel', 'oranje']

#>>>>>>> Zelfgemaakte weights model

# modelConfiguration = 'weights/yolov3_testing.cfg'
# modelWeights = 'weights/yolov3_training_final.weights'

#>>>>>> Gebruikte weights model

# Pad Annelot 
modelConfiguration = '/Users/annelotjanssen/Desktop/projectShit/weights/3cones.cfg'
modelWeights = '/Users/annelotjanssen/Desktop/projectShit/weights/3cones_last3.weights'

# Pad Kevin
# modelConfiguration = '/Users/kevin/Documents/Technische Informatica HR/2020-2021/Project78/RTR-Project78-main/phidippides-code/camera_algorithm/3cones.cfg'
# modelWeights = '/Users/kevin/Documents/Technische Informatica HR/2020-2021/Project78/RTR-Project78-main/phidippides-code/camera_algorithm/3cones_last3.weights'

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
    confidenceThreshold = 0.5
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

        #>>>>>>>>>>>>> maakt een verschill tussen linker pionnen en rechter pionnen
        if (x + 0.5 * w < 640) :
            leftCones.append((x + 0.5 * w, y+h))
        else :
            rightCones.append((x + 0.5 * w, y+h))

        #>>>>>>> Maakt blauwe rechthoek als blauwe pylon wordt gedetecteerd
        if (classIds[i] == 0):
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        #>>>>>>> Maakt gele rechthoek als gele pylon wordt gedetecteerd
        elif (classIds[i] == 1):
            cv2.rectangle(img, (x, y), (x + w, y + h), (120, 255, 255), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 255, 255), 2)

        #>>>>>>> Maakt rode rechthoek als oranje pylon wordt gedetecteerd
        elif (classIds[i] == 2):
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(img, f'({x + 0.5 * w}, {y + h})', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    calculatePath(leftCones, rightCones, img)

def calculatePath(leftCones, rightCones, img) :
    # Obtain road border coordinates
    bottomFirst = (0,0)
    bottomSecond = (0,0)
    topFirst = (0,0)
    topSecond = (0,0)
    if (len(leftCones) > 0  and len(rightCones) > 0):
        for cone in leftCones:
            # print(not (bottomFirst))
            if (cone[1] > bottomFirst[1]):
                bottomFirst = cone
            if (cone[1] < bottomFirst[1] and cone[1] > topFirst[1]):
                topFirst = cone
        for cone in rightCones:
            if (cone[1] > bottomSecond[1]):
                bottomSecond = cone
            if (cone[1] < bottomSecond[1] and cone[1] > topSecond[1]):
                topSecond = cone

        leftRoadBorder = (bottomFirst, topFirst)
        rightRoadBorder = (bottomSecond, topSecond)
        bottomFirst = (int(bottomFirst[0]), int(bottomFirst[1]))
        bottomSecond = (int(bottomSecond[0]), int(bottomSecond[1]))
        cv2.line(img, bottomFirst, bottomSecond, (0,0,255), 3)
        cv2.line(img, bottomFirst, bottomSecond, (0,0,255), 3)
    
        # calculate center top & bottom of road
        bottomMiddle = (int((bottomFirst[0] + bottomSecond[0]) / 2),int((bottomFirst[1] + bottomSecond[1]) / 2))
        topMiddle = (int((topFirst[0] + topSecond[0]) / 2),int((topFirst[1] + topSecond[1]) / 2))
        middleRoad = (bottomMiddle, topMiddle)
        middleX = (topFirst[0] + topSecond[0])/2
        middleY = (topFirst[1] + topSecond[1])/2
        
        print(bottomFirst, bottomSecond, topFirst, topSecond)
        if(bottomFirst[0] == topFirst[0] or bottomSecond[0] == topSecond[0] or topFirst == (0,0) or topSecond == (0,0)):
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

    #>>>>> Druk 'q' om het programma af te sluiten
    key = cv2.waitKey(0)
    if key == ord('q'):
        break
    #>>>>> Druk op spatie om het programma te pauzeren
    #if key == ord(' ') :
    #    key = cv2.waitKey(0)
    #    if key == cv2.waitKey(0) and key == ord('q') :
    #        break
    #    if key == ord(' '):
    #        key = cv2.waitKey(1)
    key = cv2.waitKey(0)    
        
