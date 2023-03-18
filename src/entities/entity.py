from arcade import Sprite


class Entity(Sprite):
    """Base class that all entities inherit from."""

    def __init__(
            self, image_file: str, scale: float,
            center_x: float, center_y: float, flipped_horizontally: bool) -> None:
        """Initialize the Entity

        :param image_file: Path to the image file.
        :type image_file: str
        :param scale: Scale of the sprite.
        :type scale: float
        :param center_x: Entity's x coordinate.
        :type center_x: float
        :param center_y: Entity's y coordinate.
        :type center_y: float
        :param flipped_horizontally: Should the entity sprite be flipped.
        :type flipped_horizontally: bool
        """
        super().__init__(
            image_file,
            scale=scale,
            center_x=center_x,
            center_y=center_y,
            flipped_horizontally=flipped_horizontally
        )
