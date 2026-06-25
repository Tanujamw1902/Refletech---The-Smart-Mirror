# === Imports ===
try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk
    import tkMessageBox as messagebox

import cv2
import os
import numpy as np
from PIL import Image, ImageTk
import time
from subprocess import call

# === GUI Setup ===
root = tk.Tk()
root.configure(background="seashell2")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("Smart Mirror")

# Background Image
bg = Image.open("Mirror.jpg")
bg = bg.resize((1600, 900), Image.LANCZOS)
bg_img = ImageTk.PhotoImage(bg)

bg_lbl = tk.Label(root, image=bg_img)
bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

# Title Label
lbl = tk.Label(root, text="Smart Mirror", font=('times', 40, 'bold'), height=1, width=30, bg="seashell2", fg="indian red")
lbl.place(x=430, y=5)

# Frame for Buttons
frame_alpr = tk.LabelFrame(root, text=" --Process-- ", width=280, height=600, bd=5, font=('times', 15, 'bold'), bg="seashell4")
frame_alpr.place(x=5, y=50)

# === Face Recognition Functions ===

def Create_database():
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    id = entry2.get()
    sampleN = 0

    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            sampleN += 1
            save_path = f"facesData/User.{str(id)}.{str(sampleN)}.jpg"
            os.makedirs("facesData", exist_ok=True)
            cv2.imwrite(save_path, gray[y:y + h, x:x + w])
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.waitKey(100)

        cv2.imshow('Creating Face Data', img)
        cv2.waitKey(1)

        if sampleN > 70:
            break

    cap.release()
    entry2.delete(0, 'end')
    cv2.destroyAllWindows()


def Train_database():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    path = "facesData"

    def getImagesWithID(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faces = []
        IDs = []

        for imagePath in imagePaths:
            facesImg = Image.open(imagePath).convert('L')
            faceNP = np.array(facesImg, 'uint8')
            ID = int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(faceNP)
            IDs.append(ID)
            cv2.imshow("Adding faces for training", faceNP)
            cv2.waitKey(10)

        return np.array(IDs), faces

    Ids, faces = getImagesWithID(path)
    recognizer.train(faces, Ids)
    recognizer.write("trainingdata.yml")
    cv2.destroyAllWindows()


def Test_database():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainingdata.yml')
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    font = cv2.FONT_HERSHEY_SIMPLEX

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 8, minSize=(int(minW), int(minH)))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 50:
                confidence_str = f"  {round(100 - confidence)}%"
                cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, confidence_str, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
                call(["python", "smartmirror.py"])
                print("Smart Mirror Opened")
            else:
                confidence_str = f"  {round(100 - confidence)}%"
                cv2.putText(img, "Unknown", (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, confidence_str, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
                call(["python", "Image.py"])

        cv2.imshow('camera', img)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


def window():
    root.destroy()

# === GUI Buttons ===

entry2 = tk.Entry(frame_alpr, bd=2, width=5)
entry2.place(x=200, y=40)

tk.Button(frame_alpr, text="Create Face Data", command=Create_database, width=20, height=1,
          font=('times', 15, 'bold'), bg="pink", fg="white").place(x=10, y=40)

tk.Button(frame_alpr, text="Train Face Data", command=Train_database, width=20, height=1,
          font=('times', 15, 'bold'), bg="yellow4", fg="white").place(x=10, y=100)

tk.Button(frame_alpr, text="Open Smart Mirror", command=Test_database, width=20, height=1,
          font=('times', 15, 'bold'), bg="yellow4", fg="white").place(x=10, y=150)

tk.Button(frame_alpr, text="Exit", command=window, width=20, height=1,
          font=('times', 15, 'bold'), bg="red", fg="white").place(x=10, y=400)

# === Run GUI ===
root.mainloop()
