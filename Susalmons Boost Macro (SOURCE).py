import mss
import os, sys, socket#, signal
import time
import cv2
import numpy as np
import pygame
import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
#import pyautogui
from pynput.keyboard import Controller
#import psutil
#import win32pipe, win32file, pywintypes, win32security, win32api, win32con
import json
import threading
from multiprocessing.pool import ThreadPool
#import atexit

keyboard = Controller()
serverIP = ("", 8000)

with mss.mss() as sct:
    monitor = sct.monitors[1]  # Primary monitor
    monitorWidth = monitor["width"]
    monitorHeight = monitor["height"]
print(monitor)
username = os.getlogin()
print(username)

def updateJSON(data): 
    with open("settings.json", "w") as k:
        json.dump(data, k, indent=4)
    #print("Updating JSON")

if os.path.exists("settings.json"):
    with open("settings.json", "r") as f:
        settings = json.load(f)
else:
    settings = {}


definedIcons = ["precision", "redbloom"]

imgInfo = {
    "precision": {
        "width": 38,
        "backgroundTransparency": False,
        "backgroundColour": [180, 78, 143], #RGB = 143, 78, 180, HSV = 278, 57, 71, BGR = 180, 78, 143
        "foregroundColour": [27, 27, 30], #RGB = 30, 27, 27, HSV = 0, 10, 88, BGR = 27, 27, 30
        "tolerance": 10,
        "imageComparePath" : "comparison/precision.png",
        "timeRemaining": 0,
        "refresh": 60,
        "announceTime": 15,
        "announceDirectory": "announce/precision.wav",
    },
    "redbloom": {
        "width": 1,
        "backgroundTransparency": True,
        "backgroundColourDifference": 31.5,
        "backgroundColourAverage": [112.5, 112.5, 189.5], #RGB = 190, 112.5, 112.5, HSV = 0, 41, 75, BGR = 112.5, 112.5, 190
        "backgroundColourUpper": [154, 154, 221], #RGB = 221, 154, 154, HSV = 0, 30, 87, BGR = 154, 154, 221
        "backgroundColourLower": [91, 91, 158], #RGB = 158, 91, 91, HSV = 0, 42, 62, BGR = 91, 91, 158
        "foregroundPixelx": 19,
        "foregroundPixely": 10, # 44  43 243, 47  47 243, 44  43 243, 41  40 229
        "foregroundColour": [41, 40,229], #RGB = 236, 41, 42, HSV = 0, 82, 92, BGR = 42, 41, 236
        "tolerance": 15,
        "imageComparePath" : "comparison/redbloom.png",
        "foregroundColourTolerance": 10, #This is the tolerance for the foreground colour.
        "timeRemaining": 0,
        "refresh": 8, #In game time for how long the buff lasts. This is in seeconds.
        "announceTime": 4, #The time at which the audio will play to announce that the buff is about to run out. This is in seconds.
        "announceDirectory": "announce/blooms.wav",
    }
}


def geometrySplit():
    geom = root.geometry()
    size_part = geom.split("+")[0] 
    widthGeom, heightGeom = map(int, size_part.split("x"))
    return widthGeom, heightGeom

def transitionFunc(maximumWidth, maximumHeight, prevWidth, prevHeight):
    widthGeom, heightGeom = geometrySplit()
    if widthGeom == maximumWidth and heightGeom == maximumHeight:
        return
    
    if widthGeom < maximumWidth:
        widthGeom += int(maximumWidth / 8)
        if widthGeom > maximumWidth:
            widthGeom = maximumWidth
    elif widthGeom > maximumWidth:
        widthGeom -= int(maximumWidth / 6)
        if widthGeom < maximumWidth:
            widthGeom = maximumWidth

    if heightGeom < maximumHeight:
        heightGeom += int(maximumHeight / 8)
        if heightGeom > maximumHeight:
            heightGeom = maximumHeight
    elif heightGeom > maximumHeight:
        heightGeom -= int(maximumHeight / 6)
        if heightGeom < maximumHeight:
            heightGeom = maximumHeight
    root.geometry(f"{widthGeom}x{heightGeom}")
    root.after(1, transitionFunc, maximumWidth, maximumHeight, prevWidth, prevHeight)

