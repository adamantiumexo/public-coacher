import re 
from math import pi
from random import randint
import os
import mysql.connector
from googleapiclient.discovery import build
import isodate
import json
import time 
import random
import tkinter
from PIL import Image, ImageTk
import cv2
import customtkinter as ctk
from tkinter import filedialog
import webbrowser
from tkinterweb import HtmlFrame
import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os



ytapi_key = 'AIzaSyCXo-Be62wpijOC3ZpU48G4ByxB4vTXsCw'
ytapisvc = build('youtube', 'v3', developerKey=ytapi_key)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green") #
app = ctk.CTk()

app.title("My CTK App")
app.geometry("1280x720")
app.resizable(True, True)




def iso8601converter(iso8601string):
    # Converts ISO 8601 duration format to a human-readable format
    # Example: PT1H30M15S -> 1 hour, 30 minutes, 15 seconds
    duration = isodate.parse_duration(iso8601string)
    total_seconds = int(duration.total_seconds())

    if total_seconds < 60:
        # Format as '0:NN' for durations less than 1 minute
        return f"0:{total_seconds:02}"
    else:
        # Format as 'MM:SS' or 'HH:MM:SS' for longer durations
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes}:{seconds:02}"
        
def videotitlebyID(videoID):
    # cast tuple to string
    videoID = str(videoID)  # convert tuple into string
    videoID = videoID.replace("(", "").replace(")", "").replace(",", "").replace("'", "")  # remove any brackets and commas from the video ID
    print(f' video id is {videoID}')
    # takes a video ID as input and returns the video title as the response local variable
    request = ytapisvc.videos().list(
        part='snippet',
        id=videoID
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['snippet']['title']
    else:
        return "Video title not found"

def videodatabyID(videoID):
    # takes a video ID as input and returns the video data as the response local variable
    # returns as a dictionary
    request = ytapisvc.videos().list(
        part='snippet',
        id=videoID
    )
    response = request.execute()
    return response

def videotagsbyID(videoID):
    # takes a video ID as input and returns the video's tags as the response local variable
    request = ytapisvc.videos().list(
        part='snippet',
        id=videoID
    )
    response = request.execute()
    if 'tags' in response['items'][0]['snippet'] and len(json.dump((response['items'][0]['snippet']['tags']))) < 600:
        return response['items'][0]['snippet']['tags']
    else:
        return None

def retrieveVideoEmbedCode(videoID):
    # takes a video ID as input and returns the video's HTML embed as the response local variable
    request = ytapisvc.videos().list(
        part='player',
        id=videoID
    )
    response = request.execute()
    return response['items'][0]['player']['embedHtml']

def videoDescriptionbyID(videoID):
    # takes a video ID as input and returns the video's description as the response local variable
    request = ytapisvc.videos().list(
        part='snippet',
        id=videoID
    )
    response = request.execute()
    return response['items'][0]['snippet']['description']
def videoDurationbyID(videoID):
    # takes a video ID as input and returns the video's duration as the response local variable
    request = ytapisvc.videos().list(
        part='contentDetails',
        id=videoID
    )
    response = request.execute()
    return response['items'][0]['contentDetails']['duration']
    
try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        passwd=os.getenv("DB_PASSWORD", "adam1234"),
        database =('speakercoach')
    )
    
    
    mycursor = db.cursor(buffered=True)
    print("Database connection successful.")
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
    db = None
    



class User:
    def __init__(self,username,YoB,passhash,scoreContent,scoreConf,scoreEngagement):
        self.username = username
        self.YoB = YoB
        self.passhash = passhash
        self._scoreEngagement = scoreEngagement
        self._scoreConf = scoreConf
        self._scoreContent = scoreContent
        self._activityhistory = activityLinkedList(None)
        # encapsulated to avoid outside editing
        
    def listAttrScores(self):
        print(f"Engagement: {self._scoreEngagement} | Confidence: {self._scoreConf} | Content: {self._scoreContent}")
    # Displays attributes in text
    def takeinitQuiz(self):
        self._scoreEngagement,self._scoreConf,self._scoreContent = initQuiz()
        initScores = [self._scoreEngagement,self._scoreConf,self._scoreContent]
        
        return initScores
    
    def updateDBentry(self):
        # Update the user's scores in the database
        update_query = """
        UPDATE User 
        SET scoreContent = %s, scoreConfidence = %s, scoreEngagement = %s 
        WHERE username = %s
        """
        mycursor.execute(update_query, (self._scoreContent, self._scoreConf, self._scoreEngagement, self.username))
        db.commit()  # Commit the changes to the database
        print(f"Scores for {self.username} updated successfully.")
        
    def retakeinitQuiz(self):
        self._scoreContent,self._scoreConf,self._scoreEngagement = initQuiz()
        self.listAttrScores()
        print('Updating database')
        self.updateDBentry()
    def leastTrait(self, scoreContent, scoreEngagement, scoreConf):
        if scoreContent == scoreEngagement and scoreContent == scoreConf:
            leastScore = random.choice(['research','confidence','self'])
            print(leastScore)
            return leastScore
        else:
            return min(scoreContent, scoreEngagement, scoreConf)
    
    

    def returndatabaseattributes(self):
        list = [username,passhash]
        return list
    def scoreEdit(self,scoreEngagement,scoreConf,scoreContent):
        self._scoreEngagement = scoreEngagement
        self._scoreConf = scoreConf
        self._scoreContent = scoreContent
        
    
