import json
import re
import glob
import os
import textdistance

class JsonSearcher():
    def __init__(self, rawJson, organizedJson):
        self.rawJson = rawJson
        self.organizedJson = organizedJson

    #TODO Add so user can search for any item with an attribute, without specifying attribute value.
    def searchByAttribute(self, requiredAttributes, jsonType):
        similarities = []
        # attributes = self.getAttributesFromString(string)
        typeJson = self.rawJson[jsonType]

        for entry in typeJson:
            if self.containsAllAttributes(entry, requiredAttributes):
                attributeSimilarity = self.checkAttributeSimilarity(entry, requiredAttributes)

                if attributeSimilarity == 100:
                    return entry
                elif attributeSimilarity > 0:
                    if entry.get("name"):
                        buff = {"name": entry["name"], "similarity": attributeSimilarity}
                        similarities.append(buff)
        results = self.sortBySimilarity(similarities)

        return results

    def sortBySimilarity(self, similarities):
        results = []

        sortedSimilarities = sorted(similarities, key=lambda s: s["similarity"], reverse=True)
        for value in sortedSimilarities:
            results.append(value["name"])

        return results

    def checkAttributeSimilarity(self, entry, requiredAttributes):
        # Checks if every given attribute is sufficiently similar to specified value
        failed = False
        # Sum of all similarities. Used for averaging and sorting
        totalSimilarity = 0
        equal = 0
        for attribute in requiredAttributes:
            similarity = self.getSimilarity(requiredAttributes[attribute], entry[attribute])
            # If they are exactly the same
            if requiredAttributes[attribute] == entry[attribute]:
                equal += 1
                totalSimilarity += 1
            elif similarity > 0.7:
                totalSimilarity += similarity
            # If they are completely different
            else:
                totalSimilarity = 0
                break
        # if all attributes are exactly equal
        if equal == len(requiredAttributes):
            return 100
        # if they are somewhat similar
        elif totalSimilarity:
            return totalSimilarity / len(requiredAttributes)
        else:
            return 0

    # Checks if entry contains all specified attributes
    def containsAllAttributes(self, entry, attributes):
        return all(elem in entry for elem in attributes)

    def getSimilarity(self, desired, given):
        # If the given string contains desired as a substring
        if desired in given:
            return 0.9
        # Strings have to be split up into character arrays for this algorithm
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
    def getJson(self):
        jsonFiles = self.getJsonFiles()
        self.loadJson(jsonFiles)
        return self.items

    def getOrganizedJson(self):
        return self.itemsByID

    # Get the Json directory from file; thanks to @rektrex for this function
    def readJsonDir(self):
        self.configfile = os.path.join(
            os.environ.get('APPDATA') or
            os.environ.get('XDG_CONFIG_HOME') or
            os.path.join(os.environ['HOME'], '.config'),
            'cdda_json_browser'
        )

        # Can't set it to if because both configfile and directory are checked
        try:
            with open(self.configfile, 'r') as configFile:
                directory = configFile.readline()

                if not os.path.isdir(directory):
                    raise FileNotFoundError

        except FileNotFoundError:
            return None

        self.setJsonDir(directory)
        return directory

    # Records dir to configfile for future use
    def writeJsonDir(self, directory):
        with open(self.configfile, 'w') as configFile:
            configFile.write(directory)

    def setJsonDir(self, directory):
        self.jsonDir = directory

    # Run when the program is started for the first time, or whenever the JSON dir is not found
    def getJsonDir(self):
        print("Please enter the path to the game's JSON folder.")
        directory = input() # TODO Add a user interface for this

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

    def createItemsDict(self):
        self.items = {}
        self.itemsByID = {}

        # We have to pre-populate self.items with empty keys so that
        # handleObjectJson() works correctly
        for t in self.types.keys():
            self.items[t] = []
            self.itemsByID[t] = {}

    def loadJson(self, jsonFiles):
        print("Loading items from JSON...")
        self.loadTypes()
        self.createItemsDict()

        for jsonFile in jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                jsonContent = self.loadJsonFile(openedJsonFile)
                # Although most files are arrays of objects, some are just
                # one object. This needs to be handled with a type check
                if isinstance(jsonContent, list):
                    for obj in jsonContent:
                        self.handleObjectJson(obj)

    def loadJsonFile(self, openedJsonFile):
        try: #TODO Replace with if?
            jsonContent = json.load(openedJsonFile)
        except json.decoder.JSONDecodeError:
            print("Failed to read JSON file. Skipping it.")
            return None

        return jsonContent

    # Maps JSON types to an easily readable type string
    # Done solely for the sake of converting all the item types to "item"
    def loadTypes(self):
        with open("types.json", "r") as typeFile:
            self.types = dict(json.load(typeFile))

    def handleObjectJson(self, obj):
        # sometimes the function receives a list for some reason, so this
        # check prevents crash
        if isinstance(obj, dict):
            objType = self.resolveType(obj.get("type"))
            if objType:
                namedObj = self.setObjName(obj)
                objID = self.getObjectID(namedObj)
                self.items[objType].append(namedObj)
                if objID:
                    self.itemsByID[objType][objID] = namedObj

    # Turns type specified in JSON into type program can read
    def resolveType(self, jsonType):
        for objectType in self.types:
            if jsonType in self.types[objectType]:
                return objectType
        return None

    def getObjectID(self, obj):
        objID = obj.get("id")
        # For some reason, skills use the ident attribute
        if not objID:
            objID = obj.get("ident")

        return objID

    # Makes name attribute more search friendly.
    def setObjName(self, obj):
        name = obj.get("name")
        # Checks whether the name is a legacy name
        # lowercases name so search is not case sensitive
        if isinstance(name, str):
            obj["name"] = name.lower()
        elif isinstance(name, dict):
            buff = name.get("str")
            if buff:
                obj["name"] = buff.lower()
            else:
                obj["name"] = name.get("str_sp").lower()
        return obj

class JsonTranslator():
    def __init__(self):
        with open("translation.json", "r") as translationFile:
            self.translations = json.load(translationFile)

    def translate(self, rawJson, jsonType):
        rawJson = self.filterJson(rawJson, jsonType)

        return self.translateJson(rawJson, jsonType)
        #TODO add special case for martial arts bonuses.

    def filterJson(self, rawJson, jsonType):
        # These values are removed from JSON
        with open("unwanted.json", "r") as unwantedsFile:
            unwantedValues = dict(json.load(unwantedsFile))

        resultJson = {}

        for attribute in rawJson:
            if attribute in unwantedValues[jsonType] or attribute in unwantedValues["all"]:
                continue
            else:
                resultJson[attribute] = rawJson[attribute]
        return resultJson

    def translateJson(self, rawJson, jsonType):
        typeTranslations = self.translations[jsonType]
        translatedJson = {}
        for attribute in rawJson:
            translation = typeTranslations.get(attribute)
            if translation:
                translatedJson[translation] = rawJson[attribute]
            else:
                translatedJson[attribute] = rawJson[attribute]

        return translatedJson
