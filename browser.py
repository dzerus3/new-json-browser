import json
import glob
import os

class JsonLoader:
    jsonDir = ""
    loadedJson = []

    def __init__(self):
        self.jsonDir = readJsonDir()
        self.loadedJson = loadJson()

    # Get the Json directory from file; thanks to @rektrex for this function
    def readJsonDir():
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
            directory = getJsonDir()
            with open(configfile, 'w') as configFile:
                configFile.write(directory)

        finally:
            return directory

    # Run when the program is started for the first time, or whenever the JSON dir is not found
    def getJsonDir():
        print("Please enter the path to the game's JSON folder.")
        # directory = input() # TODO

        # Recursive call to itself until a valid location is specified
        if not os.path.isdir(directory):
            print("This path appears to be wrong.")
            directory = getJsonDir()

        return directory

    # Loads game's JSON into memory
    def loadJson():
        result = []

        # Gets the name of each JSON file
        # I'm not sure whether os.path.join() is the best idea here since it's not an actual directory, but it should work
        jsonFiles = glob.glob(os.path.join(self.jsonDir, "/**/*.json", recursive=True))

        # Loops through every file name and loads it into a list
        for jsonFile in jsonFiles:
            with open(jsonFile, "r", encoding="utf8") as openedJsonFile:
                result.append(json.load(openedJsonFile))

        return result
