import pyglet
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
image = pyglet.image.load("static/Kitchen(2).png")
win = pyglet.window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
sprite = pyglet.sprite.Sprite(img=image, x=0, y=0)
label = pyglet.text.Label(f"{0}, {0}", font_size=25, x=10,y=win.height-25)
scale = min(win.width/image.width, win.height/image.height)
sprite.scale = scale

@win.event
def on_mouse_motion(x, y, dx, dy):
    global label
    label = pyglet.text.Label(f"{x}, {y}", font_size=25, x=10,y=win.height-25)

@win.event
def on_draw():
    win.clear()
    sprite.draw()
    label.draw()

pyglet.app.run()