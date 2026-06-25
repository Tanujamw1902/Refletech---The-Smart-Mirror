# smartmirror.py
# requirements
# requests, feedparser, traceback, Pillow
#class main_SM():
import logging
import tkinter as tk
#import ttk
#from Tkinter.ttk import *
#import os
from tkinter import ttk, messagebox



from tkinter import *
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
import PIL
import webbrowser
#import speech_recognition as sr
#import ImageTk
from PIL import Image, ImageTk
#import PIL.ImageTk
from contextlib import contextmanager
import time
#from gtts import gTTS
import os



LOCALE_LOCK = threading.Lock()

ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'in'
weather_api_token = '3b1aa4b5268f4183a9e105831252803'    #'<TOKEN>' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'auto' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None # Set this if IP location lookup does not work for you (must be a string)
longitude = None # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 12

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'clear-day': "assets/Clear_Day.png",  # clear sky day
    'wind': "assets/Wind_New.png",   #wind
    'cloudy': "assets/Cloud_New.png",  # cloudy day
    'partly-cloudy-day': "assets/Partly_Cloud.png",  # partly cloudy day
    'rain': "assets/Rain_New.png",  # rain day
    'snow': "assets/Snow_New.png",  # snow day
    'snow-thin': "assets/Snow_New.png",  # sleet day
    'fog': "assets/FOG_F.png",  # fog day
    'clear-night': "assets/Clear_Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/Partly_Cloud_Night.png",  # scattered clouds night
    'thunderstorm': "assets/Strom_New.png",  # thunderstorm
    'tornado': "assests/Tornado_New.png",    # tornado
    'hail': "assests/Hail_New.png"  # hail
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Tempus Sans ITC', 15), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Tempus Sans ITC', 10), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)#Tempus Sans ITC
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=('Tempus Sans ITC', 10), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            """
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format
                """

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            """if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)"""
            from datetime import datetime
            #print("Time : ",datetime.now().time().strftime("%I:%M"))
            time2 = datetime.now().time().strftime("%I:%M")
            self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


import requests
import json
import traceback
from tkinter import Frame, Label, TOP, LEFT, N
from PIL import Image, ImageTk

class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Tempus Sans ITC',15), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Tempus Sans ITC', 15), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=('Tempus Sans ITC', 14), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Tempus Sans ITC', 14), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    def get_ip(self):
         try:
             ip_url = "http://jsonip.com/"
             req = requests.get(ip_url)
             ip_json = json.loads(req.text)
             return ip_json['ip']
         except Exception as e:
             traceback.print_exc()
             return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:
            # Assume you want to fetch weather based on IP's location if latitude and longitude are None
            latitude = None
            longitude = None
            
            if latitude is None and longitude is None:
                # get location
                location_req_url='http://api.ipstack.com/103.51.95.183?access_key=b5223a5e9a9b2abdb2d4d000e9614358'
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']
                print(lon,lat)
                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])
                print(location2)

                # Replace with your actual WeatherAPI key
                api_key = "3b1aa4b5268f4183a9e105831252803"
                
                # WeatherAPI URL
                url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}&aqi=no'
                
                # Make the API request
                response = requests.get(url)
                
                # Check if the response is successful
                if response.status_code == 200:
                    data = response.json()
                    # Extract weather description and temperature
                    weather_description = data['current']['condition']['text']
                    temperature = data['current']['temp_c']
                    print(weather_description, temperature)
                else:
                    # Return error message if request fails
                    return f"Error: {response.status_code} - {response.text}"

            else:
                # If latitude and longitude are available, fetch weather data based on them
                location2 = ""
                api_key = "3b1aa4b5268f4183a9e105831252803"  # Replace with your valid WeatherAPI key
                weather_req_url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q={latitude},{longitude}&aqi=no'
                response = requests.get(weather_req_url)

                if response.status_code == 200:
                    data = response.json()
                    # Extract weather description and temperature
                    weather_description = data['current']['condition']['text']
                    temperature = data['current']['temp_c']
                    location2 = f"{data['location']['name']}, {data['location']['region']}"
                else:
                    return f"Error: {response.status_code} - {response.text}"

            # Display the weather data
            self.temperature = f"{str(int(temperature))}°C"
            self.currently = weather_description
            self.location = location2

            # Update the labels
            self.temperatureLbl.config(text=self.temperature)
            self.currentlyLbl.config(text=self.currently)
            self.locationLbl.config(text=self.location)

            # Handle weather icon (WeatherAPI provides icon URL)
            icon_url = "http:" + data['current']['condition']['icon']
            image = Image.open(requests.get(icon_url, stream=True).raw)
            image = image.resize((50, 50), Image.LANCZOS)
            image = image.convert('RGB')
            photo = ImageTk.PhotoImage(image)

            # Update icon
            self.iconLbl.config(image=photo)
            self.iconLbl.image = photo

        except Exception as e:
            traceback.print_exc()
            print(f"Error: {e}. Cannot get weather.")

        # Refresh every 10 minutes (600,000 ms)
        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32