currentGeometry = {}



def autoResizeTab(event):
    selected = notebook.index(notebook.select())
    if selected == 0:
        currentGeometry["width"], currentGeometry["height"] = geometrySplit()
        transitionFunc(200, 130, currentGeometry["width"], currentGeometry["height"])
    elif selected == 1:
        currentGeometry["width"], currentGeometry["height"] = geometrySplit()
        transitionFunc(300, 400, currentGeometry["width"], currentGeometry["height"])
    else:
        currentGeometry["width"], currentGeometry["height"] = geometrySplit()
        transitionFunc(600, 350, currentGeometry["width"], currentGeometry["height"])

colour = "#252525"
colour2 = "#151515"
colour3 = "#353535"
colourFG = "#fffefe"
#GUI STUFF

root = tk.Tk()
root.title("Buff Tracker")
root.geometry("200x100")
root.configure(bg="lightblue")
geometrySplit()
root.attributes("-topmost", True) #Keeps the window on top of all other windows



"""root.overrideredirect(True)  # removes OS title bar
root.geometry("400x300+100+100")

# Create a custom top bar
top_bar = tk.Frame(root, bg=colour, height=30)
top_bar.pack(fill="x")

title = tk.Label(top_bar, text="Buff Tracker", bg=colour, fg="white", font=("Consolas", 12))
title.pack(side="left", padx=5)

# Optional: add your own close button
def close_window():
    root.destroy()

def min_window():
    root.withdraw()

close_btn = tk.Button(top_bar, text="x", command=close_window, bg=colour, fg="white")
close_btn.pack(side="right")

min_btn = tk.Button(top_bar, text="-", command=min_window, bg=colour, fg="white")
min_btn.pack(side="right")"""

themeValues = {"Dark":["#252525", "#151515", "#353535", "#fffefe"], "Light": ["#ffefef", "#ffdfdf", "#ffffff", "#151515"]}
themeOptions = ["Dark", "Light"]

relayColour = "#803E3E"
relayFG = "#fffefe"

style = ttk.Style()
style.theme_use("clam")

def updateTheme(colour, colour2, colour3, colourFG):
    print("Colours are updating")
    style.configure("Custom.TEntry", foreground=colourFG, fieldbackground=colour3)
    style.configure("TFrame", background=colour)
    style.configure("Custom.TLabel", foreground=colourFG, background=colour)
    style.configure("Custom2.TLabel", foreground=colourFG, background=colour2)
    style.configure("Custom3.TLabel", foreground=colourFG, background=colour3)
    style.configure("Custom4.TLabel", foreground=relayFG, background=relayColour)
    style.configure("CustomNotebook.TNotebook", background=colour, borderwidth = 0)
    style.configure("CustomNotebook.TNotebook.Tab", background=colour, borderwidth = 0, padding = [10,5])
    pipelineBox.itemconfig(rect, fill=colour2, outline=colour)



notebook = ttk.Notebook(root, style="CustomNotebook.TNotebook")
notebook.pack(fill="both", expand=True, padx=0, pady=0)

tabFrames = {}

tabNames = ["tab0", "tab1", "tab2"]
tabNamesText = {"tab0": "Show", "tab1": "Accounts", "tab2": "Settings"}

for tab in tabNames:
    frame = ttk.Frame(notebook, style="TFrame")
    notebook.add(frame, text=tabNamesText[tab])
    tabFrames[tab] = frame

hotbarEntryBoxResult = {}

#Example formatting
#hotbarComboBoxResult = {"subTab" { 
#                           "hotbarSlot": "a"
#                               }
#                       }

#suggestions = ["Snowflakes", "Glitter", "Coconuts", "Stingers", "Gumdrops", ""] #Unused
hotbarLength = 7

AccHBDict = {}

#Nested Notebook for each account control
subNotebook = ttk.Notebook(tabFrames["tab1"], style="CustomNotebook.TNotebook")
subNotebook.pack(fill="both", expand=True)

