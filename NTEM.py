'''

███╗   ██╗████████╗███████╗
████╗  ██║╚══██╔══╝██╔════╝
██╔██╗ ██║   ██║   █████╗  
██║╚██╗██║   ██║   ██╔══╝  
██║ ╚████║   ██║   ███████╗
╚═╝  ╚═══╝   ╚═╝   ╚══════╝ v0.1
by @Zhyov on GitHub

'''

# [ Modules ]
import os, time, msvcrt, json
from threading import Thread

# [ "File exists" test ]
if not os.path.exists(f'{__file__[:(-len(os.path.basename(__file__))-1)]}\data\{os.path.basename(__file__)[:-3]}'):
    os.system('cls')
    print("This NTE doesn\'t have any data! Have you managed it correctly through the NTEM file?")
    time.sleep(6)
    exit()

# [ Variables ]
# [[ Hard-coded ]]
# [[[ Functionality ]]]
current = 1
currentStyle = 0

# [[[ Console ]]]
width = os.get_terminal_size().columns
length = os.get_terminal_size().lines
resizeFlag = False

# [[[ Constants ]]]
fileName = os.path.basename(__file__)[:-3]
styles = [['║', '═', '╔', '╗', '╚', '╝', '╠', '╣'], ['│', '─', '┌', '┐', '└', '┘', '├', '┤']]

# [[ JSON variables ]]
directory = f'{__file__[:(-len(os.path.basename(__file__))-1)]}'
settings = json.load(open(f'{directory}\data\{fileName}\Settings.json'))

# [[[ Settings ]]]
title = settings["title"]

# [ Functions ]
# [[ Handle ]]
# [[[ Threaded ]]]
def handleSize():
    global width, length, resizeFlag
    while True:
        newWidth = os.get_terminal_size().columns
        newLength = os.get_terminal_size().lines
        if newWidth != width or newLength != length:
            width = newWidth
            length = newLength
            resizeFlag = True
        time.sleep(.001)

# [[[ Non-threaded ]]]
def handleFormat():
    global resizeFlag, width, length
    newWidth = os.get_terminal_size().columns
    newLength = os.get_terminal_size().lines
    if newWidth != width or newLength != length:
        width = newWidth
        length = newLength
        resizeFlag = True
    if resizeFlag:
        os.system('cls')
        print("\033[H", end='')
        resizeFlag = False

def handleSelection(index : int, length : int, static : bool = False):
    if static: return 1
    if index < 1: return 1
    elif index > length: return length
    else: return index

def handleArrows(direction : str, length : int):
    global current
    if direction == 'down': current = handleSelection(current + 1, length)
    elif direction == 'up': current = handleSelection(current - 1, length)

def handleOption(type : str, index : int):
    if index == current:
        if type == 'start': return ' \033[7m'
        elif type == 'end': return ' \033[0m'
    else: return ' '

def handleStyle(type : int):
    global currentStyle, styles
    return styles[currentStyle][type]

def handlePanelUpdate(file : str):
    dir1 = f'{directory}\data\{file}\panels'
    dir2 = f'{directory}\data\{fileName}\panels\{file}\{file}Manage.json'
    data = json.load(open(dir2))
    oldOptions = data["options"]
    oldFunctions = data["functions"]
    addOptions = []
    addFunctions = []
    panelCount = 0
    for panel in [x[2] for x in os.walk(dir1)][0]:
        panelData = json.load(open(f'{dir1}\{panel}'))
        panelCount += 1
        added = False
        for option in oldOptions:
            if option != f'{panelData["name"]} ({panel[:-5]})' and added == False:
                addOptions.append(f'{panelData["name"]} ({panel[:-5]})')
                addFunctions.append(None)
                added = True
    if panelCount > 0:
        for option in oldOptions:
            if option == "(Create root panel)":
                data["functions"][data["options"].index("(Create root panel)")] = f"goto {file}\{file}Create"
                data["options"][data["options"].index("(Create root panel)")] = "(Create panel)"
    data["options"] = addOptions + oldOptions
    data["functions"] = addFunctions + oldFunctions
    json.dump(data, open(dir2, 'w'))
    json.load(open(f'{directory}\data\{file}\Settings.json'))["panels"] = panelCount
    json.dump(json.load(open(f'{directory}\data\{file}\Settings.json')), open(f'{directory}\data\{file}\Settings.json', 'w'))

def handlePanelCreation(dir : str, fileName : str, name : str, type : str, texts : list = None, inputString : str = None, command : str = None, options : list = None, functions : list = None):
    if type != "settings": open(f'{dir}\{fileName}.json', 'wb').close()
    if type == "option":
        json.dump({"name": name, "type": "option", "options": options, "functions": functions}, open(f'{dir}\{fileName}.json', 'w'))
    elif type == "text":
        json.dump({"name": name, "type": "text", "texts": texts, "functions": functions, "options": options}, open(f'{dir}\{fileName}.json', 'w'))
    elif type == "input":
        json.dump({"name": name, "type": "input", "texts": texts, "input": inputString, "command": command}, open(f'{dir}\{fileName}.json', 'w'))
    elif type == "settings":
        open(f'{dir}\Settings.json', 'wb').close()
        json.dump({"title": name, "panels": 0}, open(f'{dir}\Settings.json', 'w'))

