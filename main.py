import pygame
import sys
from src.config import WIDTH, HEIGHT
from src.network import Network
from src.player import Player
from src.states import GameState
from src.ui import UIManager

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warrior Game")

def main():
    clock = pygame.time.Clock()
    net = Network()
    ui = UIManager()

    player1 = Player(300, HEIGHT - 450, side="left")
    player2 = Player(WIDTH - 550, HEIGHT - 450, side="right")

    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            result = ui.handle_event(event, mouse_pos, player1, player2, net)
            if result.get("quit"):
                running = False

        ui.update(player1, player2, net)

        if ui.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if ui.mp_role == "HOST":
                player1.update(keys, player2)
                data = net.send({
                    "x": player1.x,
                    "y": player1.y,
                    "state": player1.state,
                    "hp": player1.health,
                    "sh": player1.shield
                })
                if data:
                    player2.x = data.get("x", player2.x)
                    player2.y = data.get("y", player2.y)
                    player2.state = data.get("state", player2.state)
                    player2.health = data.get("hp", player2.health)
                    player2.shield = data.get("sh", player2.shield)
            elif ui.mp_role == "CLIENT":
                player2.update(keys, player1)
                data = net.send({
                    "x": player2.x,
                    "y": player2.y,
                    "state": player2.state,
                    "hp": player2.health,
                    "sh": player2.shield
                })
                if data:
                    player1.x = data.get("x", player1.x)
                    player1.y = data.get("y", player1.y)
                    player1.state = data.get("state", player1.state)
                    player1.health = data.get("hp", player1.health)
                    player1.shield = data.get("sh", player1.shield)
            else:
                player1.update(keys, player2)
                player2.update(keys, player1)

        ui.render(screen, mouse_pos, player1, player2, clock)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    