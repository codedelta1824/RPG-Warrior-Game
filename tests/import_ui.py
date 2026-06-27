import sys
sys.path.append(r"d:\Ayyan's Data\Warrior Game")
import pygame
print('pygame init:', pygame.get_init())
try:
    import src.ui as ui
    print('Loaded ui module; avatar surfaces sizes:', ui.avatar_left.get_size(), ui.avatar_right.get_size())
except Exception as e:
    print('ui import error:', e)
