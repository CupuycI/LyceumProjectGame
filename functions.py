import os
import sys
import arcade
import math


def get_path(file_name):
    directory = ""
    if file_name.endswith(".jpg") or file_name.endswith(".png"):
        directory = "pictures"
    elif file_name.endswith(".wav") or file_name.endswith(".mp3"):
        directory = "sounds"

    if directory:
        return os.path.join(os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), directory),
                            file_name)

    return os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))), file_name)


def get_my_rect(center_x, center_y, width, height):
    return arcade.Rect(*arcade.XYWH(center_x, center_y, width, height))


def change_status(wd, status, value=False):
    wd.status = status
    if status == "ChoosingSize" and value:
        wd.level = value
        if wd.game_size:
            wd.game_size = ""

    elif status == "MainMenu" and wd.level:
        wd.level = ""
        wd.keys.clear()

    elif status == "Game" and value:
        wd.game_size = value


def set_background(file_name, screen_width, screen_height):
    background = arcade.load_texture(get_path(file_name))
    arcade.draw_texture_rect(background, get_my_rect(screen_width / 2, screen_height / 2.5, screen_width,
                                                     screen_height))


def set_image(file_name, center_x, center_y):
    image = arcade.load_texture(get_path(file_name))
    arcade.draw_texture_rect(image, get_my_rect(center_x, center_y, image.width, image.height))


def get_speed(x, y, speed, t_x, t_y):
    d_x, d_y = t_x - x, t_y - y
    d = math.sqrt(d_x ** 2 + d_y ** 2)
    speed_x = speed / d * d_x
    speed_y = speed / d * d_y
    return speed_x, speed_y


def check_collisions(object, lst, speed, delta_time):
    for sprite in object.collides_with_list(lst):
        if sprite.center_x < object.center_x:
            object.center_x += speed * delta_time

        elif sprite.center_x > object.center_x:
            object.center_x -= speed * delta_time

        if sprite.center_y < object.center_y:
            object.center_y += speed * delta_time

        elif sprite.center_y > object.center_y:
            object.center_y -= speed * delta_time


def draw_possibility_interaction(object, lst, collected_evidence):
    for target in object.collides_with_list(lst):
        if target not in collected_evidence:
            set_image(get_path("Interaction.png"), target.center_x + object.width / 2, target.center_y + object.height / 2)