class Activities:
    def __init__(self, activityID, trait):
        self.activityID = activityID
        self.trait = trait


class Video(Activities): # Inheritance and polymorphism from Activities class
    def __init__(self, activityID, trait, title, publisher, host, duration, viewcount, publishDate, tags,embedcode):
        super().__init__(activityID,trait)
        self._title = title
        self._publisher = publisher
        self._host = host
        self._duration = duration
        self._viewcount = viewcount
        self._publishDate = publishDate
        self._videotags = tags
        self._embedcode = embedcode

    def returnallAttributes(self):
        list = [self.activityID,self.trait,self._title,self._publisher,self._host,self._duration,self._viewcount,self._publishDate,self._videotags]
        return list


class activityNode:
    def __init__(self,data):
        self.data = data 
        self.next = None
        
class activityLinkedList:
    def __init__ (self,headptr):
        self.headptr = None # initial ptr is None because no data in first position
    
    
    def add_video(self,videoTitle):
        newNode = activityNode(videoTitle)
        if self.headptr is None :
            print('first element is' + videoTitle)
            self.headptr = newNode
            return
        
        # else, if there is already a video in the start of the linked list
        
        else:
            currentnode = self.headptr
            while(currentnode.next):
                currentnode = currentnode.next
            
            currentnode.next = newNode
    
    def lengthIsFive(self):
        length = 0
        if(self.headptr):
            current_node = self.headptr
            while(current_node):
                length += 1 
                current_node = current_node.next
        
        return (length == 5)
        
    def removeEarliestVideo(self):
        if self.headptr is None:
            return
        # if there is no head
        self.headptr = self.headptr.next
    
    def strHistory(self):
        # activity history linked list to string 
        activities = []
        current_node = self.headptr
        while current_node:
            activities.append(current_node.data)
            current_node = current_node.next
        return ', '.join(activities)
        
def update_activity_history(user, newVideo):
    # checks if already 5 videos
    if user._activityhistory.lengthIsFive():
        print('len is 5')
        user._activityhistory.removeEarliestVideo()  # Remove the earliest activity to make space

    # add only after making the length 4 videos
    user._activityhistory.add_video(newVideo)

    print(user._activityhistory.strHistory())
    stringHistory = user._activityhistory.strHistory()
    print(stringHistory)
    print("Before adding new video:")
    # update activity history in the database
    update_query = "UPDATE User SET activityhistory = %s WHERE username = %s"
    mycursor.execute(update_query, (stringHistory, user.username))
    db.commit()
    print(f"Activity history for {user.username} updated successfully.")

def initQuiz():
    # questions are mcq 
    # each mcq answer has a different weight (one for each of three traits) to determine str / wk
    weightsEngagement = [0.5, 0.1, 0.3, 0.8, 0.3, 0.4, 0.9]
    weightsConf = [0.7, 0.4, 0.4, 0.5, 0.8, 0.9, 0.8]
    weightsContent = [0.1, 0.8, 0.9, 0.6, 0.4, 0.3, 0.7]
    questions = {'0': "I can start conversations easily.",
                 '1': "It is more important to be accurate than to be engaging.",
                 '2': "When someone says something incorrect, I can't help but correct them.",
                 '3': "It is hard for me to run out of things to say.",
                 '4': "I am interested in conversations regarding topics unfamiliar to me.",
                 '5': "I consider myself risk-taking rather than risk averse.",
                 '6': "Telling stories in detail comes naturally to me."}
    ctk.quizInstruction = ctk.CTkLabel(app, text="Please answer the following questions on a scale of 1-5, where 1 is strongly disagree and 5 is strongly agree.")
    ctk.quizInstruction.configure(font=("Helvetica", 12))
    ctk.quizInstruction.pack(pady=5, padx=20)
    time.sleep(2)
    
    scoreEngagement = 0
    scoreConf = 0
    scoreContent = 0
    
    answer_submitted = tkinter.BooleanVar()

    def validate_answer(i):
        try:
            responseInted = int(ctk.answerEntry.get())
            if responseInted < 1 or responseInted > 5:
                raise ValueError("Invalid input. Please enter a number between 1 and 5.")
            nonlocal scoreEngagement, scoreConf, scoreContent
            scoreEngagement += responseInted * weightsEngagement[i]
            scoreConf += responseInted * weightsConf[i]
            scoreContent += responseInted * weightsContent[i]
            answer_submitted.set(True)
        except ValueError:
            error_label = ctk.CTkLabel(app, text="Invalid input. Please enter a number between 1 and 5.", text_color='red')
            error_label.configure(font=("Helvetica", 12))
            error_label.pack(pady=50, padx=20)
            app.after(2000, error_label.destroy)  # Schedule the label to be destroyed after 2 seconds

    ctk.answerEntry = ctk.CTkEntry(app, placeholder_text="Enter your answer (1-5)", width=200, border_color='blue')
    ctk.answerEntry.pack(pady=5, padx=20)
    answerButton = ctk.CTkButton(app, text="Next Question", fg_color="green")
    answerButton.pack(pady=10, padx=20)

    for i in range(len(questions)):
        question = questions[str(i)]
        ctk.questionLabel = ctk.CTkLabel(app, text=question)
        ctk.questionLabel.configure(font=("Helvetica", 12))
        ctk.questionLabel.pack(pady=5, padx=20)

        answerButton.configure(command=lambda i=i: validate_answer(i))
        app.bind('<Return>', lambda event: validate_answer(i))
        app.wait_variable(answer_submitted)

        print(ctk.answerEntry.get())

        ctk.answerEntry.delete(0, tkinter.END)
        ctk.questionLabel.destroy()

    ctk.quizInstruction.destroy()
    ctk.answerEntry.destroy()
    answerButton.destroy()
    ctk.quizInstruction.destroy()


    # Normalize scores so the maximum score for each trait is 9.0
    max_possible_score_engagement = sum([5 * weight for weight in weightsEngagement])  # Maximum score for engagement
    max_possible_score_conf = sum([5 * weight for weight in weightsConf])  # Maximum score for confidence
    max_possible_score_content = sum([5 * weight for weight in weightsContent])  # Maximum score for content

    multiplier_engagement = 9.0 / max_possible_score_engagement
    multiplier_conf = 9.0 / max_possible_score_conf
    multiplier_content = 9.0 / max_possible_score_content

    scoreEngagement *= multiplier_engagement
    scoreConf *= multiplier_conf
    scoreContent *= multiplier_content
    return scoreContent, scoreConf, scoreEngagement
        
    
