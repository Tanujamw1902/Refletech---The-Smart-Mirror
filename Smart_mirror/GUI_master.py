# Check for numpy before importing
try:
    import numpy as np  # For numerical operations
except ImportError:
    print("ERROR: numpy is not installed. Please install it using 'pip install numpy' and try again.")
    import sys
    sys.exit(1)

# Import other necessary libraries
import tkinter as tk  # GUI library
#from Tkinter import ttk, LEFT, END  # (Unused, can be removed)
import time
import cv2  # OpenCV for computer vision
import os  # For file and directory operations
from PIL import Image, ImageTk    # For image processing in GUI
from PIL import Image # For face recognition we will the the LBPH Face Recognizer 

##############################################+=============================================================

# Initialize the main window for the Smart Mirror GUI
root = tk.Tk()
root.configure(background="seashell2")
#root.geometry("1300x700")

# Get screen width and height, set window size to full screen
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))
root.title("Smart Mirror")

# Load and set the background image for the GUI
bg = Image.open("Mirror.jpg")
# Use the correct LANCZOS attribute for resizing depending on Pillow version, fallback to integer values if not available
if hasattr(Image, 'Resampling') and hasattr(Image.Resampling, 'LANCZOS'):
    resample_method = Image.Resampling.LANCZOS  # Pillow >= 9.1.0
else:
    # LANCZOS = 1, BICUBIC = 3 in PIL.Image
    resample_method = getattr(Image, 'LANCZOS', 1)
    # If LANCZOS is not available, fallback to BICUBIC (3)
    if resample_method is None:
        resample_method = 3
bg = bg.resize((1600, 900), resample_method)
bg_img = ImageTk.PhotoImage(bg)

# Create a label to display the background image
bg_lbl = tk.Label(root, image=bg_img)
bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

# Title label for the Smart Mirror
lbl = tk.Label(root, text="Smart Mirror", font=('times', 40,' bold '), height=1, width=30,bg="seashell2",fg="indian red")
lbl.place(x=430, y=5)

# Frame for process buttons and entry
frame_alpr = tk.LabelFrame(root, text=" --Process-- ", width=280, height=600, bd=5, font=('times', 15, ' bold '),bg="seashell4")
frame_alpr.grid(row=0, column=0, sticky='nw')
frame_alpr.place(x=5, y=50)

################################$%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
def image():
    """Capture a single image from the webcam and save it."""
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
        cv2.imwrite('/home/pi/21E9397-Smart_mirror_final/xyz.jpg',frame)
        time.sleep(3)
        rval = False
        vc.release()
        cv2.destroyWindow("preview")
        print("Save image")
        break

def Create_database():
    """Create a dataset of face images for a new user."""
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)
    # id = input('enter user id')
    id=entry2.get()
    sampleN=0;
    while 1:
        ret, img = cap.read()
        MatteBlack  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(MatteBlack, 1.3, 5)
        for (x,y,w,h) in faces:
            sampleN=sampleN+1;
            cv2.imwrite("/home/pi/21E9397-Smart_mirror_final/facesData/User."+str(id)+ "." +str(sampleN)+ ".jpg", MatteBlack[y:y+h, x:x+w])
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            cv2.waitKey(100)
        cv2.imshow('img',img)
        cv2.waitKey(1)
        if sampleN > 70:
            break
    cap.release()
    entry2.delete(0,'end')
    cv2.destroyAllWindows()


def Train_database():
    """Train the face recognizer with the collected face data."""
    # Check if cv2.face and LBPHFaceRecognizer_create are available
    if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
        print("ERROR: cv2.face.LBPHFaceRecognizer_create is not available. Please install opencv-contrib-python and ensure your OpenCV version is correct.")
        return
    recognizer = cv2.face.LBPHFaceRecognizer_create();
    path=r"/home/pi/21E9397-Smart_mirror_final/facesData"
    def getImagesWithID(path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]   
        # print image_path   
        #getImagesWithID(path)
        faces = []
        IDs = []
        for imagePath in imagePaths:      
            # Read the image and convert to grayscale
            facesImg = Image.open(imagePath).convert('L')
            faceNP = np.array(facesImg, 'uint8')
            # Get the label of the image
            ID= int(os.path.split(imagePath)[-1].split(".")[1])
            # Detect the face in the image
            faces.append(faceNP)
            IDs.append(ID)
            cv2.imshow("Adding faces for traning",faceNP)
            cv2.waitKey(10)
        return np.array(IDs), faces
    Ids,faces  = getImagesWithID(path)
    recognizer.train(faces,Ids)
    recognizer.write("trainingdata.yml")
    cv2.destroyAllWindows()


