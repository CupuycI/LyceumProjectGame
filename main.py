import arcade

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
SCREEN_TITLE = "RUC\nResponding to an urgent call"

class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()


def setup_game(width, height, title):
    game = MainWindow(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()