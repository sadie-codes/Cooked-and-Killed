import pyglet
from background import Background
from character_movement import Character
from pyglet.window import key
from items import Food
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, FRAME_RATE, TOGGLE_DELAY, DEBUG_MODE
from items import Inventory
from environment import Hiding, Environment, Door, Cooking_Menu
from pyglet import shapes

# Setup window and player
window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT)
hitbox={"offset_x":0, "offset_y":0, "width":200, "height":400}
chris = Character("chris.png", 600, 300, 300, .85, hitbox)

#key handler that receives user input
key_handler = key.KeyStateHandler()
window.push_handlers(key_handler)

#inventory object and inventory cooldowns
inventory_save = Inventory("j_grid.png", chris)
in_inventory = False
selected_item = None
inventory_toggle_cooldown = 0.0

cooking_menu = Cooking_Menu(inventory_save, "Cooking Menu.png")

class GameState():
    """GameState Class controls all of the images on the screen and the state of the room"""
    def __init__(self, player, bgs, items, hiding_spots, doors, start_index_column=3, start_index_row=0):
        """initializes a game with player, bgs, items, and the start_index of the backgrounds"""
        self.player = player
        #backgrounds list and current background the screen is showing
        self.bgs = bgs
        self.cur_index_row = start_index_row
        self.cur_index_column = start_index_column
        self.cur_bg = self.bgs[self.cur_index_row][self.cur_index_column]
        self.game_state = "MENU"

        #food on screen
        self.items = items
        self.hiding_spots = hiding_spots
        self.doors = doors

        #interaction
        self.interaction_label = pyglet.text.Label("", font_size=30, anchor_x="center")
        self.draw_interaction_lbl = False

        #inventory
        self.inventory_save = Inventory("j_grid.png", chris)
        self.in_inventory = False
        self.selected_item = None
        self.inventory_toggle_cooldown = 0.0
        self.MAX_DISTANCE = 400
        self.scale_bgs()
        self.start = pyglet.image.load("static/" + "Start.png")
        self.sprite_start = pyglet.sprite.Sprite(self.start, x=100, y=200)
        self.quit = pyglet.image.load("static/" + "Quit.png")
        self.sprite_quit = pyglet.sprite.Sprite(self.quit, x=1000, y=200)

    def change_backgrounds(self, new_x, new_y, destination_door=None):
                # Transition Forward
        #if the type of room change is not through a door, then it means the user is traveling between the same room
        if destination_door == None:
            bottom = new_y - self.player.sprite.height/2
            transitioned = False
            #Tests to see if the user steps outside of the screens boundaries
            if new_x > SCREEN_WIDTH and self.cur_index_column + 1 in self.bgs[self.cur_index_row]:
                self.cur_index_column += 1
                self.player.x = 5 # Small offset to prevent bouncing
                transitioned = True
            # Transition Backward
            elif new_x < 0 and self.cur_index_column > 0:
                self.cur_index_column -= 1
                self.player.x = SCREEN_WIDTH - 5
                transitioned = True
            elif bottom < 0 and self.cur_index_row + 1 < len(self.bgs) and self.cur_index_column in self.bgs[self.cur_index_row + 1]:
                self.cur_index_row += 1
                self.player.y = SCREEN_HEIGHT - 5 - self.player.sprite.height/2
                transitioned = True
            elif bottom > SCREEN_HEIGHT and self.cur_index_row > 0 and self.cur_index_column in self.bgs[self.cur_index_row - 1]:
                self.cur_index_row -= 1
                self.player.y = 5 + self.player.sprite.height/2
                transitioned = True

            #If the user changes backgrounds then change the current background and update the surroundings visibility
            if transitioned:
                self.cur_bg = self.bgs[self.cur_index_row][self.cur_index_column]
        self.update_surroundings_visibility()
        
    
    def scale_bgs(self):
        """scales the backgrounds according to the sprites' scale factor"""
        global in_inventory
        for bg_row, bgs in self.bgs.items():
            for col, bg in bgs.items():
                scale = min(window.width/bg.image.width, window.height/bg.image.height)
                bg.sprite.scale = scale
                bg.width *= scale
                bg.height *= scale

    def update_surroundings_visibility(self):
        
        """changes the visibility of items depending on the background, so they don't appear on the next screen"""
        for item in self.items:
            if item.in_inventory:
                item.bg_index_row = self.cur_index_row
                item.bg_index_column = self.cur_index_column
            
            if item.bg_index_row == self.cur_index_row and item.bg_index_column == self.cur_index_column and ((item.in_inventory and self.in_inventory) or not(item.in_inventory)):
                item.sprite.visible = True
            else:
                item.sprite.visible = False
            item.sprite.x = item.x
            item.sprite.y = item.y
            item.sprite.scale = item.scale
        
        for spot in Hiding.spots:
            if spot.bg_index_row != self.cur_index_row or spot.bg_index_column != self.cur_index_column:
                spot.sprite.visible = False
            else:
                spot.sprite.visible = True
    
    def open_inventory(self):
        """opens the inventory"""
        self.in_inventory = not self.in_inventory
        self.inventory_toggle_cooldown = TOGGLE_DELAY
        for food in self.items:
            if food.is_collect and not(food.in_inventory):
                food.sprite.visible = False
            else:
                food.sprite.visible = True
            if food.is_collect:
                for i in range(9):
                    if inventory_save.saved_slots[i][0] == None and food.in_inventory == False:
                        inventory_save.saved_slots[i][0] = food
                        food.x = inventory_save.saved_slots[i][1]
                        food.y = inventory_save.saved_slots[i][2]
                        food.in_inventory = True
                        break
            #draws label based on if the user is in the inventory or not
        if self.in_inventory:
            self.draw_interaction_lbl = False
        else:
            self.draw_interaction_lbl = True

    def get_nearest_interactable(self):
        """returns the nearest interactable item"""
        #AI
        # Combine all items and spots that are on the current screen
        potential_targets = []
        potential_targets.extend([item for item in self.items if not item.in_inventory])
        potential_targets.extend(self.hiding_spots)
        potential_targets.extend(self.doors)

        nearest_obj = None
        min_dist = float('inf') # Start with "infinity"

        for obj in potential_targets:
            if obj.bg_index_row == self.cur_index_row and obj.bg_index_column == self.cur_index_column and (type(obj) == Door or obj.sprite.visible):
                # Simple Euclidean distance: sqrt((x2-x1)^2 + (y2-y1)^2)
                dist = ((self.player.x - obj.x)**2 + (self.player.y - obj.y)**2)**0.5
                
                # Update if this one is closer than our previous best
                if dist < min_dist:
                    min_dist = dist
                    nearest_obj = obj
                    
        # Return object only if it's within a reasonable "interaction range"
        return nearest_obj if min_dist < self.MAX_DISTANCE else None

    def handle_interaction(self):
        """handles the interaction by drawing the label and handling the key press"""
        target = game.get_nearest_interactable()

        if target:
            # Check the type to decide what text to show
            if isinstance(target, Hiding):
                verb = "Hide"
                key_needed = key.E
            elif isinstance(target, Food):
                verb = "Grab"
                key_needed = key.Q
            elif isinstance(target, Door):
                verb = "Enter"
                key_needed = key.E
            
            # Update your label once instead of recreating it
            self.interaction_label.text = f"Press {key.symbol_string(key_needed)} to {verb}!"
            self.interaction_label.x, self.interaction_label.y = target.x, target.y + 50
            self.draw_interaction_lbl = True # Reuse one "show label" flag

            # Handle the actual press
            if key_handler[key_needed] and game.inventory_toggle_cooldown <= 0:
                game.inventory_toggle_cooldown = TOGGLE_DELAY
                if isinstance(target, Hiding):
                    chris.hiding = not chris.hiding
                elif isinstance(target, Food):
                    chris.grab_food(target)
                    target.collected(chris)
                elif isinstance(target, Door):
                    target.enter(game, chris)
        else:
            self.draw_interaction_lbl = False
        
    def is_clicked(self, image, mouse_x, mouse_y):
        """Checks if mouse coordinates are inside the label's bounding box."""
        # Since anchor_x is 'center', the x-range is (x - width/2) to (x + width/2)
        left = image.x
        right = image.x + image.width
        bottom = image.y
        top = image.y + image.height
        
        return left <= mouse_x <= right and bottom <= mouse_y <= top

    def draw_menu(self):
        self.sprite_quit.draw()
        self.sprite_start.draw()
    