def searchforVideo(searchterm,videoID, user):
    search_query = "SELECT ID, title FROM Video WHERE title LIKE %s OR tags LIKE %s"
    search_term_wildcard = f"%{searchterm}%"
    mycursor.execute(search_query, (search_term_wildcard, search_term_wildcard))
    results = mycursor.fetchall()

    if results:
        print("Search Results (with view count):")
        video_data = []

        for video_id, title in results:
            # Fetch view count from YouTube API
            video_id_str = str(video_id).strip("(),'")
            request = ytapisvc.videos().list(
                part='statistics',
                id=video_id_str
            )
            response = request.execute()
            view_count = int(response['items'][0]['statistics']['viewCount']) if response['items'] else 0
            video_data.append((video_id, title, view_count))

        # Sort video data by view count using mergesortFast
        sorted_videos = sorted(video_data, key=lambda x: x[2], reverse=True)

        # Print the top 5 videos by view count
        for video in sorted_videos[:5]:
            print(f"Title: {video[1]}, Views: {video[2]}")

        # Display the top 5 videos in the tkinter window
        for widget in app.winfo_children():
            widget.destroy()  # Clear the window before displaying results

        header_label = ctk.CTkLabel(app, text="Search Results", font=("Helvetica", 24))
        header_label.pack(pady=5, padx=20)

        # Add a return to main menu button
        def return_to_main_menu():
            loggedInDisplay(videoID, user)  # Replace with appropriate arguments if needed

        main_menu_button = ctk.CTkButton(app, text="Return to Main Menu", command=return_to_main_menu, fg_color="blue")
        main_menu_button.pack(pady=10, padx=20)

        # Create a frame to hold the thumbnails and titles
        results_frame = ctk.CTkFrame(app)
        results_frame.pack(pady=10, padx=20)

        for video in sorted_videos[:5]:
            video_id_str = str(video[0]).strip("(),'")
            thumbnail_url = f"https://img.youtube.com/vi/{video_id_str}/default.jpg"
            thumbnail = Image.open(requests.get(thumbnail_url, stream=True).raw)
            thumbnail = thumbnail.resize((160, 90))  # Resize the thumbnail to fit horizontally
            thumbnail = ImageTk.PhotoImage(thumbnail)  # Convert to PhotoImage for display

            # Create a sub-frame for each video
            video_frame = ctk.CTkFrame(results_frame)
            video_frame.pack(side=tkinter.LEFT, padx=10, pady=10)

            # Display video thumbnail
            thumbnail_label = ctk.CTkLabel(video_frame, image=thumbnail, text=' ')
            thumbnail_label.image = thumbnail  # Keep a reference
            thumbnail_label.pack()

            # Display video title
            title_label = ctk.CTkLabel(video_frame, text=video[1], font=("Helvetica", 12), justify=tkinter.CENTER, wraplength=160)
            title_label.pack()

            # Make the thumbnail clickable
            def on_thumbnail_click(video_id=video_id_str):
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(video_url)
                

            thumbnail_label.bind("<Button-1>", lambda event, video_id=video_id_str: on_thumbnail_click(video_id))

    else:
        print("No videos found matching the search term.")
        no_results_label = ctk.CTkLabel(app, text="No videos found matching the search term.", font=("Helvetica", 14), text_color="red")
        no_results_label.pack(pady=5, padx=20, anchor = "w")
        app.after(5000, no_results_label.destroy) 




    return None





            
            

    
            
            
    
