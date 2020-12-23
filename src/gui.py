import tkinter as tk
from os.path import isdir
import jsonhandler

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # A big container for the main frame
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.checkGameDirectory()

        self.createSidebar()
        self.mainloop()

    def checkGameDirectory(self):
        self.jsonLoader = jsonhandler.JsonLoader()
        directory = self.jsonLoader.readJsonDir()
        if not directory:
            self.createDirectoryFrame()
        else:
            self.createScreens(directory)

    def createDirectoryFrame(self):
        frameName = "directory"
        frameInstance = DirectoryFrame(parent=self.container, controller=self)
        # self.frames[frameName] = frameInstance

        frameInstance.grid(row=0, column=0, sticky="nsew")
        frameInstance.tkraise()

    def createScreens(self, directory):
        self.loadedJson = self.jsonLoader.getJson()
        self.createMainFrame()

    def createSidebar(self):
        self.sidebar = Sidebar(controller=self)
        self.sidebar.pack(side="left", fill="both")

    def createMainFrame(self):
        self.frames = {}
        for Frame in (MainFrame, ItemFrame, CraftingFrame):
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
            text="Items",
            width = bWidth,
            command = lambda: self.controller.showFrame("ItemFrame")
        )
        itemButton.pack(side="top")

        craftingButton = tk.Button(
            self,
            text="Crafting",
            width = bWidth,
            command = lambda: self.controller.showFrame("CraftingFrame")
        )
        craftingButton.pack(side="top")

        exitButton = tk.Button(
            self,
            text="Exit",
            width = bWidth,
            command = exit
        )
        exitButton.pack(side="top")

class DirectoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        self.label = tk.Label(self, text="Enter the path to the game folder")
        self.label.pack(side="top")

        self.dirField = tk.Entry(self)
        self.dirField.pack()

        searchButton = tk.Button(self, text="Enter", command=self.checkDir)
        searchButton.pack()

    def checkDir(self):
        directory = self.dirField.get()
        if isdir(directory):
            self.controller.jsonLoader.writeJsonDir(directory)
            self.controller.jsonLoader.setJsonDir(directory)
            self.controller.createScreens(directory)
        else:
            self.label["text"] = "Not a valid path."

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        welcome = tk.Label(self, text="Welcome to Dellon's JSON browser!")
        welcome.pack()

class LookupFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.setLookupType()
        self.createJsonSearcher(controller)
        self.createUI()
        self.assignHotkeys()

    def setLookupType(self, lookupType="item"):
        self.currentLookupType = lookupType

    def createJsonSearcher(self, controller):
        self.searcher = jsonhandler.JsonSearcher(controller.loadedJson)
        self.translator = jsonhandler.JsonTranslator()

    def createUI(self):
        self.label = tk.Label(self, text=self.getWelcomeMessage())
        self.label.pack(side="top")

        self.searchField = tk.Entry(self)
        self.searchField.pack()

        # Where the result will pop up
        self.resultField = tk.Text(self, height=20, width=50)
        self.resultField.configure(state="disabled")
        self.resultField.pack()

        searchButton = tk.Button(self, text="Search", command=self.searchItem)
        searchButton.pack()

    def addLine(self, message):
        # Disabling/enabling field is done to prevent typing in Text box
        self.resultField.configure(state="normal")
        self.resultField.insert(tk.END, str(message) + "\n")
        self.resultField.configure(state="disabled")

    def clearResultField(self):
        self.resultField.configure(state="normal")
        self.resultField.delete("1.0", "end")
        self.resultField.configure(state="disabled")

    def changeCurrentLookup(self, lookupType):
        self.currentLookupType = lookupType
        # Also clears the screen, makes for better UX
        self.clearResultField()
        self.searchField.delete(0, 'end')

    # Used for outputting lists of names, such as with attribute search
    # TODO Add clickable links to output?
    def outputList(self, results):
        for result in results:
            self.addLine(result)

    # Used to output JSON objects
    def outputJson(self, rawJson):
        self.clearResultField()
        rawJson = self.translator.translate(rawJson, self.currentLookupType)
        for attribute in rawJson:
            self.addLine(attribute + ": " + str(rawJson[attribute]))

    def searchItem(self):
        # Retrieves content of entry field
        search = self.searchField.get().lower()
        self.clearResultField()

        result = self.getResult(search)
        self.outputResult(result)

    def getResult(self, search):
        if ":" in search:
            attributes = self.searcher.getAttributesFromString(search)
            result = self.searcher.searchByAttribute(attributes, self.currentLookupType)
        else:
            result = self.searcher.searchByAttribute({"name": search}, self.currentLookupType)
        return result

    def outputResult(self, result):
        if isinstance(result, dict):
            self.outputJson(result)
        elif isinstance(result, list):
            self.outputList(result)

    def getWelcomeMessage(self):
        pass

    def assignHotkeys(self):
        pass

class ItemFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the item screen"

    def createUI(self):
        self.label = tk.Label(self, text=self.getWelcomeMessage())
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

class CraftingFrame(LookupFrame):
    def searchItem(self):
        # Retrieves content of entry field
        search = self.searchField.get().lower()
        self.clearResultField()

        item = self.searcher.searchByAttribute({"name": search}, "item")["id"]
        recipe = self.searcher.searchByAttribute({"result": item}, "recipe")

        if isinstance(recipe, dict):
            self.outputJson(recipe)
        elif isinstance(recipe, list):
            self.outputList(recipe)

    def getWelcomeMessage(self):
        return "Welcome to the crafting frame"

    def setLookupType(self, lookupType="recipe"):
        self.currentLookupType = lookupType
