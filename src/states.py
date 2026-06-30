from enum import Enum, auto

class GameState(Enum):
    """Tracks the top-level screens and gameplay modes."""
    MAIN_MENU = auto()
    NAME_INPUT = auto()
    MULTIPLAYER_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    HOW_TO_PLAY = auto()
    OPTIONS = auto()
    BACKGROUND_MENU = auto()
    AVATAR_MENU = auto()
    GAME_OVER = auto()