# Initialize game state using the new static method
game = GameState(chris, Background.load_from_json("presets.json"), Food.load_from_json("presets.json", inventory_save), Hiding.load_from_json("presets.json"), Door.load_from_json("presets.json"))

def update(dt):
    """Updates the screen every frame and is used for charcter movement along with anything requiring key presses. Params: dt Return: None"""
    if game.game_state != "MENU":
        #controls the inventory cooldown every frame
        if game.inventory_toggle_cooldown > 0:
            game.inventory_toggle_cooldown -= dt
        if not game.in_inventory:
            game.handle_interaction()
        #tracks the food the user is trying to grab
        if key_handler[key.F] and game.inventory_toggle_cooldown <= 0:
            game.open_inventory()
        if not game.in_inventory and chris.hiding == False:
            chris.move(dt, key_handler, game.cur_bg, game)
            
        game.update_surroundings_visibility()
    elif game.game_state == "MENU":
        pass


pyglet.clock.schedule_interval(update, (1/FRAME_RATE))

@window.event
def on_draw():
    window.clear()
    # Draw the current background instance
    game.cur_bg.draw()

    if game.game_state == "PLAYING":
        render_list = []
        for env in Environment.environment:
            env.update_info(game.cur_index_row, game.cur_index_column)
            if env.sprite.visible:
                render_list.append(env)
        render_list.append(chris)

        render_list.sort(key=lambda obj: obj.y, reverse=True)
        for obj in render_list:
            if obj == chris:
                chris.draw_character()
            else:
                if DEBUG_MODE:
                    env_rect = pyglet.shapes.Rectangle(obj.x + obj.data["offset_x"]- obj.hitbox["w"]/2, obj.y + obj.data["offset_y"] - obj.hitbox["h"]/2, obj.hitbox["w"], obj.hitbox["h"], color=(70, 70, 70))
                    env_rect.draw()
                obj.sprite.draw()

        if game.in_inventory:
            game.inventory_save.draw()
        Food.food_batch.draw()
        if game.draw_interaction_lbl:
            game.interaction_label.draw()
    
    if game.game_state == "MENU":
        game.draw_menu()

    


