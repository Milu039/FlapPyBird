class GameMode:
    """
    Class to manage the game mode.
    """

    def __init__(self, mode):
        self.mode = mode

    def set_mode(self, mode):
        self.mode = mode
    
    def get_mode(self):
        return self.mode
        