import json
from background import Background
#JSON SYSTEM IS GOOD, NOW ADJUST CODE TO MATCH IT
def load_from_json(file_path):
        """Returns a list of Background objects without storing them in the class"""
        with open(file_path, "r") as file:
            data = json.load(file)
        bgs = {} #bgs[row][col] == Background
        for bg_data in data["backgrounds"]:
            row, col = bg_data["row"], bg_data["col"]
            if row not in bgs:
                bgs[row] = {}
            bgs[row][col] = Background(row, col, bg_data["image_name"])
            for attribute_name, value in bg_data.items():
                    setattr(bgs[row][col], attribute_name, value)
        return bgs
bgs = load_from_json("presets.json")
for row , row_bgs in bgs.items():
    for col, the_bg in row_bgs.items():
        print(vars(the_bg))