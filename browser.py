import json
import re
import glob
import os
import textdistance
import tkinter as tk

from sys import exit

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.currentLookup = "item"
        self.loadedJson = JsonLoader()
        tk.Tk.__init__(self, *args, **kwargs)

        # A big container for the main frame
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.createMainFrame()
        self.createSidebar()
        self.mainloop()

    def createSidebar(self):
        self.sidebar = Sidebar(controller=self)
        self.sidebar.pack(side="left", fill="both")

    def createMainFrame(self):
        self.frames = {}
        for Frame in (MainFrame, LookupFrame):
            frameName = Frame.__name__
            frameInstance = Frame(parent=self.container, controller=self)
            self.frames[frameName] = frameInstance

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frameInstance.grid(row=0, column=0, sticky="nsew")

        self.showFrame("MainFrame")

    # Moves specified frame to the top, making it replace current one
    def showFrame(self, frameName):
        frame = self.frames[frameName]
        frame.tkraise()

    # https://stackoverflow.com/a/28623781
    def clearFrame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

class Sidebar(tk.Frame):
    def __init__(self, controller):
        tk.Frame.__init__(self)
        self.controller = controller
        self.createButtons()

    def createButtons(self):
        # Default width for all buttons
        bWidth = 10

        itemButton = tk.Button(
            self,
            text="Lookup",
            width = bWidth,
            command = lambda: self.controller.showFrame("LookupFrame")
        )
        itemButton.pack(side="top")

        exitButton = tk.Button(
            self,
            text="Exit",
            width = bWidth,
            command = exit
        )
        exitButton.pack(side="top")

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        welcome = tk.Label(self, text="Welcome to Dellon's JSON browser!")
        welcome.pack()

class LookupFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # The JSON type program will search for
        self.currentLookup = "item"
        #TODO Does controller need to have JSON, or can we just pass it to JsonSearcher directly?
        self.searcher = JsonSearcher(controller.loadedJson.items)
        # Makes JSON into pretty, human-readable text
        self.translator = JsonTranslator()

        self.label = tk.Label(self, text=f"Welcome to the {self.currentLookup} screen.")
        self.label.pack(side="top")

        self.searchField = tk.Entry(self)
        self.searchField.pack()

        # Where the result will pop up
        self.resultField = tk.Text(self, height=20, width=50)
        self.resultField.configure(state="disabled")
        self.resultField.pack()

        searchButton = tk.Button(self, text="Search", command=self.searchItem)
        searchButton.pack()

        self.createButtons()

    def searchItem(self):
        # Retrieves content of entry field
        search = self.searchField.get().lower()
        self.clearResultField()
        if ":" in search:
            result = self.searcher.searchByAttribute(search, self.currentLookup)
        else:
            result = self.searcher.searchByName(search, self.currentLookup)

        if isinstance(result, dict):
            self.outputJson(result)
        elif isinstance(result, list):
            self.outputList(result)

    # TODO Rename function
    def addResult(self, message):
        # Disabling/enabling field is done to prevent typing in Text box
        self.resultField.configure(state="normal")
        self.resultField.insert(tk.END, str(message) + "\n")
        self.resultField.configure(state="disabled")

    def clearResultField(self):
        self.resultField.configure(state="normal")
        self.resultField.delete("1.0", "end")
        self.resultField.configure(state="disabled")

    def changeCurrentLookup(self, lookupType):
        self.currentLookup = lookupType
        self.label["text"] = f"Welcome to the {lookupType} screen."
        # Also clears the screen, makes for better UX
        self.clearResultField()
        self.searchField.delete(0, 'end')

    # Used for outputting lists of names, such as with attribute search
    # TODO Add clickable links to output?
    def outputList(self, results):
        for result in results:
            self.addResult(result)

    # Used to output JSON objects
    def outputJson(self, rawJson):
        self.clearResultField()
        rawJson = self.translator.translate(rawJson, self.currentLookup)
        for attribute in rawJson:
            self.addResult(attribute + ": " + str(rawJson[attribute]))

    def createButtons(self):
        # Default width for all buttons
        bWidth = 10

        monsterButton = tk.Button(
            self,
            text="⚰ Monsters",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("monster")
        )
        monsterButton.pack(side="bottom")

        vehicleButton = tk.Button(
            self,
            text="⛍ Vehicles",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("vehicle")
        )
        vehicleButton.pack(side="bottom")

        martialButton = tk.Button(
            self,
            text="⚔ Martial Arts",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("martial_art")
        )
        martialButton.pack(side="bottom")

        bionicButton = tk.Button(
            self,
            text="⚙ Bionics",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("bionic")
        )
        bionicButton.pack(side="bottom")

        mutationButton = tk.Button(
            self,
            text="☣ Mutations",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("mutation")
        )
        mutationButton.pack(side="bottom")

        itemButton = tk.Button(
            self,
            text="⚒ Items",
            width = bWidth,
            command = lambda: self.changeCurrentLookup("item")
        )
        itemButton.pack(side="bottom")