def mergesortFast(videodata):
    views = [video[2] for video in videodata]
    if len(views) < 20:
        return sorted(views)
    # If too short to benefit from recursion, uses built int function
    result = []
    mid = int(len(views) / 2) # Finds the midpoint. recalculated in each function call in the stack
    y = mergesortFast(views[:mid]) # Sublist from start to midpoint is sorted
    z = mergesortFast(views[mid:]) # Sublist from midpoint to end is sorted
    i = 0 
    j = 0
    while i < len(y) and j < len(z):
        if y[i] > z[j]:
            result.append(z[j])
            j += 1
        else:
            result.append(y[i])
            i += 1
    result += y[i:]
    result += z[j:]
    print(result)
    return result




def validateUsernm(usern):
    if re.search('^(?=.*[A-Za-z])(?=.*\d)[a-zA-Z0-9._@#$!%*&]{8,30}$', usern) is None:
        error_label = ctk.CTkLabel(app, text="Username must include 1 letter, 1 number, and 8-30 total characters.", text_color="red")
        error_label.pack(pady=5, padx=20)
        app.after(2000, error_label.destroy)  
        return None
    return usern

def validatePass(passw):
    if re.search('^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&.]{8,30}$', passw) is None:
        error_label = ctk.CTkLabel(app, text="Password must include 1 letter, 1 number, 1 special character, and 8-30 total characters.", text_color="red")
        error_label.pack(pady=5, padx=20)
        app.after(2000, error_label.destroy)  # Destroy the error label after 2 seconds
        return None
    return passw
# Username and password regex validation


def painHash(string):

    # non-cryptographic hash algorithm that combines BWT, RLE, and a vernam cipher
    #BWT of the plaintext:
    string = string + '$'
    
    rotations = []
    # shift each char in the string up by one (pacman logic) to make all possible rotations
    for i in range(len(string)):
        rotation = string[i:] + string[:i]
        rotations.append(rotation)

    sorted_rotations = sorted(rotations)
    # sort all rotations alphabetically and use the last letter of each one to give the BWT
    bwt_result = ''.join(rotation[-1] for rotation in sorted_rotations)

    # the BWT is then run length encoded in the format 1E3C5D : ECCCDDDDD

    rle_result = ""
    n = len(bwt_result)
    indexinStr = 0
    while indexinStr < n:
        current_char = bwt_result[indexinStr]
        count = 1
        for j in range(indexinStr + 1, n):
            if bwt_result[j] == current_char:
                count += 1
            else:
                break
        rle_result += current_char + str(count)
        indexinStr += count

    # the RLE is then vernam ciphered, the One time pad is generated based on the BWT result and the exact same length as the data
    # if data is not at least 8 bytes, it is padded:

    key = []
    # Uses a shift to make the One time Pad for the vernam cipher to use
    for char in bwt_result:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            key_char = chr((ord(char) - shift_base + 13) % 26 + shift_base)
            key.append(key_char)
        elif char.isdigit():
            encrypted_char = chr((ord(char) - 43) % 10 + 48)
            key.append(encrypted_char)
        elif not char.isspace():
            key_char = chr((ord(char) - 32 + 5) % 95 + 32)
            key.append(key_char)
        else:
            key.append(char)  # Spaces remain unchanged

    # Uses a shift to make the One time Pad for the vernam cipher to use
    
    if len(rle_result) < len(key):
        for i in range(8 - len(rle_result)):
            rle_result += str(randint(1, 9))
    elif len(rle_result) > len(key):
        for i in range(len(rle_result) - len(key)):
            key += str(randint(1, 9))

    vnm_result = []
    hash = ""
    for i,char in enumerate(rle_result):
        asciiChar = ord(char)
        xor = ord(char)^ ord(key[i])
        
        vnm_result.append(xor)
    for elem in vnm_result:
        hash += str(elem)
    
    if len(hash) < 16:
        # padding for a 16 byte hash
        for i in range(16 - len(hash)):
            dps = 16-len(hash)
            poy = str(pi)
            buffer = poy.replace(".", "")
            hash += str(buffer[0:dps])
    elif len(hash) > 16:
        hash = hash[0:16]
    return hash



def commitnewUsertoSQL(usr):
    USERINSERTIGNOREQUERY = 'INSERT IGNORE INTO User (username,YoB,passhash,scoreContent,scoreConfidence,scoreEngagement) VALUES (%s, %s, %s, %s, %s, %s)'
    insert_tuple = (str(usr.username),
                    str(usr.YoB), 
                    str(usr.passhash),
                    str(usr._scoreContent),
                    (usr._scoreConf),
                    (usr._scoreEngagement))
    mycursor.execute(USERINSERTIGNOREQUERY, insert_tuple)
    db.commit()



mylabel = ctk.CTkLabel(app, text="Welcome to the Speaker Coach App",font=("Helvetica",24))
mylabel.pack(pady=5, padx=20)


username  = ''
password = ''
 ####################################
 ################
