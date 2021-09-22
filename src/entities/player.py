from arcade import key

from .entity import Entity


class Player(Entity):

    def __init__(
            self, image_file: str, scale: float, center_x: float, center_y: float, screen_width: int,
            screen_height: int, movement_speed: float, jump_speed: float, flipped_horizontally: bool) -> None:
        """Initialize the Player.

        :param image_file: Path to the image file.
        :type image_file: str
        :param scale: Scale of the sprite.
        :type scale: float
        :param center_x: Player's x coordinate.
        :type center_x: float
        :param center_y: Player's y coordinate.
        :type center_y: float
        :param screen_width: Width on the screen.
        :type screen_width: int
        :param screen_height: Height of the screen
        :type screen_height: int
        :param movement_speed: Player's movement speed.
        :type movement_speed: float
        :param jump_speed: Player's jump speed.
        :type jump_speed: float
        :param flipped_horizontally: Should the player sprite be flipped.
        :type flipped_horizontally: bool
        """
        super().__init__(
            image_file, scale, center_x, center_y, flipped_horizontally)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.movement_speed = movement_speed
        self.jump_speed = jump_speed

    def update(self) -> None:
        self.check_bounds()

    def check_bounds(self) -> None:
        """Check if player is out of bounds."""
        if self.left < 0:
            self.left: int = 0
        elif self.right > self.screen_width - 1:
            self.right: int = self.screen_width - 1

        if self.bottom < 0:
            self.bottom: int = 0
        elif self.top > self.screen_height - 1:
            self.top: int = self.screen_height - 1

    def on_key_press(
            self, key_pressed: int, modifier: int,
            can_jump: bool) -> None:
        """Called whenever a key is pressed.

        :param key_pressed: Key that got pressed.
        :type key_pressed: int
        :param modifier: Modifiers pressed with the key.
        :type modifier: int
        :param can_jump: If the player on the ground.
        :type can_jump: bool
        """
        if key_pressed == key.UP:
            if can_jump:
                self.change_y = self.jump_speed
        elif key_pressed == key.LEFT:
            self.change_x = -self.movement_speed
        elif key_pressed == key.RIGHT:
            self.change_x = self.movement_speed

    def on_key_release(self, key_released: int, modifiers: int) -> None:
        """Called when the user releases a key.

        :param key_pressed: Key that was released.
        :type key_pressed: int
        :param modifiers: Mofidiers that were released with the key.
        :type modifiers: int
        """
        if key_released in (key.LEFT, key.RIGHT):
            self.change_x = 0