class JsonTranslator():
    def __init__(self):
        translationFile = open("translation.json", "r")
        self.translations = json.load(translationFile)

    def translate(self, rawJson, jsonType):
        rawJson = self.filterJson(rawJson, jsonType)
        self.translateJson(rawJson, jsonType)

        return rawJson
        #TODO add special case for martial arts bonuses.

    def filterJson(self, rawJson, jsonType):
        unwantedValues = {
            "all":  ["type", "//", "//2", "copy-from"], #id is also candidate
            "item": ["color", "use_action", "category", "subcategory",
                     "id_suffix", "result"],
            "mutation":  ["valid"],
            "bionic"  :  ["flags", "fake_item", "time"],
            "martial_art":["initiate", "static_buffs", "onmiss_buffs",
                          "onmove_buffs", "ondodge_buffs", "onhit_buffs",
                          "oncrit_buffs", "onblock_buffs"],
            "material":  ["dmg_adj", "bash_dmg_verb", "cut_dmg_verb",
                          "ident"], #TODO add material search
            "vehicle": ["item", "location", "requirements", "size"],
            "monster":   ["harvest", "revert_to_itype", "vision_day",
                          "color", "weight", "default_faction"]
        }

        resultJson = {}

        for attribute in rawJson:
            if attribute in unwantedValues[jsonType] or attribute in unwantedValues["all"]:
                continue
            else:
                resultJson[attribute] = rawJson[attribute]
        return resultJson

    def translateJson(self, rawJson, jsonType):
        typeTranslations = self.translations[jsonType]
        for attribute in rawJson:
            translation = typeTranslations.get(attribute)

            #TODO add support for legacy names
            # Names are special because they are an object
            if attribute == "name":
                name = rawJson["name"].get("str")
                rawJson["name"] = name

            elif translation:
                rawJson[translation] = rawJson[attribute]
                rawJson.pop(attribute)

class JsonSearcher():
    def __init__(self, rawJson):
        self.rawJson = rawJson

    def searchByName(self, name, jsonType):
        # Gets the item with the name `search` from the JSON of
        # currentLookup type # TODO
        return self.rawJson[jsonType].get(name)

    def searchByAttribute(self, string, jsonType):
        results = []
        attributes = self.getAttributesFromString(string)
        typeJson = self.rawJson[jsonType]

        # Loops through all entries of selected type
        for entryName in typeJson:
            entry = typeJson[entryName]
            # Checks if entry contains all specified attributes
            result =  all(elem in entry for elem in attributes)
            if result:
                # Checks if every given attribute is equal to specified value
                for attribute in attributes:
                    similarity = self.getSimilarity(attributes[attribute], entry[attribute])
                    if similarity > 0.5:
                        # similarResults[entryName] = similarity
                        results.append(entryName)
                    else:
                        break
        return results

    def getSimilarity(self, desired, given):
        # If the given string contains desired as a substring
        if desired in given:
            return 1
        desired_attr = [char for char in desired]
        given_attr = [char for char in given]

        # Returns a number representing how similar the two strings are
        return textdistance.jaccard(desired_attr, given_attr)

    def getAttributesFromString(self, string):
        attributes = {}
        pattern = re.compile(r"\w*:\w*")
        # pattern = re.compile(r"\w*:\"\w*\"") #TODO
        matches = pattern.findall(string)
        for match in matches:
            key = match.split(":")[0]
            value = match.split(":")[1]
            attributes[key] = value

        return attributes

