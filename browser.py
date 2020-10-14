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
        sidebar = tk.Frame(self)
        sidebar.pack(side="left", fill="both")
        self.sidebarButtons(sidebar)

    def sidebarButtons(self, sidebar):
        itemButton = tk.Button(sidebar, text="⚔ Items")
        itemButton.pack(side="left")

    def createMainFrame(self):
        mainFrame = tk.Frame(self)
        mainFrame.pack(side="right", fill="both")
        welcome = tk.Label(self, text="Welcome to Dellon's JSON browser!")
        welcome.pack()

class JsonLoader():
    def __init__(self):
        self.jsonDir = self.readJsonDir()
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
        # directory = input() # TODO

        # Recursive call to itself until a valid location is specified
        if not os.path.isdir(directory):
            print("This path appears to be wrong.")
            directory = getJsonDir()

        return directory

    # Loads game's JSON into memory
    def loadJson(self):
        result = []

        # Gets the name of each JSON file
        # I'm not sure whether os.path.join() is the best idea here since it's not an actual directory, but it should work
        jsonFiles = glob.glob(os.path.join(self.jsonDir, "/**/*.json", recursive=True))

        # Loops through every file name and loads it into a list
        for jsonFile in jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                result.append(json.load(openedJsonFile))

        return result

def main():
    gui = Gui()

if __name__ == "__main__":
    main()
