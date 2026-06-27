import sys
sys.path.append(r"d:\Ayyan's Data\Warrior Game")
import pygame
print('pygame init:', pygame.get_init())
try:
    import src.player as player
    print('left_idle_frames:', len(player.left_idle_frames))
    print('left_walk_frames:', len(player.left_walk_frames))
    print('available_backgrounds:', len(player.available_backgrounds))
    print('game_background type:', type(player.game_background))
except Exception as e:
    print('import error:', e)