#=============================================================================
class G_Search(Frame):
    
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'Google Search......' 
        self.Searchwin = Frame(self, bg="black")
        self.Searchwin.pack(side=TOP)
        # Used to take text from entrybox 
        cvt_to = StringVar()
        # And display the new string to the label
        cvt_from = StringVar()
        
        def doTheSearch():
            address = 'https://www.google.com/search?q='
            word = cvt_from.get()
            newWord = address + word
            cvt_to.set(newWord)
            time.sleep(1.5)
            webbrowser.open(newWord)
            
        
        ent_one = Entry(self, width=20, textvariable=cvt_from, justify='left', font=("Tempus Sans ITC", 10))
        ent_one.pack(side=LEFT, anchor=W)
#        photo=ImageTk.PhotoImage(file="assets/google.png")
                
#        can.create_image(150,150,image=photo)
        
#        boton = Button(miFrame,image=photo,border=0)
        #photo=PhotoImage(file=r"C:\Users\srcmo\OneDrive\Desktop\New folder\SMART_MIRROR\assets\Google_Sym.png")
        #photo=photo.subsample(2,2)
        #photo=Image.open(r"C:\Users\srcmo\OneDrive\Desktop\New folder\SMART_MIRROR\assets\Google_New.png")
        #photo = photo.resize((100, 100), Image.ANTIALIAS)
        #photo=ImageTk.PhotoImage(photo)
        btn_two = Button(self, bg='white',fg='red' ,text="Google Search",font=("Tempus Sans ITC",10,"bold"), command=doTheSearch )
#        btn_two.config(image=photo)
        btn_two.pack(side=RIGHT, anchor=W)
        
        def listen():
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Say Something...")
                audio = r.listen(source)
                text = r.recognize_google(audio)
                import time
                language = 'en'
                time.sleep(5)
                print('You Said : {}'.format(text))
                address = 'http://www.google.com/#q='
                newWord = address + text
                webbrowser.open(newWord)
                mytext="Dear!  Your Search Is Ready !!"
                myobj = gTTS(text=mytext, lang=language, slow=False)
                myobj.save("welcome.mp3")
                os.system(" welcome.mp3")
                
                    
                    #print(t)
                    
        #image = Image.open("C:/Users/srcmo/OneDrive/Desktop/New folder/SMART_MIRROR/assets/Mike.png")
        #image = image.resize((50, 50), Image.ANTIALIAS)
        #image = image.convert('RGB')
        #photo = ImageTk.PhotoImage(image)
        #photo=PhotoImage(file="C:/Users/srcmo/OneDrive/Desktop/New folder/SMART_MIRROR/assets/Mike.png")
        """voice = Button(self,image=photo,command=listen)
        voice.pack(side=RIGHT, anchor=W)"""
        voice = Button(self,text="<)))",bg='white',fg='black',command=listen,font=("Tempus Sans ITC",10,"bold"))
        voice.pack(side=LEFT, anchor=W)
    

    

    
    