accountList = []

subTabFrames = {}

hotbarTextLabels = {}

def drawSubTabs(dict):
    global connInfoDict, hbnu
    print(dict)
    for subTab in list(subTabFrames.keys()):
        idx = int(subTab.replace("subTab", ""))
        if idx >= len(accountList):
            frame = subTabFrames.pop(subTab)
            subNotebook.forget(frame)

    for i, accountName in enumerate(dict):
        print(i, accountName)
        subTab = f"subTab{i}"
        if subTab not in subTabFrames:
            frame = ttk.Frame(subNotebook, style="TFrame")
            subNotebook.add(frame, text=accountName)
            subTabFrames[subTab] = frame
        else:
            frame = subTabFrames[subTab]
        for widget in frame.winfo_children():
            widget.destroy()

        for hotbarNumber in range(hotbarLength):
            entryboxHeight = hotbarNumber * 36 + 5
            hotbarLabel = ttk.Label(frame, text=str(hotbarNumber + 1), font=("Consolas", 18), style="Custom.TLabel")
            hotbarLabel.place(x=0, y=entryboxHeight)
            #hotbarLabel.grid(row=hotbarNumber, column=0, padx=2, pady=2, sticky="w")

            if accountName == "Main":
                entryboxWidth = 260
                entryboxX = 25
            else:
                entryboxWidth = 164
                entryboxX = 126
            
            entryBox = ttk.Entry(frame, font=("Consolas", 18), style="Custom.TEntry")
            entryBox.place(x=entryboxX, y=entryboxHeight, width=entryboxWidth, height=30)
            if accountName not in settings["Accounts"]:
                settings["Accounts"].update({accountName: {}})
            if settings["Accounts"][accountName] != {}:
                if settings["Accounts"][accountName][str(hotbarNumber)] != "":
                    entryBox.insert(0, settings["Accounts"][accountName][str(hotbarNumber)])

            if accountName not in hotbarEntryBoxResult:
                hotbarEntryBoxResult[accountName] = {}
            #print(type(hotbarTextLabels))
            hotbarEntryBoxResult[accountName][hotbarNumber] = entryBox
            hbNumStr = str(hotbarNumber)
            #if accountName in AccHBDict:
            lbl = 0
            if accountName != "Main":
                if hbNumStr in connInfoDict[accountName]["hotbar"].keys():
                    lbl = ttk.Label(frame, text=connInfoDict[accountName]["hotbar"][hbNumStr], font=("Consolas", 12), style="Custom.TLabel")
                    lbl.place(x=23, y=entryboxHeight + 5)
            #hotbarTextLabels.setdefault(accountName, {})
            #hotbarTextLabels[accountName][hbNumStr] = lbl

keybindUpdate = False

def submitButtonFunc(event=None):
    global keybindUpdate, hotbarEntryBoxResult, connInfoDict, msgList
    print("Key was pressed")
    keybindUpdate = True
    #settings["Accounts"] = []
    for acc in hotbarEntryBoxResult:
        info = None
        for i in hotbarEntryBoxResult[acc]:
            if info != None:
                info = info + "." + hotbarEntryBoxResult[acc][i].get()
            else:
                info = hotbarEntryBoxResult[acc][i].get()
        if acc != "Main":
            info = info.encode("utf-8")
            connInfoDict[acc]["conn"].sendto(info, connInfoDict[acc]["addr"])
        settings["Accounts"][acc] = {}
        for i in hotbarEntryBoxResult[acc]:
            settings["Accounts"][acc][i] = hotbarEntryBoxResult[acc][i].get()
        print(settings["Accounts"][acc])

    msgList = []
    myList = []
    for hb in hotbarEntryBoxResult["Main"]:
        myList.append(hotbarEntryBoxResult["Main"][hb].get())
    msgList = myList


    

submitButton = ttk.Button(tabFrames["tab1"], text=f"Start  (F1)", style="Custom4.TLabel", command=submitButtonFunc, padding=(5,5))
submitButton.place(x=10, y=325, width=100, height=30)
root.bind("<F1>", lambda event: submitButtonFunc(event))