def signuploop(username,password,YOB):
    # validate year of birth 
    try:
        if 1900 < int(YOB) <= 2023:
            print(f'Year of birth is {YOB} and valid')
            username = validateUsernm(username)  # Validate username
            password = validatePass(password)
            passwordHash = painHash((password))  # Hash the password 
            
        else:
            mylabel = ctk.CTkLabel(app, text="Invalid year of birth. Please enter a 4-digit integer between 1900 and 2023.",text_color='red')
            mylabel.pack(pady=5, padx=20)

    except ValueError:
        mylabel = ctk.CTkLabel(app, text="Invalid year of birth. Please enter a 4-digit integer between 1900 and 2023.")
        mylabel.pack(pady=5, padx=20)
        return

    
    user = User(username,
    YOB,  # Validated year of birth
    passwordHash, 
    0, 0, 0)
    
    user.takeinitQuiz() 
    user.listAttrScores() 
    commitnewUsertoSQL(user) 
    
     # Commit the user to the database



def loginloop():  
    while True:
        # login loop
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        
        # hash the entered password 
        hashed_password = painHash(password)
        
        # searches for the username and hashed password
        mycursor.execute("SELECT * FROM User WHERE username = %s AND passhash = %s", (username, hashed_password))
        result = mycursor.fetchone()
        
        if result:
            print("Login successful!")
            break  # Exit the loop if login is successful
        else:
            print("Invalid username or password. Please try again.")
    return username, hashed_password, result[2]  # Return the username, hashed password, and year of birth 

    
# -------- MODEL --------

def get_user_by_credentials(username, hashed_pass):
    query = "SELECT * FROM User WHERE username = %s AND passhash = %s"
    mycursor.execute(query, (username, hashed_pass))
    return mycursor.fetchone()

def get_user_by_username(username):
    query = "SELECT * FROM User WHERE username = %s"
    mycursor.execute(query, (username,))
    return mycursor.fetchone()

def get_user_yob(username):
    mycursor.execute("SELECT YoB FROM User WHERE username = %s", (username,))
    result = mycursor.fetchone()
    return result[0] if result else None

def get_user_attributes(username):
    mycursor.execute("SELECT scoreContent, scoreEngagement, scoreConfidence FROM User WHERE username = %s", (username,))
    return mycursor.fetchone()

# -------- VIEW --------

def show_login_success():
    mylabel = ctk.CTkLabel(app, text="Login successful!", text_color="green")
    mylabel.pack(pady=5, padx=20)

def show_signup_success():
    success_label = ctk.CTkLabel(app, text="Signup successful! Welcome!", text_color="green")
    success_label.pack(pady=5, padx=20)
    app.after(3000, success_label.destroy)  # Automatically remove the label after 3 seconds

def show_login_failure(message):
    error_label = ctk.CTkLabel(app, text=message, text_color="red")
    error_label.pack(pady=5, padx=20)

# -------- CONTROLLER --------

def loginsignupdiscriminant(username, password, yob):
    hashedpass = None
    while not hashedpass:
        password = validatePass(password)  # Validate the password
        if password is None:
            return  # Wait for the user to re-enter the password and click the submit button again
        hashedpass = painHash(password)  # Hash the valid password
        
    validusernm = validateUsernm(username) # check whether username is valid.
    # validusernm will either be the username, or None
    while not validusernm:
        # if validusernm is None, prompt reinput and display the error label
        validusernm = validateUsernm(username)
        if validusernm is None:
            return

    existing_user = get_user_by_credentials(username, hashedpass)

    # Case 1: Existing user with matching credentials
    if existing_user:
        show_login_success()
        yob = get_user_yob(username)
        attributes = get_user_attributes(username)
        user_obj = instantiateUser(username, password, yob, attributes[0], attributes[1], attributes[2])
        _, grabquery = focusedTraitscore(user_obj)
        videoID, user = videoGetter(grabquery, user_obj)
        loggedInDisplay(videoID, user_obj)  # Pass user_obj to loggedInDisplay

    # Case 2: Username exists but password incorrect
    elif get_user_by_username(username):
        show_login_failure("Login failed: Incorrect password.")

    # Case 3: New user registration
    else:
        try:
            yob_int = int(yob)
            if 1900 < yob_int <= 2023:
                hashed_new_pass = painHash(password)
                new_user = User(username, yob_int, hashed_new_pass, 0, 0, 0)
                new_user.takeinitQuiz()
                commitnewUsertoSQL(new_user)
                show_signup_success()

            else:
                show_login_failure("Invalid year of birth. Please enter a valid 4-digit year.")
        except ValueError:
            show_login_failure("Year of birth must be numeric.")


#instantiate user object 
def instantiateUser(username,password,YOB,scoreEngagement,scoreConf,scoreContent):
    # Create a new user object with the provided attributes
    # Year of birth is a tuple and must be converted to int
    YOB = int(YOB[0]) if isinstance(YOB, tuple) else int(YOB)
    user = User(username,
                YOB,  # Validated year of birth
                password,  # Password is hashed using the painHash function
                scoreEngagement, 
                scoreConf, 
                scoreContent)
    
    fetchquery = "SELECT activityhistory FROM User WHERE username = %s"
    mycursor.execute(fetchquery, (username,))
    result = mycursor.fetchone()
    
    if result and result[0]:
        # splits the whole string into the nodes, then adds them in the same order preserving the order
        activity_history_str = result[0]
        activities = activity_history_str.split(', ')  
        for activity in activities:
            user._activityhistory.add_video(activity)
    return user

