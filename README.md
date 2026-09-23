What is Cooked and Killed?
-------------------------------------------------------------
Cooked and Killed is a horror game developed in my senior year computer science project as our main project throughout the 
semester. Since we had a harsh deadline to meet, this game has only basic features and character movement. The thought behind the 
game is that a character ends up in an abandoned restaurant where they need to cook meals and escape an evil chef to survive.
So far, the game has the character movement, inventory system, hiding mechanics, item mechanics, and environment interaction 
programmed. This game was programmed using a Python library called Pyglet.

Features
--------
- Character movement in all directions across mulitiple rooms
- Sprinting ability
- Starting menu
- Inventory mechanics (dragging, locking, opening, exiting)
- Environment boundaries
- Hiding abilities
- Item collecting

Challenges
-----
This was my first ever group programming project over a long period of time. We were not able to use GitHub due to computer restrictions, so we ended up using Google Drive, which made version control complex. We started to program animation, but image sizing became a big issue because different images had different qualities that needed to be dealt with. Similarly, inventory locking mechanics were difficult because, if we tried to update the image with a different image of separate dimensions, the coordinates would be off because it is hard-coded. This taught me that hard-coding aspects of a program can lead to a bigger problem later on and can be hard to work with.

Getting Started
-------------------------------
You will need to install the latest version of Python and pyglet for this game. <br>
git clone https://github.com/sadie-codes/Cooked-and-Killed <br>
pip install pyglet <br>
py main.py <br>
