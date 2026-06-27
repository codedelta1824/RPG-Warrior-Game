import os
import pygame

os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

paths = [
    r"d:\Ayyan's Data\Warrior Game\assets\images\Left Sword Man\idle1.png",
    r"d:\Ayyan's Data\Warrior Game\assets\images\Right Sword Man\idle1.png",
]

for p in paths:
    print('Checking', p)
    print('exists:', os.path.exists(p))
    try:
        img = pygame.image.load(p).convert_alpha()
        print('loaded size:', img.get_size())
    except Exception as e:
        print('load error:', e)

print('Done')