def Test_database():
    """Test the face recognizer in real-time and launch the smart mirror or image script based on recognition."""
    # Check if cv2.face and LBPHFaceRecognizer_create are available
    if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
        print("ERROR: cv2.face.LBPHFaceRecognizer_create is not available. Please install opencv-contrib-python and ensure your OpenCV version is correct.")
        return
    flag=0
    recognizer = cv2.face.LBPHFaceRecognizer_create(1, 8, 8, 8, 100)
    # recognizer = cv2.face.FisherFaceRecognizer(0, 3000);
    recognizer.read('trainingdata.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);
    font = cv2.FONT_HERSHEY_SIMPLEX
    #iniciate id counter
    id = 0
    # names related to ids: example ==> Marcelo: id=1,  etc
    #names = ['None', 'Rohini', 'SURABHI', 'C', 'D','Neha'] 
    # Initialize and start realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height
    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
    while True:
        ret, img =cam.read()
        # img = cv2.flip(img, -1) # Flip vertically
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray,1.3,8,minSize = (int(minW), int(minH)))
        # faces = faceCascade.detectMultiScale( 
        #     gray,
        #     scaleFactor = 1.2,
        #     minNeighbors = 5,
        #     minSize = (int(minW), int(minH)),
        #    )
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            # If confidence is less them 100 ==> "0" : perfect match
            print(confidence)
            if (confidence < 50):
                # print(id,confidence)
                # id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))            
                cv2.putText(img,str(id),(x+5,y-5),font,1,(255,255,255),2)
                cv2.putText(img,str(confidence),(x+5,y+h-5),font,1,(255,255,0),1)
                from subprocess import call
                call(["python3", "smartmirror.py"])
                print("Smart miror Open")
            else:
                # print(confidence)
                id = "unknown person"
                confidence = "  {0}%".format(round(100 - confidence))
                cv2.putText(img,str(id),(x+5,y-5),font,1,(255,255,255),2)
                cv2.putText(img,str(confidence),(x+5,y+h-5),font,1,(255,255,0),1)  
                from subprocess import call
                call(["python3", "Image.py"]) 
        # time.sleep(0.2)
        cv2.imshow('camera',img) 
        # print(flag)
        if flag==10:
            flag=0
            cam.release()
            cv2.destroyAllWindows()
        if cv2.waitKey(1) == ord('q'):
            break

# The following is an alternative test function (commented out)
'''
def Test_database1():
    # ... existing code ...
'''

def test():
    """Launch the smartmirror.py script (for testing)."""
    # Launch the smartmirror.py script (for testing)
    # window =tk.Tk()
    # window.title("Student Login Window")
    print("SS")
    from subprocess import call
    call(["python", "smartmirror.py"])

#################################################################################################################
def window():
    """Destroy the main window (exit the application)."""
    root.destroy()

# Create buttons and entry for the GUI
button1 = tk.Button(frame_alpr, text="Create Face Data", command=Create_database,width=15, height=1, font=('times', 15, ' bold '),bg="pink",fg="white")
button1.place(x=10, y=40)

button2 = tk.Button(frame_alpr, text="Train Face Data", command=Train_database, width=20, height=1, font=('times', 15, ' bold '),bg="yellow4",fg="white")
button2.place(x=10, y=100)

button3 = tk.Button(frame_alpr, text="Open Smart Mirror", command=Test_database, width=20, height=1, font=('times', 15, ' bold '),bg="yellow4",fg="white")
button3.place(x=10, y=150)

# Entry for user ID
entry2=tk.Entry(frame_alpr,bd=2,width=5)
entry2.place(x=200, y=40)
#button4 = tk.Button(frame_alpr, text="Smart Mirror", command=test,width=20, height=1,bg="yellow4",fg="white", font=('times', 15, ' bold '))
#button4.place(x=10, y=220)
#
#button5 = tk.Button(frame_alpr, text="button5", command=window,width=20, height=1, font=('times', 15, ' bold '),bg="yellow4",fg="white")
#button5.place(x=10, y=280)

# Exit button
exit = tk.Button(frame_alpr, text="Exit", command=window, width=20, height=1, font=('times', 15, ' bold '),bg="red",fg="white")
exit.place(x=10, y=400)

# Start the main event loop
root.mainloop()