def handleCommand(command : str, inputReceived : str):
    global current
    current = 1
    message = command.split(" ")
    if message[0] == "goto":
        build(f'{inputReceived}\{inputReceived}Manage')
    elif message[0] == "createNTE":
        os.system(f'mkdir {directory}\data\{inputReceived}')
        os.system(f'mkdir {directory}\data\{inputReceived}\panels')
        os.system(f'mkdir {directory}\data\{fileName}\panels\{inputReceived}')
        handlePanelCreation(f'{directory}\data\{fileName}\panels\{inputReceived}', f"{inputReceived}Manage", f"Manage {inputReceived}", "option", None, None, None, ["(Create root panel)", "(Delete)", "Back"], [f"goto {inputReceived}\{inputReceived}Root", f"delete {fileName} {inputReceived}", "goto root"])
        handlePanelCreation(f'{directory}\data\{fileName}\panels\{inputReceived}', f"{inputReceived}Root", f"Main {inputReceived} Panel", "input", [f"What will you name {inputReceived}'s main panel?"], "> ", f"createRoot {inputReceived}")
        handlePanelCreation(f'{directory}\data\{inputReceived}', None, inputReceived, "settings")
        handlePanelUpdate(inputReceived)
        build(f'{inputReceived}\{inputReceived}Manage')
    elif message[0] == "createRoot":
        handlePanelCreation(f'{directory}\data\{message[1]}\panels', "root", inputReceived, "option", None, None, None, None, None)
        handlePanelUpdate(message[1])
        build(f'{message[1]}\{message[1]}Manage')
    elif message[0] == "createPanel":
        return

def handleEnter(functions : str):
    global current
    for function in functions:
        if functions.index(function) + 1 == current:
            current = 1
            message = function.split(" ")
            if message[0] == "goto":
                build(message[1])
            elif message[0] == "change":
                data = json.load(open(f'{directory}\data\{message[1]}\{message[2]}.json'))
                data[message[3]] = message[4]
                json.dump(data, open(f'{directory}\data\{message[1]}\{message[2]}.json', 'w'))
            elif message[0] == "add":
                data = json.load(open(f'{directory}\data\{message[1]}\{message[2]}.json'))
                data[message[3]].append(message[4])
                json.dump(data, open(f'{directory}\data\{message[1]}\{message[2]}.json', 'w'))
            elif message[0] == "create":
                location = f'{directory}\data\{message[1]}\panels\{message[2]}.json'
                open(location, 'wb').close()
                json.dump({"title": f"{message[2]}"}, open(location, 'w'))
            elif message[0] == "delete":
                locationFile = f'{directory}\data\{message[1]}\panels\{message[2]}'
                locationFolder = f'{directory}\data\{message[2]}'
                os.system(f'rmdir {locationFile} /s /q')
                os.system(f'rmdir {locationFolder} /s /q')
                build("root")
            elif message[0] == "exit":
                exit()

def handleKeys(key, list : list, functions : list):
    if key == b'H' and list != None: handleArrows('up', len(list))
    elif key == b'P' and list != None: handleArrows('down', len(list))
    elif key == b'\r' and functions != None:
        os.system('cls')
        handleEnter(functions)
    elif key == b'\x1b':
        exit()

def fetchKeys(list : list, functions : list):
    key = msvcrt.getch()
    if list == None and functions == None: return [key, key.decode()]
    else: handleKeys(key, list, functions)

# [[ TUI builder ]]
def buildBorders(type : list, title : str = None):
    global width
    if 'continue' not in type:
        if 'merge' in type: print(f'{handleStyle(6)}{handleStyle(1) * (width - 2)}{handleStyle(7)}')
        else: print(f'{handleStyle(2)}{handleStyle(1) * (width - 2)}{handleStyle(3)}')
    if 'title' in type and title: print(f'{handleStyle(0)}{title.center(width - 3)} {handleStyle(0)}')
    if 'finish' in type:
        if 'merge' in type: print(f'{handleStyle(6)}{handleStyle(1) * (width - 2)}{handleStyle(7)}')
        else: print(f'{handleStyle(4)}{handleStyle(1) * (width - 2)}{handleStyle(5)}')
    if 'option' in type: print(f'{handleStyle(0)}{title} {handleStyle(0)}')

