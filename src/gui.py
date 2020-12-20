import tkinter as tk
import jsonhandler

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.currentLookup = "item"
        self.loadedJson = jsonhandler.JsonLoader()

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
        self.searcher = jsonhandler.JsonSearcher(controller.loadedJson.items)
        # Makes JSON into pretty, human-readable text
        self.translator = jsonhandler.JsonTranslator()

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

        # Makes enter key run search too
        controller.bind('<Return>', lambda search : self.searchItem())

        self.createButtons()

    def searchItem(self):
        # Retrieves content of entry field
        search = self.searchField.get().lower()
        self.clearResultField()
        if ":" in search:
            attributes = self.searcher.getAttributesFromString(search)
            result = self.searcher.searchByAttribute(attributes, self.currentLookup)
        else:
            result = self.searcher.searchByAttribute({"name": search}, self.currentLookup)

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

class CraftingFrame(tk.Frame): #TODO This is quite similar to LookupFrame, do we need two separate classes?
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.searcher = jsonhandler.JsonSearcher(controller.loadedJson.items["recipe"])
        # Makes JSON into pretty, human-readable text
        self.translator = jsonhandler.JsonTranslator()

        self.label = tk.Label(self, text=f"Welcome to the crafting screen.")
        self.label.pack(side="top")

        self.searchField = tk.Entry(self)
        self.searchField.pack()

        # Where the result will pop up
        self.resultField = tk.Text(self, height=20, width=50)
        self.resultField.configure(state="disabled")
        self.resultField.pack()

        searchButton = tk.Button(self, text="Search", command=self.searchItem)
        searchButton.pack()

        # Makes enter key run search too
        controller.bind('<Return>', lambda search : self.searchItem())

    def searchItem(self):
        # Retrieves content of entry field
        search = self.searchField.get().lower()
        self.clearResultField()
        if ":" in search:
            attributes = self.searcher.getAttributesFromString(search)
            result = self.searcher.searchByAttribute(attributes, self.currentLookup)
        else:
            result = self.searcher.searchByAttribute({"name": search}, self.currentLookup)

        if isinstance(result, dict):
            self.outputJson(result)
        elif isinstance(result, list):
            self.outputList(result)