def stopButtonFunc(event=None):
    global keybindUpdate, hotbarEntryBoxResult, connInfoDict, msgList
    print("Key was pressed")
    keybindUpdate = "stop"
    for acc in hotbarEntryBoxResult:
        if acc != "Main":
            connInfoDict[acc]["conn"].sendto("stop".encode("utf-8"), connInfoDict[acc]["addr"])

    msgList = []
    myList = []
    for i in range(hotbarLength):
        myList.append("")
    msgList = myList
    
stopButton = ttk.Button(tabFrames["tab1"], text=f"Stop   (F2)", style="Custom4.TLabel", command=stopButtonFunc, padding=(5,5))
stopButton.place(x=120, y=325, width=100, height=30)
root.bind("<F2>", lambda event: stopButtonFunc(event))

if "Accounts" not in settings:
    settings["Accounts"] = {"Main": {}}

settings["ActiveAccounts"] = ["Main"]

drawSubTabs(settings["ActiveAccounts"])

root.resizable(False, False) #Prevents the window from being resized

notebook.bind("<<NotebookTabChanged>>", autoResizeTab)


themeText = ttk.Label(tabFrames["tab2"], text="Set Theme", font=("Consolas", 8), style="Custom.TLabel")
themeText.place(x=5, y=45)
themeComboBox = ttk.Combobox(tabFrames["tab2"], values=themeOptions, width=12)
themeComboBox.place(x=5, y=60)

accountText = ttk.Label(tabFrames["tab2"], text="Set Account Type", font=("Consolas", 8), style="Custom.TLabel")
accountText.place(x=5,y=5)
options = ["Main", "Alt"]
accountType = ttk.Combobox(tabFrames["tab2"], values=options, width=12)
accountType.place(x=5, y=20)

if "AccountType" not in settings:
    accountType.set("Alt")
    settings["AccountType"] = accountType.get()
    updateJSON(settings)
else:
    accountType.set(settings["AccountType"])
pipelineBox = tk.Canvas(tabFrames["tab2"], width=145, height=370)
pipelineBox.place(x=455, y=0)
rect = pipelineBox.create_rectangle(0, 0, 145, 370, fill=colour2, outline=colour)
pipelineText = ttk.Label(tabFrames["tab2"], text="Linked\nAccounts:", font=("Consolas", 14), style="Custom2.TLabel")
pipelineText.place(x=460,y=5)

connectedAccountLabels = {}

def redrawRelay(accountsList):
    global connectedAccountLabels
    # Normalize to list
    if isinstance(accountsList, str):
        accounts = [accountsList]
    else:
        accounts = accountsList

    # Remove labels for accounts that no longer exist
    for name in list(connectedAccountLabels.keys()):
        if name not in accounts:
            connectedAccountLabels[name].destroy()
            del connectedAccountLabels[name]

    # Update or create labels
    for i, accname in enumerate(accounts):
        yval = i * 26 + 50

        if accname in connectedAccountLabels:
            # Update existing label text
            connectedAccountLabels[accname].config(text=accname)
            connectedAccountLabels[accname].place(x=460, y=yval)
        else:
            # Create new label
            lbl = ttk.Label(
                tabFrames["tab2"],
                text=accname,
                style="Custom4.TLabel",
                font=("Consolas", 12)
            )
            lbl.place(x=460, y=yval)
            connectedAccountLabels[accname] = lbl

redrawRelay(settings["ActiveAccounts"])

label = ttk.Label(tabFrames["tab0"], text="Buff Tracker is running...", font=("Consolas", 18), style="Custom.TLabel")
label.pack()

if "Theme" not in settings:
    updateTheme(themeValues["Dark"][0], themeValues["Dark"][1], themeValues["Dark"][2], themeValues["Dark"][3])
    settings["Theme"] = "Dark"
    themeComboBox.set("Dark") #Sets a default value for the combobox
    print("Theme does not exist")
else:
    theme = settings["Theme"]
    themeComboBox.set(theme) #Sets the value of the combobox to the last known colour
    print("Theme exists", theme)
    updateTheme(themeValues[theme][0], themeValues[theme][1], themeValues[theme][2], themeValues[theme][3])





