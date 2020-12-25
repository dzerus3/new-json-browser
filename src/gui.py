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
        self.organizedJson = self.jsonLoader.getOrganizedJson()
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
        self.searcher = jsonhandler.JsonSearcher(controller.loadedJson, controller.organizedJson)
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

    def getEntryByID(self, entryID, entryType):
        return self.searcher.organizedJson[entryType].get(entryID)

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

    def outputJson(self, rawJson):
        self.clearResultField()
        self.unpackUsing(rawJson)
        self.prettifyComponents(rawJson)
        self.prettifyBooks(rawJson)
        rawJson = self.translator.translate(rawJson, self.currentLookupType)
        for attribute in rawJson:
            self.addLine(attribute + ": " + str(rawJson[attribute]))

    def prettifyComponents(self, entry):
        output = []
        components = entry.get("components")

        if not components:
            return

        for component in components:
            outputStr = ""
            first = True
            for optionalComponent in component:
                # First does not need to have "or" in output
                if first:
                    first = False
                else:
                    outputStr += " or "
                name = self.getNameFromID(optionalComponent[0])
                outputStr += str(optionalComponent[1]) + " of " + name
            output.append(outputStr)
        entry["components"] = "\n".join(output)

    def prettifyBooks(self, entry):
        output = []
        books = entry.get("book_learn")

        if not books:
            return

        for book in books:
            outputStr = f"{self.getNameFromID(book[0])} (level {self.getNameFromID(book[1])})"
            output.append(outputStr)
        entry["book_learn"] = "\n".join(output)

    def unpackUsing(self, entry):
        output = []
        using = entry.get("using")

        if not using:
            return

        for preset in using:
            presetID = preset[0]
            presetQuantity = preset[1]
            presetJson = self.getEntryByID(presetID, "requirement")
            if not presetJson:
                return
            tools = presetJson.get("tools")
            components = presetJson.get("components")
            qualities = presetJson.get("qualities")

            #TODO: Refactor

        if tools:
            self.addToJson(entry, "tools", tools)

        if components:
            for component in components:
                for optionalComponent in component:
                    optionalComponent[1] *= presetQuantity
            self.addToJson(entry, "components", self.handleRequirementComponent(components))

        if qualities:
            self.addToJson(entry, "qualities", qualities)
        return output

    # These are sometimes nested and have to be handled specially.
    def handleRequirementComponent(self, components):
        output = []

        for optionalComponents in components:
            optOutput = []
            for optionalComponent in optionalComponents:
                # Nested components appear to have an extra element
                # to indicate they are nested
                if len(optionalComponent) > 2:
                    componentJson = self.getEntryByID(optionalComponent[0], "requirement")

                    buff = self.handleRequirementComponent(componentJson["components"])
                    quantity = optionalComponent[1]
                    for comp in buff:
                        for optComp in comp:
                            # Multiplies everything by quantity in preset
                            optComp[1] *= quantity
                            optOutput.append(optComp)
                else:
                    optOutput.append(optionalComponent)
            output.append(optOutput)
        return output

    def addToJson(self, entry, attribute, content):
        if entry.get(attribute):
            entry[attribute] += content
        else:
            entry[attribute] = content

    def getNameFromID(self, entryID):
        componentJson = self.getEntryByID(entryID, "item")
        if componentJson:
            return componentJson["name"]
        else:
            # Output id if name is not found for some reason
            return entryID