def focusedTraitscore(user):
    # Get the least trait score
    focusedTrait = user.leastTrait(user._scoreContent, user._scoreEngagement, user._scoreConf)
    # Handle the case where all scores are equal
    if user._scoreContent == user._scoreConf == user._scoreEngagement:
        print(f"All traits are equal. Randomly selected focused trait: {focusedTrait}")
        GRABQUERY = f"SELECT ID FROM Video WHERE tags LIKE '%{focusedTrait}%'"
        
        
    else:
        # Determine the focused trait based on the least score
        if focusedTrait == user._scoreContent:
            print("Content is your least trait")
            focusedTrait = 'content'
            GRABQUERY = "SELECT ID FROM Video WHERE tags LIKE '%research%'"
        elif focusedTrait == user._scoreEngagement:
            print("Engagement is your least trait")
            focusedTrait = 'engagement'
            GRABQUERY = "SELECT ID FROM Video WHERE tags LIKE '%self%'"
        elif focusedTrait == user._scoreConf:
            print("Confidence is your least trait")
            focusedTrait = 'confidence'
            GRABQUERY = "SELECT ID FROM Video WHERE tags LIKE '%confidence%'"
    
    print(f"Focused Trait: {focusedTrait}, Query: {GRABQUERY}")
    return focusedTrait, GRABQUERY

def videoGetter(GRABQUERY, user):
    mycursor.execute(GRABQUERY)
    result = mycursor.fetchall()
    print(f'row = {result}')
    
    # Fetch a random video ID from the GRABQUERY
    if result:
        randomindex = random.randint(0,(len(result)-1))
        random_video = result[randomindex]  # Randomly select a video ID from the result set
        videoID = random_video[0] if isinstance(random_video, tuple) else random_video
        print(f'Video Title Will Be {videotitlebyID(videoID)}')
        return videoID, user  # Call the loggedInDisplay function with the video ID
    else:
        print("No videos found for the focused trait.")
        loggedInDisplay(None, user)  # Pass None to indicate no video found
        
def loggedInDisplay(videoID, user):
    print(f"VideoID Passed to Loggedindisplay : {videoID}")
    for widget in app.winfo_children():
        widget.destroy()
    if videoID:
        videoIDstr = str(videoID)
        videoIDstr = videoID.replace("(", "").replace(")", "").replace(",", "").replace("'", "")  # remove any brackets and commas from the video ID
    else:
        print("No video to display.")
        return  # Exit the function if no video ID is provided
    header_label = ctk.CTkLabel(app, text="Main Menu", font=("Helvetica", 24))
    header_label.pack(pady=5, padx=20)

    # Display the video's thumbnail as a clickable link to the video
    thumbnail_url = f"https://img.youtube.com/vi/{videoID}/default.jpg"
    thumbnail = Image.open(requests.get(thumbnail_url, stream=True).raw)
    thumbnail = thumbnail.resize((320, 180))  # Resize the thumbnail
    thumbnail = ImageTk.PhotoImage(thumbnail)  # Convert to PhotoImage for display
    message_label = ctk.CTkLabel(app, text=f"Recommended Video: {videotitlebyID(videoID)}", justify=tkinter.CENTER)
    message_label.pack(pady=5, padx=50, anchor="e")  # Pack above the thumbnail
    message_label.configure(font=("Helvetica", 20))
    logout_button = ctk.CTkButton(app, text='Logout', command = logout, fg_color = 'Blue')
    logout_button.pack(pady = 5, padx = 20, anchor = 'ne') # Packs the logout button to the top right of the window
    
    
    userprofile_button = ctk.CTkButton(app, text='User Profile', command=lambda: profileDisplay(videoID, user), fg_color = 'blue')
    # Pack the button to the top left corner
    userprofile_button.pack(pady=5, padx=20, anchor="nw")  # Pack the button on the left side
    
    
    # Pack above the thumbnail
    thumbnail_label = ctk.CTkLabel(app, image=thumbnail, text=' ')
    thumbnail_label.image = thumbnail  # Keep a reference
    thumbnail_label.pack(pady=5, padx=50, anchor="e")  # Pack the thumbnail label on the right side
    def on_thumbnail_click(event=None):
        open_video(videoID, user)
        update_activity_history(user,videotitlebyID(videoID))
    thumbnail_label.bind("<Button-1>", on_thumbnail_click)
    
    retakeQuizButton = ctk.CTkButton(app, text='Retake Quiz', command = user.retakeinitQuiz, fg_color='green')
    retakeQuizButton.pack(pady=5, padx=20)
    # pack retake button under Main Menu
    # Bind click event to open video
    
    searchforVideoFrame = ctk.CTkFrame(app, width=400, height=300, corner_radius=10)
    searchforVideoFrame.pack(pady=5, padx=10, anchor = "w")
    searchforVideoEntry = ctk.CTkEntry(searchforVideoFrame, placeholder_text="Search for a video", width=200)
    searchSubmitButton = ctk.CTkButton(searchforVideoFrame, text="Search", command=lambda: searchforVideo(searchforVideoEntry.get(),videoID,user), fg_color="blue")
    searchforVideoEntry.pack(pady=5, padx=10, anchor = "w")
    searchSubmitButton.pack(pady=5, padx=10, anchor = "w")
    