def buildInput(top : str, bottom : str, texts : list, inputString : str, command : str, typed : str = ''):
    global width, length, resizeFlag
    counter = 0
    chunkCounter = 0
    buildBorders(['title'], top)
    buildBorders(['title', 'merge', 'finish'], bottom)
    if resizeFlag:
        resizeFlag = False
        os.system('cls')
        buildInput(top, bottom, texts, inputString, command)
    for text in texts:
        index = texts.index(text)
        if len(text) > width - 5:
            division = [text[i:i+(width - 5)] for i in range(0, len(text), (width - 5))]
            for chunk in division:
                buildBorders(['option', 'continue'], f' {chunk}{' ' * (width - len(chunk) - 5)} ')
                chunkCounter += 1
            chunkCounter += 1
        else:
            buildBorders(['option', 'continue'], f' {texts[index]}{' ' * (width - len(texts[index]) - 5)} ')
            counter += 1
        buildBorders(['continue', 'title'], ' ')
    buildBorders(['option', 'continue'], f'{handleOption('start', 1)}{inputString + typed}{' ' * (width - len(inputString + typed) - 5)}{handleOption('end', 1)}')
    for _ in range(length - (counter * 2) - chunkCounter - 8):
        buildBorders(['continue', 'title'], ' ')
    buildBorders(['continue', 'finish'])
    detected = fetchKeys(None, None)
    letter = detected[1]
    if detected[0] == b'\r':
        os.system('cls')
        handleCommand(command, typed)
    else:
        if letter != None: typed += letter
        os.system('cls')
        buildInput(top, bottom, texts, inputString, command, typed)

def buildText(top : str, bottom : str, texts : list, functions : list, options : list = None):
    global width, length, resizeFlag
    counter = 0
    chunkCounter = 0
    buildBorders(['title'], top)
    buildBorders(['title', 'merge', 'finish'], bottom)
    if resizeFlag:
        resizeFlag = False
        os.system('cls')
        buildText(top, bottom, texts, functions, options)
    for text in texts:
        index = texts.index(text)
        if len(text) > width - 5:
            division = [text[i:i+(width - 5)] for i in range(0, len(text), (width - 5))]
            for chunk in division:
                buildBorders(['option', 'continue'], f' {chunk}{' ' * (width - len(chunk) - 5)} ')
                chunkCounter += 1
            chunkCounter += 1
        else:
            buildBorders(['option', 'continue'], f' {texts[index]}{' ' * (width - len(texts[index]) - 5)} ')
            counter += 1
        buildBorders(['continue', 'title'], ' ')
    if options:
        for option in options:
            index = options.index(option)
            buildBorders(['option', 'continue'], f'{handleOption('start', index + 1)}{options[index]}{' ' * (width - len(options[index]) - 5)}{handleOption('end', index + 1)}')
        for _ in range(length - (counter * 2) - chunkCounter - len(options) - 7):
            buildBorders(['continue', 'title'], ' ')
    else:
        for _ in range(length - (counter * 2) - chunkCounter - 7):
            buildBorders(['continue', 'title'], ' ')
    buildBorders(['continue', 'finish'])
    if options:
        fetchKeys(options, functions)
        buildText(top, bottom, texts, functions, options)
        os.system('cls')
    else:
        fetchKeys(None)
        os.system('cls')
        buildText(top, bottom, texts)

def buildOption(top : str, bottom : str, options : list, functions : list):
    global width, length, resizeFlag
    buildBorders(['title'], top)
    buildBorders(['title', 'merge', 'finish'], bottom)
    for option in options:
        index = options.index(option)
        buildBorders(['option', 'continue'], f'{handleOption('start', index + 1)}{options[index]}{' ' * (width - len(options[index]) - 5)}{handleOption('end', index + 1)}')
    for _ in range(length - len(options) - 7):
        buildBorders(['continue', 'title'], ' ')
    buildBorders(['continue', 'finish'])
    if resizeFlag:
        resizeFlag = False
        os.system('cls')
        buildOption(top, bottom, options, functions)
    fetchKeys(options, functions)
    os.system('cls')
    buildOption(top, bottom, options, functions)

def build(load : str):
    try:
        panel = json.load(open(f'{directory}\data\{fileName}\panels\{load}.json'))
        load = panel["name"]
        if panel["type"] == "option":
            buildOption(title, load, panel["options"], panel["functions"])
        elif panel["type"] == "text":
            buildText(title, load, panel["texts"], panel["functions"], panel["options"])
        elif panel["type"] == "input":
            buildInput(title, load, panel["texts"], panel["input"], panel["command"], "")
    except FileNotFoundError:
        print(f"Can\'t go to panel \"{load}\" because it wasn\'t found.")
        time.sleep(4)
        if load == "root":
            exit()
        build("root")

# [ Threads ]
threadSize = Thread(target=handleSize, daemon=True)
threadSize.start()

# [ Allign console ]
os.system("mode con: lines=37")
handleFormat()

# [ Start ]
build("root")