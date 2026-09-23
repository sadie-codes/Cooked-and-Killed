import pyglet
import json
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
        self.image = pyglet.image.load("static/" + image)
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

    def on_mouse_released(self, released, in_inventory):
        if self.is_collect:
            if released:
                self.released = self
                self.current_slot = self.saved_slot
            else:
                self.released = None
                
            
            if self.inventory.sprite.x+100>self.x>self.inventory.sprite.x and self.inventory.sprite.y+100>self.y>self.inventory.sprite.y:
                self.x = self.inventory.sprite.x+50
                self.y = self.inventory.sprite.y+50
                self.inventory.saved_slots[6][0] = self.released
                self.saved_slot = 6
            
            if self.inventory.sprite.x+200>self.x>self.inventory.sprite.x+100 and self.inventory.sprite.y+100>self.y>self.inventory.sprite.y:
                self.x = self.inventory.sprite.x+150
                self.y = self.inventory.sprite.y+50
                self.inventory.saved_slots[7][0] = self.released
                self.saved_slot = 7
            
            if self.inventory.sprite.x+300>self.x>self.inventory.sprite.x+200 and self.inventory.sprite.y+100>self.y>self.inventory.sprite.y:
                self.x = self.inventory.sprite.x+250
                self.y = self.inventory.sprite.y+50
                self.inventory.saved_slots[8][0] = self.released
                self.saved_slot = 8
            
            if self.inventory.sprite.x+100>self.x>self.inventory.sprite.x and self.inventory.sprite.y+200>self.y>self.inventory.sprite.y+100:
                self.x = self.inventory.sprite.x+50
                self.y = self.inventory.sprite.y+150
                self.inventory.saved_slots[3][0] = self.released
                self.saved_slot = 3
            
            if self.inventory.sprite.x+200>self.x>self.inventory.sprite.x+100 and self.inventory.sprite.y+200>self.y>self.inventory.sprite.y+100:
                self.x = self.inventory.sprite.x+150
                self.y = self.inventory.sprite.y+150
                self.inventory.saved_slots[4][0] = self.released
                self.saved_slot = 4

            if self.inventory.sprite.x+300>self.x>self.inventory.sprite.x+200 and self.inventory.sprite.y+200>self.y>self.inventory.sprite.y+100:
                self.x = self.inventory.sprite.x+250
                self.y = self.inventory.sprite.y+150
                self.inventory.saved_slots[5][0] = self.released
                self.saved_slot = 5

            if self.inventory.sprite.x+100>self.x>self.inventory.sprite.x and self.inventory.sprite.y+300>self.y>self.inventory.sprite.y+200:
                self.x = self.inventory.sprite.x+50
                self.y = self.inventory.sprite.y+250
                self.inventory.saved_slots[0][0] = self.released
                self.saved_slot = 0

            if self.inventory.sprite.x+200>self.x>self.inventory.sprite.x+100 and self.inventory.sprite.y+300>self.y>self.inventory.sprite.y+200:
                self.x = self.inventory.sprite.x+150
                self.y = self.inventory.sprite.y+250
                self.inventory.saved_slots[1][0] = self.released
                self.saved_slot = 1
            
            if self.inventory.sprite.x+300>self.x>self.inventory.sprite.x+200 and self.inventory.sprite.y+300>self.y>self.inventory.sprite.y+200:
                self.x = self.inventory.sprite.x+250
                self.y = self.inventory.sprite.y+250
                self.inventory.saved_slots[2][0] = self.released
                self.saved_slot = 2

            if released:
                for food in Food.foods:
                    if food == self:
                        pass
                    else:
                        if self.x == food.x and self.y == food.y:
                            self.x = self.bx
                            self.y = self.by
                            self.inventory.saved_slots[self.saved_slot][0] = food
                            if self.current_slot != None:
                                self.inventory.saved_slots[self.current_slot][0] = self
            
            if not(self.inventory.sprite.x+300>self.x>self.inventory.sprite.x and self.inventory.sprite.y+300>self.y>self.inventory.sprite.y):
                self.inventory.saved_slots[self.current_slot][0] = self
                self.x = self.inventory.saved_slots[self.current_slot][1]
                self.y = self.inventory.saved_slots[self.current_slot][2]
            
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
        self.image = pyglet.image.load("static/" + image)
        self.player = player
        self.sprite = pyglet.sprite.Sprite(self.image, 682, 264)
        self.sprite.x = 682
        self.sprite.y = 264
        self.sprite.scale = 3
        self.saved_slots = [[None, self.sprite.x+50, self.sprite.y+250], [None, self.sprite.x+150, self.sprite.y+250], [None, self.sprite.x+250, self.sprite.y+250], 
                            [None, self.sprite.x+50, self.sprite.y+150], [None, self.sprite.x+150, self.sprite.y+150], [None, self.sprite.x+250, self.sprite.y+150], 
                            [None, self.sprite.x+50, self.sprite.y+50], [None, self.sprite.x+150, self.sprite.y+50], [None, self.sprite.x+250, self.sprite.y+50]]
    
    def print_list(self):
        for food in self.saved_slots:
            if food != None:
                print(food.name)


    def draw(self):
        self.sprite.draw()
