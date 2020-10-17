import json
import glob
import os
import tkinter as tk

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.createMainFrame()
        self.createSidebar()
        self.mainloop()

    def createSidebar(self):
        self.sidebar = Sidebar(controller=self)
        self.sidebar.pack(side="left", fill="both")

    def createMainFrame(self):
        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(side="top", fill="both")
        welcome = tk.Label(self.mainFrame, text="Welcome to Dellon's JSON browser!")
        welcome.pack()

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
            text="⚒ Items",
            width = bWidth
            # command = self.itemScreen
        )
        itemButton.pack(side="top")

        mutationButton = tk.Button(
            self,
            text="☣ Mutations",
            width = bWidth
        )
        mutationButton.pack(side="top")

        bionicButton = tk.Button(
            self,
            text="⚙ Bionics",
            width = bWidth
        )
        bionicButton.pack(side="top")

        martialButton = tk.Button(
            self,
            text="⚔ Martial Arts",
            width = bWidth
        )
        martialButton.pack(side="top")

        vehicleButton = tk.Button(
            self,
            text="⛍ Vehicles",
            width = bWidth
        )
        vehicleButton.pack(side="top")

        monsterButton = tk.Button(
            self,
            text="⚰ Monsters",
            width = bWidth
        )
        monsterButton.pack(side="top")

    # def itemScreen(self):
    #     self.clearFrame(self.mainFrame)
    #     itemLabel = tk.Label(self.mainFrame, text="Welcome to the item screen.")
    #     itemLabel.pack(side="top")

class JsonLoader():
    def __init__(self):
        self.jsonDir = self.readJsonDir()
        self.jsonFiles = self.getJsonFiles()
        self.loadedJson = self.loadJson()
        print(self.items[0])

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
        itemTypes = [
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
        ]

        self.items = {}

        for jsonFile in self.jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                jsonContent = json.load(openedJsonFile)
                objType = ""

                # Although most files are arrays of objects, some are just
                # one object. This needs to be handled.
                if isinstance(jsonContent, dict):
                    objType = jsonContent.get("type")
                else:
                    for obj in jsonContent:
                        if obj["type"] in itemTypes:
                            name = self.getItemName(obj["name"])
                            self.items[name] = obj
        print(self.items["atomic lamp"])

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
    loadedJson = JsonLoader()
    gui = Gui()

if __name__ == "__main__":
    main()
