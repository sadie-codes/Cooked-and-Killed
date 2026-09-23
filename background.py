"""
Controls the backgrounds of the game and displays it
"""
import pyglet
import json
from constants import SCREEN_HEIGHT, SCREEN_WIDTH

class Background:
    def __init__(self, row, column, image_name, x=0, y=0, x_min=0, x_max=None, y_min=0, y_max=None, walls=None):
        self.row = row
        self.column = column
        self.image = pyglet.image.load("static/" + image_name)
        # Create the sprite once in __init__ for better performance
        self.sprite = pyglet.sprite.Sprite(img=self.image, x=x, y=y)
        
        self.width = self.image.width
        self.height = self.image.height
        self.x_min = x_min
        self.y_min = y_min
        if x_max == None:
            self.x_max = SCREEN_WIDTH
        else:
            self.x_max = x_max

        if y_max == None:
            self.y_max = SCREEN_HEIGHT
        else:
            self.y_max = y_max
        
        self.walls = walls if walls else []

    
    def draw(self):
        self.sprite.draw()
    
    #AI GENERATED
    #could be not allowing the screen shift
    def check_bounds(self, new_x, new_y):
        
        # Use a small buffer or ensure boundaries match SCREEN_WIDTH/HEIGHT
        if not(self.x_min <= new_x <= self.x_max and self.y_min <= new_y <= self.y_max):
            return False
        else:
            for wall in self.walls:
                x1, y1 = wall["p1"]
                x2, y2 = wall["p2"]
                side = wall.get("side", 1) #1 or -1
                d = (x2 - x1) * (new_y - y1) - (y2 - y1) * (new_x - x1)
            
                # If the player is on the wrong side of ANY wall, they are out of bounds
                if side > 0 and d < 0: return False
                if side < 0 and d > 0: return False
        return True


    @staticmethod
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


