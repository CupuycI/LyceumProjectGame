from functions import  *


class MyButton:
    def __init__(self, wd, center_x, center_y, text, function, color, hovered_color, text_size):
        self.wd = wd
        self.center_x, self.center_y = center_x, center_y
        self.text = arcade.Text(text, center_x, self.center_y, arcade.color.WHITE,
                                text_size)
        self.function = function
        self.is_hovered = False
        self.color, self.hovered_color = color, hovered_color

    def draw(self):
        color = self.color if not self.is_hovered else self.hovered_color
        arcade.draw_rect_filled(self.text.rect, color)
        self.text.draw()

    def check_mouse_over(self, x, y):
        return (self.text.x < x < self.text.x + self.text.content_width and
                self.text.y - self.text.content_height / 4 < y < self.text.y + self.text.content_height)

    def on_hover_update(self, x, y):
        if not self.check_mouse_over(x, y):
            self.is_hovered = False
            return

        self.is_hovered = True

    def on_press(self):
        if self.is_hovered:
            self.function()