def resourcePath(relative_path):
    base = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base, relative_path)

#Audio Setup

updatedTimer = {icon: imgInfo[icon]["timeRemaining"] for icon in imgInfo}

previousTime = time.time()


#ICONS

#FOR REAL TIME
iconTop:int = 58
iconLeft:int = 0 
iconLength:int = 38
iconOverlapVal = 0 #0 was the best

monitor = 0 #Defines which monitor to look at
#folderName = "BuffBarScreenshots"
#os.makedirs(folderName, exist_ok=True)

hotbarSize = 7
hotbarInfo = {
    "background":{
        "backgroundColour": [200,200,200]#[216,216,216], #On a perfectly black background
    },
    "hotbarItems": ["Snowflakes, CloudVial, JellyBean, Gumdrops, BloomShaker"],
    "hotbarPositions": {}
}

def hotbarCheck():
    barTop = monitorHeight - 150
    barLeft = int(round((monitorWidth * 0.5) - 262))
    barWidth = 1536 - 1018 - 2 #The -2 is for the 2 pixels on the left and right
    barHeight = 70 - 2 #The -2 is for the 2 pixels on the top and bottom
    width = 49

    captureArea = {"top": barTop, "left": barLeft, "width": barWidth, "height": barHeight}
    with mss.mss() as sct:
        sct_image = sct.grab(captureArea)
        sct_image = np.array(sct_image)[:, :, :3]
        for number in range(hotbarSize):
            x1 = (number * 75) + 10 #Best 75
            x2 = x1 + width
            y1 = 10
            y2 = 69 - y1
            image = sct_image.copy()
            image = image[y1:y2, x1:x2]

            baseBackground = np.array(hotbarInfo["background"]["backgroundColour"], dtype=np.int16)

            mask = np.all(baseBackground <= image, axis=2)
            maskedIconCapture = image
            maskedIconCapture[mask] = [0,0,0]
            hotbarList = hotbarInfo["hotbarItems"]
            hotbarList = hotbarList[0].split(", ")
            #print(hotbarList)
            for icon in hotbarList:
                #print(icon)
                #cv2.imwrite(resourcePath(f"{number}.png"), maskedIconCapture)
                comparison = cv2.imread(resourcePath(f"comparison/{icon}.png"))[:,:,:3]
                #Template Matching
                gray_img = maskedIconCapture#cv2.cvtColor(maskedIconCapture, cv2.COLOR_BGR2GRAY)
                gray_template = comparison#cv2.cvtColor(comparison, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(gray_img, gray_template, cv2.TM_CCOEFF_NORMED)
                confidence = np.max(result)

                #cv2.imshow(f"grayTemplate", gray_template)
                if confidence > 0.55:
                    #print(f"Template matching confidence for {icon} at {number}: {confidence}")
                    hotbarInfo["hotbarPositions"][number] = icon
                    print(hotbarInfo)
    t2.start()
    

        #print(hotbarInfo["hotbarPositions"])
                #cv2.imwrite(f"{icon}-{number}-{confidence:.3f}.png", gray_img) #DEBUG


def loadAudio():
    global soundprecision, soundredbloom, precisionChannel, redBloomChannel
    pygame.init()
    pygame.mixer.init()

    soundprecision = pygame.mixer.Sound(resourcePath(imgInfo["precision"]["announceDirectory"]))
    soundredbloom = pygame.mixer.Sound(resourcePath(imgInfo["redbloom"]["announceDirectory"]))

    precisionChannel = None
    redBloomChannel = None


def playAudio(elapsed):
    global soundprecision, soundredbloom, precisionChannel, redBloomChannel
    for icon in updatedTimer:
        updateByElapsed(elapsed, icon)
        #print(f"{updatedTimer[icon]} '{icon}' has been updated.")
        if 0 < updatedTimer["precision"] <= imgInfo["precision"]["announceTime"]:
                if precisionChannel is None or not precisionChannel.get_busy(): #Checks if audio is already playing
                    precisionChannel = soundprecision.play()#print("Playing precision sound")#precisionChannel = soundprecision.play()
        if 0 < updatedTimer["redbloom"] <= imgInfo["redbloom"]["announceTime"]:
                if redBloomChannel is None or not redBloomChannel.get_busy(): #Checks if audio is already playing
                    redBloomChannel = soundredbloom.play()#Updates the screenshot every second, this is a recursive function call

