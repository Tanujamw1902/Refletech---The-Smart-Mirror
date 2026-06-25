import cv2
import time

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
   
else:
        rval = False

while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        cv2.imwrite('abc.jpg',frame)
        time.sleep(3)
        rval = False
        vc.release()
        cv2.destroyWindow("preview")
        print("Save image")
        break