#=======================================================================================================

class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = "Today's News" # 'News' is more internationally generic
        self.newsLbl = Label(self, text=self.title, font=('times', 10), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black",height=10)
        self.headlinesContainer.pack(side=TOP)
        self.get_headlines()

    def get_headlines(self):
        try:
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
            if news_country_code == None:
                headlines_url = "https://news.google.com/news?ned=us&output=rss"
            else:
                headlines_url = "https://news.google.com/news?ned=%s&output=rss" % news_country_code

            feed = feedparser.parse(headlines_url)

            for post in feed.entries[0:5]:
                headline = NewsHeadline(self.headlinesContainer, post.title)
                headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get news." % e)

        self.after(600000, self.get_headlines)


class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.LANCZOS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('times', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLbl = Label(self, text=self.title, font=('Tempus Sans ITC', medium_text_size), fg="white", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.get_events()

    def get_events(self):
        #TODO: implement this method
        # reference https://developers.google.com/google-apps/calendar/quickstart/python

        # remove all children
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        calendar_event = CalendarEvent(self.calendarEventContainer)
        calendar_event.pack(side=TOP, anchor=E)
        pass


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Tempus Sans ITC', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)




#########################################################################################333

    
import random

#================================================================####################################################
#class MainApp(tk.Tk):
from tkinter import *
import tkinter as tk
from PIL import Image, ImageTk
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import call

class FullscreenWindow:
    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='grey')
        
        w, h = self.tk.winfo_screenwidth(), self.tk.winfo_screenheight()
        self.tk.geometry("%dx%d+0+0" % (w, h))
        
        # Frames
        # self.topFrame = LabelFrame(self.tk, background='red', bd=0)
        # self.midFrame = LabelFrame(self.tk, background='red', bd=0)
        # self.bottomFrame = LabelFrame(self.tk, background='grey', bd=0)
        
        # self.topFrame.pack(side=TOP, fill=BOTH, expand=YES)
        # self.midFrame.pack(side=TOP, fill=BOTH, expand=YES)
        # self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        
        # Background image
        self.bg = Image.open("Mirror.jpg").resize((w, h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.bg)
        self.bg_lbl = tk.Label(self.tk, image=self.bg_img)
        self.bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)
        
        #self.bottomFrame = LabelFrame(self.tk, background='skyblue', bd=0)
        
      
        #self.bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=YES)
        # Widgets
        self.clock = Clock(self.tk)
        self.clock.place(x=800,y=10)
        
        self.weather = Weather(self.tk)
        self.weather.place(x=5,y=10)
        
        self.search = G_Search(self.tk)
        self.search.place(x=250,y=10)
        
        self.news = News(self.tk)
        self.news.place(x=180,y=100)
        
       # Email section - placed inside a frame
        self.email_frame = LabelFrame(self.tk, text="Send Email", background="grey", fg="white", font=("times",10, "bold"), bd=2)
        self.email_frame.place(x=10, y=400, width=400, height=300)  # Adjust positioning and size as needed
        #self.create_email_widgets()

       
        # Email widget titles and entry fields
        tk.Label(self.email_frame, text="Message Body", width=15, background="grey", foreground="white", 
                 font=("Tempus Sans ITC", 10, "bold")).place(x=10, y=5)
        
        self.body1 = Text(self.email_frame, font="Tahoma", bd=4, height=4, width=15)
        self.body1.place(x=5, y=40)
        
        tk.Label(self.email_frame, text="Enter Your Mail:", width=15, background="grey", foreground="white", 
                 font=("Tempus Sans ITC", 10, "bold")).place(x=200, y=5)
        
        self.entry1 = Entry(self.email_frame, bd=2, width=15)
        self.entry1.place(x=200, y=40)
        
        tk.Label(self.email_frame, text="Enter Password:", width=15, background="grey", foreground="white", 
                 font=("Tempus Sans ITC", 10, "bold")).place(x=200, y=80)
        
        self.entry2 = Entry(self.email_frame, bd=2, width=15, show="#")
        self.entry2.place(x=200, y=120)
        
        tk.Label(self.email_frame, text="Receiver's Mail ID:", width=15, background="grey", foreground="white", 
                 font=("Tempus Sans ITC", 10, "bold")).place(x=200, y=160)
        
        self.entry3 = Entry(self.email_frame, bd=2, width=15)
        self.entry3.place(x=200, y=200)
        
        # Send Mail Button
        tk.Button(self.email_frame, text="SEND MAIL", command=self.send_email, font=("Tempus Sans ITC", 12), bg='green',
                  fg='white').place(x=50, y=200)
        
        tk.Button(self.tk, text="Todo list", bg='red', fg='white', bd=5,font=("Times", 18, "bold"),
                  command=self.open_todo).place(x=800, y=300)
        
        # Call the motivation thoughts method
        self.motivation_frame = tk.LabelFrame(self.tk, text="Motivational Thoughts", background="skyblue",
                                              fg="red", font=("Tempus Sans ITC", 10, "bold"), bd=2)
        self.motivation_frame.place(x=450, y=400, width=500, height=300)  # Adjust position and size
       # self.show_motivational_thoughts()
       # List of 20 motivational thoughts
        thoughts = [
           "Believe in yourself and all that you are.",
           "You are stronger than you think.",
           "The only way to do great work is to love what you do.",
           "Don't watch the clock; do what it does. Keep going.",
           "Believe you can and you're halfway there.",
           "The future belongs to those who believe in \n the beauty of their dreams.",
           "The only limit to our realization of tomorrow is our doubts of today.",
           "Do not wait to strike till the iron is hot,\n but make it hot by striking.",
           "Everything you can imagine is real.",
           "Success is not final, failure is not fatal: \n It is the courage to continue that counts.",
           "Hardships often prepare ordinary people for an extraordinary destiny.",
           "Don't stop when you're tired. Stop when you're done.",
           "You are never too old to set another goal or to dream a new dream.",
           "The best time to plant a tree was 20 years ago.\n The second best time is now.",
           "Success is not how high you have climbed, but how you make \n a positive difference to the world.",
           "The journey of a thousand miles begins with one step.",
           "It does not matter how slowly you go as long as you do not stop.",
           "Opportunities don't happen, you create them.",
           "Don't be pushed around by the fears in your mind. \n Be led by the dreams in your heart.",
           "Act as if what you do makes a difference. It does."
       ]

       # Randomly select 5 thoughts
        random_thoughts = random.sample(thoughts, 5)
       
       # Display the random thoughts on the frame
        y_position = 10  # Starting Y position for first thought
        for thought in random_thoughts:
           tk.Label(self.motivation_frame, text=" - "+str(thought), bg="skyblue",
                    fg="black", font=("times", 10,'bold')).place(x=10, y=y_position)
           y_position += 50  # Increment Y position for the next label
        
        

    def send_email(self):
        fromaddr = self.entry1.get()
        toaddr = self.entry3.get()
        password = self.entry2.get()
        body = self.body1.get('1.0', 'end-1c')
        
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = "Smart Mirror :"
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(fromaddr, password)
            s.sendmail(fromaddr, toaddr, msg.as_string())
            print("Mail Sent Successfully!")
        except Exception as e:
            print("Oops! Mail Not Sent!", str(e))
        finally:
            s.quit()

    def open_todo(self):
        call(["python3", "todo.py"])




       
#w = FullscreenWindow()
#w.tk.main()
#w.tk.mainloop()
    #====================================================================

if __name__ == '__main__':
    w = FullscreenWindow()
   
#    w.tk.main()
    w.tk.mainloop()
    
    
