import os
path_file = os.path.realpath(os.path.join(os.path.dirname((os.path.dirname(__file__))), "parameters.txt"))
class SaveFilePath(): 
    def WriteFile(self, path): 
        file = open(path_file, "w")
        file.write(path)
        file.close()        

    def ReadFile(self):
        file = open(path_file, "r")
        content = file.read()
        return content