def checkActiveScreen():
    # Get all windows

    # Search for a specific window title
    target_title = "Roblox"
    windows = gw.getAllWindows()
    for w in windows:
        if w.title == target_title:
            win = w
            if win.left == -8:
                iconTop = 81
            elif win.left == 0:
                iconTop = 58
            else:
                win.maximize()
                iconTop = 58
    
    return iconTop

def updateByElapsed(elapsed, icon):
    if icon in updatedTimer:                        
        updatedTimer[icon] = updatedTimer[icon] - elapsed

        if updatedTimer[icon] > 0:
            print(f"'{icon}' timer is at {round(updatedTimer[icon], 0)}s")
        else:
            #print(f"'{icon}' has reached 0")
            updatedTimer[icon] = max(updatedTimer[icon], 0) #Ensures that the timer does not go below 0

def opaqueBackgroundTimer(iconCapture, icon):
    target_colour = np.array(imgInfo[icon]["backgroundColour"], dtype=np.uint8)
    mask = np.all(iconCapture == target_colour, axis=2)
    iconCapture[mask] = [255,255,255]
    white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = np.all(iconCapture == white, axis=2) #CHATGPT SECTION
    white_per_row = np.sum(white_mask, axis=1)
    #print(f"White Per Row: {white_per_row}")
    first_row = np.where(white_per_row > 0)[0]
    
    #rows_with_background = np.where(np.any(mask, axis=1))[0]
    #print(first_row)
    if len(first_row) == 0:
        first_row = int(iconLength)
    else:
        first_row = first_row[0]
    #print(f"First Row {first_row}")
    #print(f"White Per Row {white_per_row}")
    return first_row

def transparentBackgroundTimer(iconCapture, icon, **kvargs):
    lower = np.array(imgInfo[icon]["backgroundColourLower"], dtype=np.uint8)
    upper = np.array(imgInfo[icon]["backgroundColourUpper"], dtype=np.uint8)
    #icon_int = iconCapture.astype(np.uint8)
    #Timer = kvargs.get("Timer", 5)
    mask = np.all((lower <= iconCapture) & (iconCapture <= upper), axis=2)
    iconCapture[mask] = [255,255,255]
    white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = np.all(iconCapture == white, axis=2) #CHATGPT SECTION
    white_per_row = np.sum(white_mask, axis=1)

    #print(type(white_per_row))
    first_row = np.where(white_per_row > 0)[0]
    #print(len(first_row))
    if len(first_row) == 0:
        first_row = int(iconLength)
    else:
        first_row = first_row[0]

    #print(f"First Row {first_row} with type {type(first_row)}")
    #print(f"White Per Row {white_per_row}")

    return first_row

def soundPlayer(updatedTimer, icon):
    if 0 < updatedTimer[icon] <= imgInfo[icon]["announceTime"]:
        if not f"sound{icon}".get_busy(): #Checks if audio is already playing
            f"sound{icon}".play()

