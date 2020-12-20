import json
import re
import glob
import os
import textdistance

class JsonSearcher():
    def __init__(self, rawJson):
        self.rawJson = rawJson

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
            if requiredAttributes[attribute] == entry[attribute]:
                equal += 1
                totalSimilarity += 1
            elif similarity > 0.7:
                totalSimilarity += similarity
            else:
                totalSimilarity = 0
                break

        if equal == len(requiredAttributes):
            return 100
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

class JsonLoader(): #TODO Make this return the loaded JSON, rather than passing the class itself around.
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

        # TODO: Change this to glob entire game directory
        # This way it will automatically read mods too
        for jsonFile in glob.iglob(wildcard, recursive=True):
            jsonFiles.append(jsonFile)

        return jsonFiles

    def loadJson(self):
        print("Loading items from JSON...")
        self.loadTypes()

        self.items = {}

        # We have to pre-populate self.items with empty keys so that
        # handleObjectJson() works correctly
        for t in self.types.keys():
            self.items[t] = []

        for jsonFile in self.jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                try: #TODO Replace with if?
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

    # Maps JSON types to an easily readable type string
    # Done solely for the sake of converting all the item types to "item"
    def loadTypes(self):
        with open("types.json", "r") as typeFile:
            self.types = dict(json.load(typeFile))

    def handleObjectJson(self, obj):
        objType = self.resolveType(obj["type"])
        if objType:
            namedObj = self.setObjName(obj)
            self.items[objType].append(namedObj)

    def resolveType(self, jsonType):
        for objectType in self.types:
            if jsonType in self.types[objectType]:
                return objectType
        return None

    # Makes name more search friendly.
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
        translationFile = open("translation.json", "r")
        self.translations = json.load(translationFile)

    def translate(self, rawJson, jsonType):
        rawJson = self.filterJson(rawJson, jsonType)

        return self.translateJson(rawJson, jsonType)
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
                          "ident"],
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
        translatedJson = {}
        for attribute in rawJson:
            translation = typeTranslations.get(attribute)
            if translation:
                translatedJson[translation] = rawJson[attribute]
            else:
                translatedJson[attribute] = rawJson[attribute]

        return translatedJson
