import pyglet
from pyglet.window import key
from items import Food
import math
from environment import Hiding, Environment
from constants import DEBUG_MODE
class Character():
    SPRINT_MODIFIER = 2.0
    def __init__(self, image_name, x, y, speed, scale, hitbox_data):
        self.image = pyglet.image.load("static/" + image_name)
        self.x = x
        self.y = y
        self.scale = scale
        #sets the anchor of the image to the center
        self.image.anchor_x = self.image.width//2
        self.image.anchor_y = self.image.height//2
        self.sprite = pyglet.sprite.Sprite(self.image, x=self.x, y=self.y)
        self.speed = speed
        self.sprint = False
        self.inventory = []
        self.hiding = False
        self.data = hitbox_data

    @property
    def hitbox(self):
        s = self.sprite.scale
        return {
            "x": self.sprite.x + (self.data['offset_x'] * s),
            "y": self.sprite.y + (self.data['offset_y'] * s),
            "w": self.data['width'] * s,
            "h": self.data['height'] * s
        }
    
    def draw_character(self):
        """Draws the existing sprite without re-initializing it"""
        # Set scale once or only when it changes, not every frame
        self.sprite.scale = self.scale
        self.width = self.sprite.width
        self.height = self.sprite.height
        if not self.hiding and self.sprite.visible:
            if DEBUG_MODE:
                rect = pyglet.shapes.Rectangle(self.x + self.data["offset_x"] - self.hitbox["w"]/2, self.y + self.data["offset_y"] - self.hitbox["h"]/2, self.hitbox["w"], self.hitbox["h"], color=(70, 70, 70))
                rect.draw()
            self.sprite.draw()


    def is_sprinting(self, key_handler):
        """checks to see if the character is sprinting"""
        if key_handler[key.LSHIFT] or key_handler[key.RSHIFT]:
            if not(self.sprint):
                self.sprint = True
                self.speed = self.speed * Character.SPRINT_MODIFIER
        else:
            if self.sprint:
                self.sprint = False
                self.speed = self.speed/Character.SPRINT_MODIFIER

    def check_collision(self, new_hitbox):
        """Checks each of the hit boxes and if they overlap Params: self, other_obj Returns True if they overlap"""
        #AI GENERATED
        if self.sprite.visible:
            return (self.hitbox["x"] < new_hitbox["x"] + new_hitbox["w"] and
            self.hitbox["x"] + self.hitbox["w"] > new_hitbox["x"] and
            self.hitbox["y"] < new_hitbox["y"] + new_hitbox["h"] and
            self.hitbox["y"] + self.hitbox["h"] > new_hitbox["y"])
        
        return False
        

    def is_hitting_env(self, new_hitbox):
        is_collide = False
        for env in Environment.environment:
            if env.check_collision(new_hitbox):
                is_collide = True
                break
        return is_collide
    #AI FIXED
    def move(self, dt, key_handler, current_bg, game):
            self.is_sprinting(key_handler)
            bottom = self.y - (self.sprite.height/2)
        
            # Calculate intended movement
            dx = 0
            dy = 0
            
            if key_handler[key.W]: dy += self.speed * dt
            if key_handler[key.S]: dy -= self.speed * dt
            if key_handler[key.A]: dx -= self.speed * dt
            if key_handler[key.D]: dx += self.speed * dt

            new_x = self.x + dx
            new_y = self.y + dy
            bottom = new_y - (self.sprite.height / 2)

            # Test the NEW position
            #Positioning is based on the feet of the character
            new_hitbox = {"x":self.hitbox["x"] + dx, "y":self.hitbox["y"] + dy, "w":self.hitbox["w"], "h":self.hitbox["h"]}

            in_bounds_x = current_bg.check_bounds(new_x, self.y - self.sprite.height / 2)
            in_bounds_y = current_bg.check_bounds(self.x, bottom)
            if self.is_hitting_env(new_hitbox):
                return
            elif not(in_bounds_x) or not(in_bounds_y):
                game.change_backgrounds(new_x, new_y)
            else:
                self.x = new_x
                self.y = new_y
                self.sprite.position = (self.x, self.y, self.sprite.z)

    
    def nearest_food(self, items):
        """finds the nearest food and returns that food with the least distance"""
        least_distance = -1
        nearest_food = None
        for food in items:
            x_distance = abs(food.sprite.x - self.sprite.x)
            y_distance = abs(food.sprite.y - self.sprite.y)
            total_distance = math.sqrt(x_distance**2 + y_distance**2)
            if (least_distance == -1 or least_distance > total_distance) and not(food.is_collect) and total_distance <= Food.MAX_GRAB_DISTANCE:
                least_distance = total_distance
                nearest_food = food
        return nearest_food


    def grab_food(self, food):
        """grabs the nearest food to the character"""
        if food:
            food.sprite.visible = False
            self.inventory.append(food)
    
    def nearest_hiding_spot(self):
        """finds the nearest hiding spot and returns that spot with the least distance"""
        least_distance = -1
        nearest_spot = None
        for spot in Hiding.spots:
            x_distance = abs(spot.sprite.x - self.sprite.x)
            y_distance = abs(spot.sprite.y - self.sprite.y)
            total_distance = math.sqrt(x_distance**2 + y_distance**2)
            if (least_distance == -1 or least_distance > total_distance) and total_distance <= Hiding.MAX_GRAB_DISTANCE:
                least_distance = total_distance
                nearest_spot = spot
        return nearest_spot
