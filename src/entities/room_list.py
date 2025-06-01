from ..utils import GameConfig
from .entity import Entity

class RoomList(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(
            config=config,
            image=config.images.room_list,
            x=(config.window.width - config.images.room_list.get_width()) // 2,
            y=int(config.window.height - config.images.room_list.get_height()) // 2 - 50,
        )