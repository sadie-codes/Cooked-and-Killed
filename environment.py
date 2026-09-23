import pyglet
import json
import math

class Environment:
    environment = []
    environment_batch = pyglet.graphics.Batch()
    def __init__(self, name, image, hitbox_data, bg_index_row=0, bg_index_column=0, x=500, y=500, scale=1):
        self.name = name
        self.x = x
        self.y = y
        self.bg_index_row = bg_index_row
        self.bg_index_column = bg_index_column
        self.image = pyglet.image.load("static/" + image)
        self.image.anchor_x = self.image.width//2
        self.image.anchor_y = self.image.height//2
        self.scale = scale
        self.sprite = pyglet.sprite.Sprite(self.image, x=self.x, y=self.y, batch=Environment.environment_batch)
        self.sprite.scale = self.scale
        self.data = hitbox_data

        Environment.environment.append(self)
    @property
    def hitbox(self):
        s = self.sprite.scale
        return {
            "x": self.sprite.x + (self.data['offset_x'] * s),
            "y": self.sprite.y + (self.data['offset_y'] * s ),
            "w": self.data['width'] * s,
            "h": self.data['height'] * s
        }
    def update_info(self, bg_index_row, bg_index_column):
        self.sprite.scale = self.scale
        self.width = self.sprite.width
        self.height = self.sprite.height
        self.x = self.sprite.x
        self.y = self.sprite.y
        self.sprite.visible = (bg_index_row == self.bg_index_row and self.bg_index_column == bg_index_column)

    def check_collision(self, new_hitbox):
        """Checks each of the hit boxes and if they overlap Params: self, other_obj Returns True if they overlap"""
        #AI GENERATED
        """
        if self.sprite.visible:
            return (self.hitbox["x"] < new_hitbox["x"] + new_hitbox["w"] and
            self.hitbox["x"] + self.hitbox["w"] > new_hitbox["x"] and
            self.hitbox["y"] < new_hitbox["y"] + new_hitbox["h"] and
            self.hitbox["y"] + self.hitbox["h"] > new_hitbox["y"])
        return False
        """

        if self.sprite.visible:
            h1 = self.hitbox
            h2 = new_hitbox

            blx1 = h1["x"] - h1["w"]/2
            blx2 = h2["x"] - h2["w"]/2
            bly1 = h1["y"] - h1["h"]/2
            bly2 = h2["y"] - h2["h"]/2

            trx1 = h1["x"] + h1["w"]/2
            trx2 = h2["x"] + h2["w"]/2
            try1 = h1["y"] + h1["h"]/2
            try2 = h2["y"] + h2["h"]/2
            return (blx1 < trx2 and trx1 > blx2 and bly1 < try2 and try1 > bly2)
    
    def load_from_json(file_path, data_str):
        """Returns a list of Background objects without storing them in the class"""
        with open(file_path, "r") as file:
            data = json.load(file)
            environment_list = []
            for environment_data in data[data_str]:
                # Pass image_name to init, then update other attributes
                cur_object = Environment(environment_data.pop("name"), environment_data.pop("image_name"), environment_data.pop("hitbox_data"))
                for attribute_name, value in environment_data.items():
                    setattr(cur_object, attribute_name, value)
                cur_object.sprite.x = cur_object.x
                cur_object.sprite.y = cur_object.y
                environment_list.append(cur_object)
            return environment_list
        
class Hiding(Environment):
    MAX_GRAB_DISTANCE = 300
    spots = []
    def __init__(self, name, image, hitbox_data, bg_index_row=0, bg_index_column=0, x=500, y=500, scale=1):
        super().__init__(name, image, hitbox_data, bg_index_row, bg_index_column, x, y, scale)
        Hiding.spots.append(self)
    
    @staticmethod
    def load_from_json(file_path, data_str="hiding_spots"):
        """Returns a list of Background objects without storing them in the class"""
        with open(file_path, "r") as file:
            data = json.load(file)
            spots_list = []
            for spots_data in data[data_str]:
                # Pass image_name to init, then update other attributes
                cur_spot = Hiding(spots_data.pop("name"), spots_data.pop("image_name"), spots_data.pop("hitbox_data"))
                for attribute_name, value in spots_data.items():
                    setattr(cur_spot, attribute_name, value)
                cur_spot.sprite.x = cur_spot.x
                cur_spot.sprite.y = cur_spot.y
                spots_list.append(cur_spot)
            return spots_list