def open_video(videoID,user):
    # Open the video in a new window using the YouTube API
    video_url = f"https://www.youtube.com/watch?v={videoID}"
    webbrowser.open(video_url)  # Open the video URL in the default web browser
    
    

    
def profileDisplay(videoID, user):
    for i in app.winfo_children():
        i.destroy()
        
    print(user.username)
    # Remove all widgets from the app window
    mainmenuButton = ctk.CTkButton(app, text='Main Menu', command=lambda: loggedInDisplay(videoID, user), fg_color = 'blue')
    # Pack the button to the top left corner
    mainmenuButton.pack(pady=5, padx=20, anchor="nw")  # Pack the button on the left side
    
    header_label = ctk.CTkLabel(app, text="User Profile", font=("Helvetica", 24))
    header_label.pack(pady=5, padx=20) 
    
    
    QUERY = "SELECT ActivityHistory FROM User WHERE username = %s"
    mycursor.execute(QUERY, (user.username,))
    
    result = mycursor.fetchall()
    acthistorystr = str(result).replace(',','\n').replace("[('",'').replace(")]",'')
    print(acthistorystr)
    # frame for the activity history
    activity_history_frame = ctk.CTkFrame(app, width=900, height=300, corner_radius=10)  
    activity_history_frame.pack(pady=10, padx=20, anchor="e") 

    # Add a label to display the activity history
    activity_history_label = ctk.CTkLabel(activity_history_frame, text="Activity History", font=("Helvetica", 18))
    activity_history_label.pack(pady=5, padx=10)

    # Display the user's activity history in the frame
    activity_history_text = ctk.CTkTextbox(activity_history_frame, width=900, height=300)
    activity_history_text.insert("1.0", acthistorystr)  # Insert the activity history string
    activity_history_text.configure(state="disabled")  # Make the textbox read-only
    activity_history_text.pack(pady=5, padx=10)
    
    
    # Left side frame for user details to show username, YOB, and scores
    user_details_frame = ctk.CTkFrame(app, width=400, height=300, corner_radius=10)
    user_details_frame.pack(pady=10, padx=20, anchor="w")  # Anchor to the left side of the screen

    # Add a label to display the user details
    user_details_label = ctk.CTkLabel(user_details_frame, text="User Details", font=("Helvetica", 18))
    user_details_label.pack(pady=5, padx=10)

    # Display the user's username
    username_label = ctk.CTkLabel(user_details_frame, text=f"Username: {user.username}", font=("Helvetica", 14))
    username_label.pack(pady=5, padx=10)

    # Display the user's year of birth
    print(f'Data of Birth issu {user.YoB}')
    yob_label = ctk.CTkLabel(user_details_frame, text=f"Year of Birth: {user.YoB}", font=("Helvetica", 14))
    yob_label.pack(pady=5, padx=10)

    # Display the user's scores
    scores_label = ctk.CTkLabel(user_details_frame, text="Scores:", font=("Helvetica", 16))
    scores_label.pack(pady=5, padx=10)

    engagement_label = ctk.CTkLabel(user_details_frame, text=f"Engagement: {user._scoreEngagement}", font=("Helvetica", 14))
    engagement_label.pack(pady=5, padx=10)

    confidence_label = ctk.CTkLabel(user_details_frame, text=f"Confidence: {user._scoreConf}", font=("Helvetica", 14))
    confidence_label.pack(pady=5, padx=10)

    content_label = ctk.CTkLabel(user_details_frame, text=f"Content: {user._scoreContent}", font=("Helvetica", 14))
    content_label.pack(pady=5, padx=10)
    
    
    # Friends List display underneath activity history
    add_friend_frame = ctk.CTkFrame(app, width=500, height=300, corner_radius=10)
    add_friend_frame.pack(pady=(5, 0), padx=20, anchor="e")  

    add_friend_label = ctk.CTkLabel(add_friend_frame, text="Add a Friend", font=("Helvetica", 18))
    add_friend_label.pack(pady=5, padx=10)
    
    friend_entry = ctk.CTkEntry(add_friend_frame, placeholder_text="Enter friend's username", width=200)
    friend_entry.pack(pady=5, padx=10)

    # Fetch the user's friends list and their most recent activity
    recent_activity = getFriendActivity(user.username)

    friends_list_frame = ctk.CTkFrame(app, width=400, height=200, corner_radius=10)
    friends_list_frame.pack(pady=5, padx=20, anchor="e") 
    
    friends_list_text = ctk.CTkTextbox(friends_list_frame, width=380, height=150)
    if recent_activity:
        friends_display = "\n".join([f"{friend}: {activity}" for friend, activity in recent_activity.items()])
        friends_list_text.insert("1.0", friends_display)
    else:
        friends_list_text.insert("1.0", "No friends or recent activity found.")  # Display a message if no friends or activity are found
    friends_list_text.configure(state="disabled")  # Make the textbox read-only
    friends_list_text.pack(pady=5, padx=10, anchor="e")
        
 
    friends_list_label = ctk.CTkLabel(friends_list_frame, text="Friends List", font=("Helvetica", 18))
    friends_list_label.pack(pady=5, padx=10)

    

    def add_friend():
        friend_username = friend_entry.get()
        if not friend_username:
            error_label = ctk.CTkLabel(add_friend_frame, text="Please enter a username.", text_color="red")
            error_label.pack(pady=5, padx=10)
            app.after(2000, error_label.destroy)  # Destroy the error label after 2 seconds
            return

        # Check if the friend exists in the database
        friend_query = "SELECT username FROM User WHERE username = %s"
        mycursor.execute(friend_query, (friend_username,))
        friend_result = mycursor.fetchone()

        if friend_result:
            # Add the friend to the user's friends list
            current_friends_query = "SELECT friends FROM User WHERE username = %s"
            mycursor.execute(current_friends_query, (user.username,))
            current_friends_result = mycursor.fetchone()

            if current_friends_result and current_friends_result[0]:
                current_friends = current_friends_result[0].split(',')
                if friend_username in current_friends:
                    error_label = ctk.CTkLabel(add_friend_frame, text="Friend already added.", text_color="red")
                    error_label.pack(pady=5, padx=10)
                    app.after(2000, error_label.destroy)
                    return
                current_friends.append(friend_username)
            else:
                current_friends = [friend_username]

            updated_friends = ','.join(current_friends)
            update_friends_query = "UPDATE User SET friends = %s WHERE username = %s"
            mycursor.execute(update_friends_query, (updated_friends, user.username))
            db.commit()

            success_label = ctk.CTkLabel(add_friend_frame, text="Friend added successfully!", text_color="green")
            success_label.pack(pady=5, padx=10)
            app.after(2000, success_label.destroy)  # Destroy the success label after 2 seconds
        else:
            error_label = ctk.CTkLabel(add_friend_frame, text="User not found.", text_color="red")
            error_label.pack(pady=5, padx=10)
            app.after(2000, error_label.destroy)  # Destroy the error label after 2 seconds

    add_friend_button = ctk.CTkButton(add_friend_frame, text="Add Friend", command=add_friend, fg_color="blue")
    add_friend_button.pack(pady=5, padx=10)
    


