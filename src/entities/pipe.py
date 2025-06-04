import random
from typing import List

from ..utils import GameConfig
from .entity import Entity


class Pipe(Entity):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # speed of the pipe
        self.vel_x = -8

    def draw(self) -> None:
        self.x += self.vel_x
        super().draw()


class Pipes(Entity):
    upper: List[Pipe]
    lower: List[Pipe]

    def __init__(self, config: GameConfig) -> None:
        super().__init__(config)
        # the middle space between the upper and lower pipe
        self.mode = "solo"
        self.pipe_gap = 150
        self.top = 0
        self.bottom = self.config.window.viewport_height
        self.upper = []
        self.lower = []
        self.spawn_initial_pipes()

    def set_mode(self, mode: str):
        assert mode in ("solo", "multi")
        self.mode = mode

    def set_pipes(self, upper, lower):
        self.upper.append(upper)
        self.lower.append(lower)

    def reset(self):
        self.upper = []
        self.lower = []
        self.resume()

    def tick(self) -> None:
        if self.mode == "solo" and self.can_spawn_pipes():
            self.spawn_new_pipes()
        self.remove_old_pipes()

        for up_pipe, low_pipe in zip(self.upper, self.lower):
            up_pipe.tick()
            low_pipe.tick()

    def stop(self) -> None:
        for pipe in self.upper + self.lower:
            pipe.vel_x = 0

    def resume(self) -> None:
        for pipe in self.upper + self.lower:
            pipe.vel_x = -8

    def can_spawn_pipes(self) -> bool:
        if not self.upper:  # if the list is empty
            return True

        last = self.upper[-1]
        return self.config.window.width - (last.x + last.w) > last.w * 2.5

    def spawn_new_pipes(self):
        # add new pipe when first pipe is about to touch left of screen
        upper, lower = self.make_random_pipes()
        self.upper.append(upper)
        self.lower.append(lower)

    def multi_spawn_new_pipes(self, gap_y: int = None):
        """Spawns a new pipe. If gap_y is given, uses it for multiplayer consistency."""
        if gap_y is None:
            # Solo mode random pipe generation
            base_y = self.config.window.viewport_height
            gap_y = random.randint(
                int(base_y * 0.2),
                int(base_y * 0.6 - self.pipe_gap)
            )

        upper, lower = self.multi_make_random_pipes(gap_y)
        self.set_pipes(upper, lower)

    def remove_old_pipes(self):
        # remove first pipe if its out of the screen
        for pipe in self.upper:
            if pipe.x < -pipe.w:
                self.upper.remove(pipe)

        for pipe in self.lower:
            if pipe.x < -pipe.w:
                self.lower.remove(pipe)

    def spawn_initial_pipes(self):
        upper_1, lower_1 = self.make_random_pipes()
        upper_1.x = self.config.window.width + upper_1.w * 3
        lower_1.x = self.config.window.width + upper_1.w * 3
        self.upper.append(upper_1)
        self.lower.append(lower_1)

        upper_2, lower_2 = self.make_random_pipes()
        upper_2.x = upper_1.x + upper_1.w * 3.5
        lower_2.x = upper_1.x + upper_1.w * 3.5
        self.upper.append(upper_2)
        self.lower.append(lower_2)

    def make_random_pipes(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        base_y = self.config.window.viewport_height
        # gap_y is the y coordinate of the gap between upper and lower pipe
        gap_y = random.randrange(0, int(base_y * 0.6 - self.pipe_gap))
        gap_y += int(base_y * 0.2)
        pipe_height = self.config.images.pipe[0].get_height()
        pipe_x = self.config.window.width + 10

        upper_pipe = Pipe(
            self.config,
            self.config.images.pipe[0],
            pipe_x,
            gap_y - pipe_height,
        )

        lower_pipe = Pipe(
            self.config,
            self.config.images.pipe[1],
            pipe_x,
            gap_y + self.pipe_gap,
        )

        return upper_pipe, lower_pipe
    
    def multi_make_random_pipes(self, gap_y: int):
        pipe_height = self.config.images.pipe[0].get_height()
        pipe_x = self.config.window.width + 10

        upper_pipe = Pipe(
            self.config,
            self.config.images.pipe[0],
            pipe_x,
            gap_y - pipe_height,
        )
        lower_pipe = Pipe(
            self.config,
            self.config.images.pipe[1],
            pipe_x,
            gap_y + self.pipe_gap,
        )
        return upper_pipe, lower_pipe
