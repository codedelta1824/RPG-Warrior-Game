import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
import sys
sys.path.append(r"d:\Ayyan's Data\Warrior Game")
from src.config import WIDTH, HEIGHT
from src.player import Player, game_background

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create players and draw one frame
p1 = Player(300, HEIGHT - 430, side="left")
p2 = Player(WIDTH - 550, HEIGHT - 430, side="right")

screen.blit(game_background, (0, 0))
# draw players
p1.draw(screen, opponent_x=p2.x)
p2.draw(screen, opponent_x=p1.x)

out_path = os.path.join('tests', 'frame.png')
pygame.image.save(screen, out_path)
print('Saved frame to', out_path)
pygame.quit()