class Door():
    doors = []
    def __init__(self, id, x, y, bg_index_row, bg_index_column, pair_door, exit_entry, exit_distance):
        self.id = id
        self.x = x
        self.y = y
        self.bg_index_row = bg_index_row
        self.bg_index_column = bg_index_column  
        self.pair_door = pair_door
        self.exit_entry = exit_entry
        self.exit_distance = exit_distance
        Door.doors.append(self)
    def enter(self, game, player):
        """finds the pair door and calls the exit function on it"""
        pair_door_obj = None
        for door in Door.doors:
            if door.id == self.pair_door:
                pair_door_obj = door
        pair_door_obj.exit(game, player)

    def exit(self, game, player):
        """exits based on where the door is and where it should go out"""
        if self.exit_entry == "right":
            player.x = self.x + self.exit_distance
            player.y = self.y
        elif self.exit_entry == "left":
            player.x = self.x - self.exit_distance
            player.y = self.y
        elif self.exit_entry == "up":
            player.y = self.y + self.exit_distance
            player.x = self.x
        elif self.exit_entry == "down":
            player.y = self.y - self.exit_distance
            player.x = self.x
        else:
            player.x = self.x
            player.y = self.y
        
        game.cur_index_row = self.bg_index_row
        game.cur_index_column = self.bg_index_column
        game.cur_bg = game.bgs[self.bg_index_row][self.bg_index_column]
    @staticmethod
    def load_from_json(file_path):
      """loads info from the json file"""
      with open(file_path, "r") as file:
            data = json.load(file)
            door_list = []
            for door_data in data["doors"]:
                # Pass image_name to init, then update other attributes
                cur_door = Door(door_data.pop("id"), door_data.pop("x"), door_data.pop("y"), door_data.pop("bg_index_row"), door_data.pop("bg_index_column"), door_data.pop("pair_door"), door_data.pop("exit_entry"), door_data.pop("exit_distance"))
                for attribute_name, value in door_data.items():
                    setattr(cur_door, attribute_name, value)
                door_list.append(cur_door)
            return door_list



class Cooking():
    MAX_COOK_DISTANCE = 300
    cooking_spots = []
    cooking_batch = pyglet.graphics.Batch()
    def __init__(self, name, image, bg_index = 0, x=500, y=500, scale=1):
        super().__init__(name, image, bg_index, x, y, scale)
        Cooking.cooking_spots.append(self)

class Cooking_Menu():
    def __init__(self, inventory, image):
        self.image = image
        self.inventory = inventory
        self.menu_slot = [(None, 1483, 573), (None, 1687, 573), 
                                (None, 1482, 376), (None, 1684, 376)]
        self.inventory_slots = inventory.saved_slots[:]
        self.offsets =  [
            (50, 250), (150, 250), (250, 250), # Top row
            (50, 150), (150, 150), (250, 150), # Middle row
            (50, 50),  (150, 50),  (250, 50)   # Bottom row
        ]

        self.on_screen = False
        self.recipes = {"pb_j":["bread", "peanut_butter", "jelly"], "ex":["jack", "hi", "bruv"]}

    def activate(self):
        self.on_screen = True 
        self.load_inventory()
    
    def load_inventory(self):
        """loads the inventory on the left side and puts the food in their correct slots"""
        self.inventory.x = 227
        self.inventory.y = 568
        new_slots = []
        for s in range(len(self.inventory_slots)):
            cur_slot = self.inventory_slots[s]
            new_slot = (cur_slot[0], self.inventory.x + self.offset[s][0], self.inventory.y + self.offset[s][1])
            if cur_slot[0]:
                cur_slot[0].x = new_slot[1]
                cur_slot[0].y = new_slot[2]
            new_slots.append(new_slot)
        self.inventory_slots = new_slots

    def on_mouse_released(self, mouse_x, mouse_y, food, foods, character):
        all_slots = []
        all_slots.extend(self.inventory_slots)
        all_slots.extend(self.menu_slot)

        nearest_slot = None
        nearest_slot_distance = 0
        for slot in all_slots:
            slot_x = slot[1]
            slot_y = slot[2]
            distance = math.sqrt((mouse_x - slot_x)**2 + (mouse_y - slot_y)**2)
            if (nearest_slot == None or distance < nearest_slot_distance) and nearest_slot[0] == None:
                nearest_slot = slot
                nearest_slot_distance = distance
        nearest_slot[0] = food
        food.x = nearest_slot[1]
        food.y = nearest_slot[2]
        self.inventory_slots = all_slots[0:9]
        self.menu_slot = all_slots[9:]

        self.make_recipe(foods, character)
    
    def adjust_slot_state(self, food_clicked):
        for slot in self.inventory_slots:
            if slot[0] == food_clicked:
                slot[0] = None
                return
        for slot_menu in self.menu_slot:
            if slot_menu[0] == food_clicked:
                slot_menu[0] = None
                return
    
    def make_recipe(self, foods, character):
        """checks to see if the recipe exists"""
        items_in_menu = []
        for slot_menu in self.menu_slot:
            items_in_menu.append(slot_menu[0])
        
        make = False
        the_product = None
        for product, recipe in self.recipes.items():
            if sorted(recipe) == sorted(items_in_menu):
                make = True
                the_product = product
        new_food = foods[0]
        for f in foods:
            if f.name == the_product:
                new_food = f
        if make:
            for slot_menu in self.menu_slot:
                character.inventory.remove(slot_menu[0])
                del slot_menu[0]
            
            self.menu_slot = [(new_food, 1483, 573), (None, 1687, 573), 
                                (None, 1482, 376), (None, 1684, 376)]
            character.inventory.append(new_food)
            
            
        



