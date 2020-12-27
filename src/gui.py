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
        for Frame in (MainFrame, ItemFrame, MutationFrame, BionicFrame, MartialArtFrame, MonsterFrame, CraftingFrame, VehicleFrame):
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
            width = bWidth,
            command = lambda: self.controller.showFrame("BionicFrame")
        )
        bionicButton.pack(side="top")

        monsterButton = tk.Button(
            self,
            text="⚰ Monsters",
            width = bWidth,
            command = lambda: self.controller.showFrame("MonsterFrame")
        )
        monsterButton.pack(side="top")

        martialButton = tk.Button(
            self,
            text="⚔ Martial Arts",
            width = bWidth,
            command = lambda: self.controller.showFrame("MartialArtFrame")
        )
        martialButton.pack(side="top")

        vehicleButton = tk.Button(
            self,
            text="⛍ Vehicles",
            width = bWidth,
            command = lambda: self.controller.showFrame("VehicleFrame")
        )
        vehicleButton.pack(side="top")

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

class MutationFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the mutation screen"

    def setLookupType(self, lookupType="mutation"):
        self.currentLookupType = lookupType

class BionicFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the bionic screen"

    def setLookupType(self, lookupType="bionic"):
        self.currentLookupType = lookupType

class MartialArtFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the martial art screen"

    def setLookupType(self, lookupType="martial_art"):
        self.currentLookupType = lookupType

class VehicleFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the vehicle part screen"

    def setLookupType(self, lookupType="vehicle"):
        self.currentLookupType = lookupType

class MonsterFrame(LookupFrame):
    def getWelcomeMessage(self):
        return "Welcome to the monster screen"

    def setLookupType(self, lookupType="monster"):
        self.currentLookupType = lookupType

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
        self.prettifyRecipe(rawJson)
        rawJson = self.translator.translate(rawJson, self.currentLookupType)
        for attribute in rawJson:
            self.addLine(attribute + ": " + str(rawJson[attribute]))

    def prettifyRecipe(self, rawJson):
        prettifiers = {
            "book_learn": self.prettifyBooks,
            "components": self.prettifyComponents,
            "skills_required": self.prettifySkillsRequired,
            "tools": self.prettifyTools,
            "qualities": self.prettifyQualities
        }
        self.unpackUsing(rawJson)
        for prettifier in prettifiers:
            self.prettify(rawJson, prettifier, prettifiers[prettifier])
        self.prettifySkillUsed(rawJson)

    def prettify(self, entry,attributeName, prettifier):
        output = []
        attributes = entry.get(attributeName)

        if not attributes:
            return

        for attribute in attributes:
            prettifier(attribute, output)

        entry[attributeName] = "\n".join(output)

    def prettifyTools(self, tool, output):
        outputStr = ""
        first = True
        for optionalTool in tool:
            # First does not need to have "or" in output
            if first:
                first = False
            else:
                outputStr += " or "
            name = self.getNameFromID(optionalTool[0], "item")
            outputStr += name + f" ({optionalTool[1]} charges)"
        output.append(outputStr)

    def prettifyQualities(self, quality, output):
        qualityID = quality["id"]
        qualityLevel = quality["level"]
        name = self.getNameFromID(qualityID, "tool_quality")
        output.append(f"1 tool with {name} quality of {qualityLevel}")

    def prettifyComponents(self, component, output):
        outputStr = ""
        first = True
        for optionalComponent in component:
            # First does not need to have "or" in output
            if first:
                first = False
            else:
                outputStr += " or "
            name = self.getNameFromID(optionalComponent[0], "item")
            outputStr += str(optionalComponent[1]) + " of " + name
        output.append(outputStr)

    def prettifyBooks(self, book, output):
        outputStr = f"{self.getNameFromID(book[0], 'item')} (level {book[1]})"
        output.append(outputStr)

    def prettifySkillUsed(self, entry):
        skill = entry.get("skill_used")

        if not skill:
            return

        entry["skill_used"] = f"{self.getNameFromID(skill, 'skill')} (level {entry.get('difficulty')})"

    def prettifySkillsRequired(self, skill, output):
        outputStr = f"{self.getNameFromID(skill[0], 'skill')} (level {skill[1]})"
        output.append(outputStr)

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

    def getNameFromID(self, entryID, entryType):
        componentJson = self.getEntryByID(entryID, entryType)
        if componentJson:
            return componentJson["name"]
        else:
            # Output id if name is not found for some reason
            return entryID
