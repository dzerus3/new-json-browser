import json
import glob
import os
import tkinter as tk

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.loadedJson = JsonLoader()
        tk.Tk.__init__(self, *args, **kwargs)

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
        for Frame in (MainFrame, ItemFrame, MutationFrame):
            frameName = Frame.__name__
            frameInstance = Frame(
                parent=self.container, json=self.loadedJson.items)
            self.frames[frameName] = frameInstance

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frameInstance.grid(row=0, column=0, sticky="nsew")

        self.showFrame("MainFrame")

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
            text="⚒ Items",
            width = bWidth,
            command = lambda: self.controller.showFrame("ItemFrame")
        )
        itemButton.pack(side="top")

        mutationButton = tk.Button(
            self,
            text="☣ Mutations",
            width = bWidth,
            command = lambda: self.controller.showFrame("MutationFrame")
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

class MainFrame(tk.Frame):
    def __init__(self, parent, json):
        tk.Frame.__init__(self, parent)
        welcome = tk.Label(self, text="Welcome to Dellon's JSON browser!")
        welcome.pack()

class ItemFrame(tk.Frame):
    def __init__(self, parent, json):
        tk.Frame.__init__(self, parent)
        self.json = json

        itemLabel = tk.Label(self, text="Welcome to the item screen.")
        itemLabel.pack(side="top")

        self.searchField = tk.Entry(self)
        self.searchField.pack()

        self.resultLabel = tk.Message(self, text="")
        self.resultLabel.pack()

        searchButton = tk.Button(
            self,
            text="Search",
            command=self.searchItem
        )
        searchButton.pack()

    def searchItem(self):
        search = self.searchField.get().lower()
        item = self.json["item"].get(search)
        self.resultLabel["text"] = str(item)

class MutationFrame(tk.Frame):
    def __init__(self, parent, json):
        tk.Frame.__init__(self, parent)
        mutationLabel = tk.Label(self, text="Welcome to the mutation screen.")
        mutationLabel.pack(side="top")

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
                jsonContent = json.load(openedJsonFile)
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