def getFriendActivity(username):
    # Fetch the user's friends list from the database
    friends_query = "SELECT friends FROM User WHERE username = %s"
    mycursor.execute(friends_query, (username,))
    friends_result = mycursor.fetchone()

    if friends_result and friends_result[0]:
        friends_list = friends_result[0].split(',')  # Assuming friends are stored as a comma-separated string
        recent_activity = {}

        # Fetch the most recent activity for each friend
        for friend in friends_list:
            activity_query = "SELECT ActivityHistory FROM User WHERE username = %s"
            mycursor.execute(activity_query, (friend,))
            activity_result = mycursor.fetchone()

            if activity_result and activity_result[0]:
                activity_history = activity_result[0].split(',')  # Assuming activity history is comma-separated
                recent_activity[friend] = activity_history[-1]  # Get the most recent video

        return recent_activity
    else:
        return None

def logout():
    for widget in app.winfo_children():
        widget.destroy()
    # remove all widgets and re initialise the login signup screen.

    signedoutDisplay()

def signedoutDisplay():
    usern_entry = ctk.CTkEntry(app, placeholder_text="Enter your username", width = 200)
    usern_entry.pack(pady=23, padx=20)
    passw_entry = ctk.CTkEntry(app, placeholder_text="Enter your password", show="*",  width = 200)
    passw_entry.pack(pady=26, padx=20)
    YOB_entry = ctk.CTkEntry(app, placeholder_text="Enter your year of birth")   
    YOB_entry.pack(pady=28, padx=20)
    submitButton = ctk.CTkButton(app, text='Submit', command =lambda : loginsignupdiscriminant(usern_entry.get(),passw_entry.get(),YOB_entry.get()), fg_color='green')
    submitButton.pack(pady=30, padx=20)
    app.bind('<Return>', lambda event: loginsignupdiscriminant(usern_entry.get(), passw_entry.get(), YOB_entry.get()))


usern_entry = ctk.CTkEntry(app, placeholder_text="Enter your username", width = 200)
usern_entry.pack(pady=23, padx=20)
passw_entry = ctk.CTkEntry(app, placeholder_text="Enter your password", show="*",  width = 200)
passw_entry.pack(pady=26, padx=20)
YOB_entry = ctk.CTkEntry(app, placeholder_text="Enter your year of birth")   
YOB_entry.pack(pady=28, padx=20)
submitButton = ctk.CTkButton(app, text='Submit', command =lambda : loginsignupdiscriminant(usern_entry.get(),passw_entry.get(),YOB_entry.get()), fg_color='green')
submitButton.pack(pady=30, padx=20)
app.bind('<Return>', lambda event: loginsignupdiscriminant(usern_entry.get(), passw_entry.get(), YOB_entry.get()))


app.mainloop()











