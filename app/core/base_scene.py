from abc import ABC, abstractmethod

class BaseScene(ABC):
    def __init__(self, matrix, state_manager):
        self.matrix = matrix
        self.state_manager = state_manager
        self.canvas = matrix.canvas
        self.width = matrix.width
        self.height = matrix.height

    @abstractmethod
    def draw(self, canvas):
        """
        Called every frame to render content.
        :param canvas: The current matrix canvas to draw on.
        """
        pass

    def update(self, dt):
        """
        Called every tick to update logic.
        :param dt: Delta time since last frame in seconds.
        """
        pass

    def enter(self, state_manager):
        """Called when the scene becomes active."""
        pass

    def exit(self):
        """Called when the scene is being replaced."""
        pass
