import os.path


import json 
filepath = os.path.dirname(__file__)
class SaveParameters(): 

    def __init__(self): 
        pass
           
    def WriteFile(self, data): 
        json_object = json.dumps(data, indent=4)
        with open(os.path.join(filepath, "parameters.json"), "w") as outfile:
            outfile.write(json_object)     

    def ReadFile(self):
        with open(os.path.join(filepath, "parameters.json"), 'r') as openfile:
            json_object = json.load(openfile)
        return json_object
    