@window.event
def on_mouse_press(mouse_x, mouse_y, button, modifier):
    if game.game_state == "MENU":
        # Check if START was clicked
        if game.is_clicked(game.sprite_start, mouse_x, mouse_y):
            game.cur_index_row = 1
            game.cur_index_column = 2
            game.cur_bg = game.bgs[game.cur_index_row][game.cur_index_column]
            game.update_surroundings_visibility()
            game.change_backgrounds(300, 300)
            game.game_state = "PLAYING"
            
        # Check if QUIT was clicked
        elif game.is_clicked(game.sprite_quit , mouse_x, mouse_y):
            pyglet.app.exit()

    if game.in_inventory:
        for food in game.items:
            if food.check_hit(mouse_x, mouse_y) and food.is_collect:
                game.selected_item = food
                game.selected_item.bx = game.selected_item.x
                game.selected_item.by = game.selected_item.y
                game.selected_item.dragging = True
                game.selected_item.inventory.saved_slots[food.current_slot][0] = None
                game.selected_item.on_mouse_released(False, game.in_inventory)
                #if the game state equals cooking, adjust the slot_state

                if game.game_state == "COOKING":
                    cooking_menu.adjust_slot_state(food)
                break

@window.event    
def on_mouse_drag(mouse_x, mouse_y, dx, dy, button, modifier):

    if game.in_inventory:
        if game.selected_item and game.selected_item.dragging:
            game.selected_item.x = mouse_x
            game.selected_item.y = mouse_y
            #switches the group so that the items don't drag under each other
            game.selected_item.sprite.group = Food.drag_group

@window.event
def on_mouse_release(mouse_x, mouse_y, button, modifier):
    """on mouse release the item is not being dragged anymore and """

    if game.in_inventory:
        if game.selected_item:
            #if the mode is in cooking, do the cooking version of on_mouse released
            if game.game_state == "COOKING":
                cooking_menu.on_mouse_released(mouse_x, mouse_y, game.selected_item)
            else:
                game.selected_item.on_mouse_released(True, game.in_inventory)
            game.selected_item.dragging = False
            #switches the group so that the items don't drag under each other
            game.selected_item.sprite.group = Food.food_group
            game.selected_item = None

pyglet.app.run()