class JsonLoader():
    def __init__(self):
        self.jsonDir = self.readJsonDir()
        self.jsonFiles = self.getJsonFiles()
        self.loadedJson = self.loadJson()

    # Get the Json directory from file; thanks to @rektrex for this function
    def readJsonDir(self):
        configfile = os.path.join(
                os.environ.get('APPDATA') or
                os.environ.get('XDG_CONFIG_HOME') or
                os.path.join(os.environ['HOME'], '.config'),
                'cdda_json_browser'
        )
        try:
            with open(configfile, 'r') as configFile:
                directory = configFile.readline()

                if not os.path.isdir(directory):
                    raise FileNotFoundError

        except FileNotFoundError:
            directory = self.getJsonDir()
            with open(configfile, 'w') as configFile:
                configFile.write(directory)

        finally:
            return directory

    # Run when the program is started for the first time, or whenever the JSON dir is not found
    def getJsonDir(self):
        print("Please enter the path to the game's JSON folder.")
        directory = input() # TODO

        # Recursive call to itself until a valid location is specified
        if not os.path.isdir(directory):
            print("This path appears to be wrong.")
            directory = getJsonDir()

        return directory

    # Loads game's JSON into memory
    def getJsonFiles(self):
        print(f"Retrieving a list of JSON files from {self.jsonDir}...")

        # Gets the name of each JSON file
        # os.path.join does *not* work here
        jsonFiles = []
        wildcard = self.jsonDir + "/**/*.json"

        for jsonFile in glob.iglob(wildcard, recursive=True):
            jsonFiles.append(jsonFile)

        return jsonFiles

    def loadJson(self):
        print("Loading items from JSON...")

        self.items = {
            "item":{},
            "mutation":{},
            "bionic":{},
            "martial_art":{},
            "vehicle":{},
            "monster":{}
        }

        for jsonFile in self.jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                try:
                    jsonContent = json.load(openedJsonFile)
                except json.decoder.JSONDecodeError:
                    print("Failed to read game's JSON. Did you modify it?")
                    exit(1)

                objType = ""

                # Although most files are arrays of objects, some are just
                # one object. This needs to be handled.
                if isinstance(jsonContent, dict):
                    self.handleObjectJson(jsonContent)
                else:
                    for obj in jsonContent:
                        self.handleObjectJson(obj)

    def handleObjectJson(self, obj):
        objType = self.resolveType(obj["type"])
        if objType:
            name = self.getItemName(obj.get("name"))
            self.items[objType][name] = obj

    def resolveType(self, jsonType):
        types = {
            "item": [
                "AMMO", # Ammunition for guns
                "ARMOR", # Wearable clothing
                "BATTERY", # Batteries
                "BIONIC_ITEM", # Bionic modules
                "BOOK", # Readable book
                "COMESTIBLE", # Food
                "GENERIC", # Random things
                "GUN", # Firearms
                "GUNMOD", # Gun modifications
                "MAGAZINE", # Magazines for guns
                "PET_ARMOR", # Armor wearable by pets
                "TOOL" # Tools and bombs
            ],
            "mutation": ["mutation"],
            "bionic": ["bionic"],
            "martial_art": ["martial_art"],
            "vehicle": ["vehicle_part"],
            "monster": ["MONSTER"]
        }

        for objectType in types:
            if jsonType in types[objectType]:
                return objectType

        return None

    def getItemName(self, name):
        # Checks whether the name is a legacy name
        # lowercases name so search is not case sensitive
        if isinstance(name, str):
            return name.lower()
        elif isinstance(name, dict):
            return name.get("str").lower()
        else:
            return "NONE"

def main():
    gui = Gui()

if __name__ == "__main__":
    main()