def updateScreenshot():
    global previousTime, redBloomChannel, precisionChannel, iconTop
    currentTime = time.time()
    elapsed = currentTime - previousTime
    elapsed = elapsed
    previousTime = time.time()
    #print(elapsed)
    failText = None
    if accountType.get() == "Main":
        with mss.mss() as sct:
            try:
                iconTop = checkActiveScreen()
                failText = None
            except:
                failText = "Roblox Is\nNot Open"
                #print(failText)
            
            captureArea = {"top": iconTop, "left": iconLeft, "width": monitorWidth, "height": int(iconLength)} #Defines the screenshotting area using a dictionary.

            sct_image = sct.grab(captureArea) #Takes the image and stores in memory
            isInList = []
            iconImage = {}
            iconAmount = int((monitorWidth // iconLength) - 1)
            for amount in range(iconAmount):
                x1:int = int(round(amount * (iconLength - iconOverlapVal)))
                x2:int = int(round(x1 + iconLength))
                y1 = 0
                y2 = int(round(iconLength))
        
                iconCapture = np.array(sct_image)[:, :, :3] #Format Screenshot
                iconCapture = iconCapture[y1:y2, x1:x2] #Crop the screenshot to only include the current icon
                for icon in definedIcons:
                    maskedIconCapture = iconCapture.copy()
                    base = np.array(imgInfo[icon]["foregroundColour"], dtype=np.int16)
                    tolerance = imgInfo[icon]["tolerance"]

                    upper = np.clip(base + tolerance, 0, 255).astype(np.uint8)
                    lower = np.clip(base - tolerance, 0, 255).astype(np.uint8)

                    mask = np.all((lower <= iconCapture) & (iconCapture <= upper), axis=2)
                    mask = ~mask
                    maskedIconCapture[mask] = [255,255,255]
                    

                    comparison = cv2.imread(resourcePath(imgInfo[icon]["imageComparePath"]))
                    #Template Matching
                    gray_img = cv2.cvtColor(maskedIconCapture, cv2.COLOR_BGR2GRAY)
                    gray_template = cv2.cvtColor(comparison, cv2.COLOR_BGR2GRAY)
                    result = cv2.matchTemplate(gray_img, gray_template, cv2.TM_CCOEFF_NORMED)
                    confidence = np.max(result)

                    #cv2.imshow(f"grayTemplate", gray_template)

                    if confidence > 0.75 and icon not in isInList: #Precision threshold is around 0.4
                        isInList.append(icon)
                        iconImage[icon] = iconCapture
                        print(f"Template matching confidence for {icon} at {amount}: {confidence}")

        if True: #>= 1:
            #print(f"{isInList}")

            for icon in isInList: 
                iconCapture = iconImage[icon]
                if imgInfo[icon]["backgroundTransparency"] == True:
                    first_row = transparentBackgroundTimer(iconCapture, icon)
                if imgInfo[icon]["backgroundTransparency"] == False:
                    first_row = opaqueBackgroundTimer(iconCapture, icon)
                #print(f"First Row: {first_row}")

                #Calculating Remaining time
                remaingingTime = (1 - (int(first_row) / int(iconLength))) * imgInfo[icon]["refresh"]

                #print(f"{remaingingTime:.1f}")

                #updateByElapsed(updatedTimer, elapsed, icon)
                updatedTimer[icon] = max(remaingingTime, 0) #Ensures that the timer does not go below 0
        playAudio(elapsed)
    else:
        failText = "ALT ACCOUNT"



        #soundPlayer(updatedTimer, icon)
    text = text = "\n".join(
        f"{k}: {int(round(updatedTimer[k], 0))}s"
        for k in definedIcons
    )

    if failText != None:
        text = failText

    combo = themeComboBox.get()

    if combo == "Dark" or combo == "Light":
        if "Theme" in settings:
            if combo != settings["Theme"]:
                settings["Theme"] = combo
                updateTheme(themeValues[combo][0], themeValues[combo][1], themeValues[combo][2], themeValues[combo][3])
                print(settings["Theme"])

    settings["AccountType"] = accountType.get()
    

    updateJSON(settings)

    label.config(text=text)
    root.after(100, updateScreenshot) 

enable = True

emptyList = []
for i in range(hotbarLength):
    emptyList.append("")
msgList = emptyList

def keypresser() -> None:
    global msgList
    timer = 0
    while True:
        time.sleep(1)
        try:
            checkActiveScreen()
            print("Roblox Open")
            print(timer)

            timer += 1
            if msgList == emptyList:
                timer = 0
            for i in range(len(msgList)):
                if msgList[i] != "":
                    if timer % int(msgList[i]) == 0:
                        keyboard.press(str(i + 1))
                        keyboard.release(str(i + 1))
        except:
            print("Roblox Closed")


#V2 Client-Server system
def connectClients(server, dict,) -> tuple:
    #while True:
        #time.sleep(1)
        try:
            #print("waiting")
            a, b = server.accept()
            if a != None:
                #print("account connected!")
                length = len(dict)
                return (length, a, b)
            #print(dict)
            
        except BlockingIOError as e:
            if e.winerror != 10035:
                raise
            return None

def pipelineClient():
    global hotbarLength, enable, msgList
    keythread = threading.Thread(target=keypresser)
    keythread.start()

    client = socket.create_connection(serverIP)

    hotbarInfo["hotbarPositions"]
    hotbarKeys = None
    hotbarValues = None

    for i in hotbarInfo["hotbarPositions"].keys():
        if hotbarKeys == None:
            hotbarKeys = str(i)
            hotbarValues = hotbarInfo["hotbarPositions"][i]
        else:
            hotbarKeys = hotbarKeys + "," + str(i)
            hotbarValues = hotbarValues + "," + hotbarInfo["hotbarPositions"][i]

    info = f"{username}.{hotbarKeys}.{hotbarValues}"
    print(info)
    client.send((info).encode("utf-8"))

    #Listens for messages as soon as hotbarinfo is sent
    while True:
        try:
            message = client.recv(1024*8).decode("utf-8")
            
            print(message)
            msgList = []
            if message == "stop":
                for i in range(hotbarLength):
                    msgList.append("")
                    enable = False
            else:
                msgList = message.split(".")
                enable = True
            print(msgList)

        except:
            raise


connInfoDict = {}
tempAddrStorage = []

def pipelineServer():
    global connInfoDict, tempAddrStorage, settings, server

    keythread = threading.Thread(target=keypresser)
    keythread.start()

    server = socket.create_server(serverIP, family=socket.AF_INET)
    #server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Alternative Server Creation
    #server.bind(serverIP)
    server.listen(6) #Connect up to 6 accounts
    server.settimeout(0) #Sets server to non-blocking

    """connect = threading.Thread(target=connectClients, daemon=True, args=(server, connInfoDict))
    connect.start()"""

    pool = ThreadPool(processes=1)
    while True:
        time.sleep(1)
        asyncResult = pool.apply_async(connectClients, (server, connInfoDict))
        resultVal = asyncResult.get()
        #print(resultVal)
        if resultVal != None:
            index, conn, addr = resultVal
            #print(resultVal, type(resultVal), index)
            tempAddrStorage = []
            tempAddrStorage.append((conn, addr))
        if tempAddrStorage != []:
            #print("temp storage =", tempAddrStorage)
            msg = tempAddrStorage[0][0].recv(1024*8) #Attemps to read any new messages
            if msg != 0: #Confirms whether the message exists
                msg = msg.decode("utf-8")
                msgUser, hotbarDict = socketDecoder(msg)
                connInfoDict[msgUser] = {}
                connInfoDict[msgUser]["conn"] = conn
                connInfoDict[msgUser]["addr"] = addr
                connInfoDict[msgUser]["hotbar"] = hotbarDict
                if msgUser not in settings["ActiveAccounts"]:
                    settings["ActiveAccounts"].append(msgUser)
                redrawRelay(settings["ActiveAccounts"])
                drawSubTabs(settings["ActiveAccounts"])
                tempAddrStorage = []
            print("dict =", connInfoDict)
            


def socketDecoder(string) -> tuple:
    user, key, value = string.split(".")
    dictionary = {}
    key = key.split(",") #Creates a list of each individual key
    value = value.split(",") #Creates a list of each individual value
    #print(user, key, value)
    for i in range(len(key)):
        dictionary[key[i]] = value[i]
    
    return (str(user), dict(dictionary))



t = threading.Thread(target=pipelineServer, daemon=True)
t2 = threading.Thread(target=pipelineClient, daemon=True)
hotbarThread = threading.Thread(target=hotbarCheck, daemon=True)



updateScreenshot()
if accountType.get() == "Main":
    #pipelineServer()
    t.start()
    loadAudio()
if accountType.get() == "Alt":
    hotbarThread.start()
    #t2.start()

root.mainloop()