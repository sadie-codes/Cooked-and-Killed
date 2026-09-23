import pyglet
import json
import math
class Food:
    MAX_GRAB_DISTANCE = 400
    foods = []
    food_batch = pyglet.graphics.Batch()
    food_group = pyglet.graphics.Group(order=0)
    drag_group = pyglet.graphics.Group(order=1)
    def __init__(self, name, image, inventory, bg_index_row=0, bg_index_column=0, x=500, y=400, scale=1, product=False):
        self.inventory = inventory
        self.x = x
        self.y = y
        self.image = pyglet.image.load(image)
        self.image.anchor_x = self.image.width//2
        self.image.anchor_y = self.image.height//2
        self.scale = scale
        self.sprite = pyglet.sprite.Sprite(self.image, x=self.x, y=self.y, batch=Food.food_batch)
        self.sprite.visible = not(product)
        self.is_moving = False
        self.dragging = False
        self.bx = 0
        self.by = 0
        self.released = None
        self.saved_slot = None
        self.current_slot = None
        self.in_inventory = False
        self.name = name
        self.is_collect = False
        self.bg_index_row = bg_index_row
        self.bg_index_column = bg_index_column
        Food.foods.append(self)

    def update_info(self, in_cinventory):
        #updates info
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.scale = self.scale
        if self.in_inventory and not(in_cinventory):
            self.sprite.visible = False
        else:
            self.sprite.visible = True

    def check_hit(self, mouse_x, mouse_y):
        return(self.x+(self.sprite.width/2)>mouse_x>self.x-(self.sprite.width/2) and self.y+(self.sprite.height/2)>mouse_y>self.y-(self.sprite.width/2))

    def collected(self, character):
        character.inventory.remove(self)
        for i in range(9):
            if self.inventory.saved_slots[i][0] == None:
                self.inventory.saved_slots[i][0] = self
                self.x = self.inventory.saved_slots[i][1]
                self.y = self.inventory.saved_slots[i][2]
                break
        self.in_inventory = True
        self.sprite.visible = False
        self.is_collect = True

    def on_mouse_released(self, dropped, in_inventory):
        if dropped and in_inventory:
            inv = self.inventory.sprite
            cell_w, cell_h = (inv.width / 3, inv.height / 3)
            rel_x = self.x - inv.x
            rel_y = self.y - inv.y
            if rel_x >= 0 and rel_y >= 0:
                grid_col = int(rel_x // cell_w)
                grid_row = int(rel_y // cell_h)
                slot_idx = grid_row * 3 + grid_col
                if 0 <= grid_col < 3 and 0 <= grid_row < 3:
                                target_slot = self.inventory.saved_slots[slot_idx]
                                if target_slot[0] is None or target_slot[0] == self:
                                    if self.current_slot is not None:
                                        self.inventory.saved_slots[self.current_slot][0] = None
                                    self.x = target_slot[1]
                                    self.y = target_slot[2]
                                    self.current_slot = slot_idx
                                    target_slot[0] = self
                                    self.sprite.position = (self.x, self.y)
                                    self.bx, self.by = (self.x, self.y)
        self.x, self.y = (self.bx, self.by)
        self.sprite.position = (self.x, self.y)
    @staticmethod
    def load_from_json(file_path, inventory):
        """Returns a list of Background objects without storing them in the class"""
        with open(file_path, "r") as file:
            data = json.load(file)
            item_list = []
            for item_data in data["food"]:
                # Pass image_name to init, then update other attributes
                cur_food = Food(item_data.pop("name"), item_data.pop("image_name"), inventory)
                for attribute_name, value in item_data.items():
                    setattr(cur_food, attribute_name, value)
                item_list.append(cur_food)
            return item_list
            
        
class Inventory:
    def __init__(self, image, player):
        self.image = pyglet.image.load(image)
        self.player = player
        self.sprite = pyglet.sprite.Sprite(self.image, x=player.x-150, y=player.y-150)
        self.sprite.scale = .65
        self.saved_slots = [[None, self.player.x+50, self.player.y+250], [None, self.player.x+150, self.player.y+250], [None, self.player.x+250, self.player.y+250], 
                            [None, self.player.x+50, self.player.y+150], [None, self.player.x+150, self.player.y+150], [None, self.player.x+250, self.player.y+150], 
                            [None, self.player.x+50, self.player.y+50], [None, self.player.x+150, self.player.y+50], [None, self.player.x+250, self.player.y+50]]
        self.offsets =  [
            (50, 250), (150, 250), (250, 250), # Top row
            (50, 150), (150, 150), (250, 150), # Middle row
            (50, 50),  (150, 50),  (250, 50)   # Bottom row
        ]
    def print_list(self):
        for food in self.saved_slots:
            if food != None:
                print(food.name)

    #fixed object positions with inventory with ai
    def update_slot_positions(self):
        # Update the background sprite position relative to the player
        self.sprite.x = self.player.x - self.sprite.width/2
        self.sprite.y = self.player.y - self.sprite.height/2


        for i, (off_x, off_y) in enumerate(self.offsets):
            # Update the stored slot coordinates
            new_x = self.sprite.x + off_x
            new_y = self.sprite.y + off_y
            self.saved_slots[i][1] = new_x
            self.saved_slots[i][2] = new_y

            # If a food item is currently in this slot, move its sprite too
            
            food_item = self.saved_slots[i][0]
            if food_item:
                food_item.x = new_x
                food_item.y = new_y
        

    def draw(self):
        self.x = self.player.x - 150
        self.y = self.player.y - 150
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.draw()
