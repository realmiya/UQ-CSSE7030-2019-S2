"""Class for representing a Player entity within the game."""

__version__ = "1.1.0"

from game.entity import DynamicEntity


class Player(DynamicEntity):
    """A player in the game"""
    _type = 3


    def __init__(self, name: str = "Mario", max_health: float = 20):
        """Construct a new instance of the player.

        Parameters:
            name (str): The player's name
            max_health (float): The player's maximum & starting health
        """
        super().__init__(max_health=max_health)
        self._invincible = False
        self._bigger=False

        self._name = name
        self._score = 0
        self_start = 0
        self._mushroom_1s=False
    def get_name(self) -> str:
        """(str): Returns the name of the player."""
        return self._name

    def get_score(self) -> int:
        """(int): Get the players current score."""
        return self._score

    def change_score(self, change: float = 1):
        """Increase the players score by the given change value."""
        self._score += change

    def set_invincible(self, TrueorFalse):
        """
        used to determin invincible
        :param TrueorFalse:bool

        """
        self._invincible=TrueorFalse

    def is_invincible(self):
        return self._invincible

    def set_bigger(self,TorF):
        """
        used to determine to be big mario
        :param TorF:bool

        """
        self._bigger=TorF

    def is_bigger(self):
        return self._bigger

    def set_mushroom_2s(self,plus):
        """
        used to dealy mushroom remove
        :param plus:bool

        """
        self._mushroom_2s=plus

    def is_2s(self):
        return self._mushroom_2s



    def __repr__(self):
        return f"Player({self._name!r})"

    def step(self, time_delta: float, game_data):
        pass

    def recall_bricks(self):
        pass
