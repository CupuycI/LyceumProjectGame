import json
import math
from random import choice

import arcade

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


class Detective:
    def __init__(self, wd: arcade.Window, x, y, location, hp=100, speed=100):
        self.wd = wd
        self.x = x
        self.y = y
        self.hp = hp
        self.speed = speed
        self.items = ["Pistol", "Flashlight", "Handcuffs", "Hands"]
        self.item = ""
        self.sprite = arcade.Sprite(get_path("Detective.png"), (1, 1), x, y)
        self.sprite.append_texture(arcade.load_texture(get_path("DetectiveWithGun.png")))
        self.rotate = "forward"
        self.location = location

    def draw(self):
        pass


    def update(self, keys: list, delta_time=False):
        if keys and delta_time:
            if arcade.key.KEY_1 in keys:
                self.item = self.items[0]
                self.sprite.set_texture(1)

            elif arcade.key.KEY_4 in keys:
                self.item = self.items[3]
                self.sprite.set_texture(0)

            speed = self.speed / math.sqrt(2) if len(keys) > 1 else self.speed
            for key in keys:
                if key == arcade.key.W:
                    self.sprite.center_y += speed * delta_time
                    if self.rotate == "right":
                        self.sprite.turn_left()

                    elif self.rotate == "left":
                        self.sprite.turn_right()

                    elif self.rotate == "down":
                        self.sprite.turn_right()
                        self.sprite.turn_right()

                    self.rotate = "forward"

                elif key == arcade.key.S:
                    self.sprite.center_y -= speed * delta_time
                    if self.rotate == "right":
                        self.sprite.turn_right()

                    elif self.rotate == "left":
                        self.sprite.turn_left()

                    elif self.rotate == "forward":
                        self.sprite.turn_left()
                        self.sprite.turn_left()

                    self.rotate = "down"

                elif key == arcade.key.A:
                    self.sprite.center_x -= speed * delta_time
                    if self.rotate == "forward":
                        self.sprite.turn_left()

                    elif self.rotate == "right":
                        self.sprite.turn_left()
                        self.sprite.turn_left()

                    elif self.rotate == "down":
                        self.sprite.turn_right()

                    self.rotate = "left"

                elif key == arcade.key.D:
                    self.sprite.center_x += speed * delta_time
                    if self.rotate == "forward":
                        self.sprite.turn_right()

                    elif self.rotate == "left":
                        self.sprite.turn_right()
                        self.sprite.turn_right()

                    elif self.rotate == "down":
                        self.sprite.turn_left()

                    self.rotate = "right"

                for sprite in self.sprite.collides_with_list(self.location.spawns_objects):
                    if sprite.center_x < self.sprite.center_x:
                        self.sprite.center_x += speed * delta_time

                    elif sprite.center_x > self.sprite.center_x:
                        self.sprite.center_x -= speed * delta_time

                    if sprite.center_y < self.sprite.center_y:
                        self.sprite.center_y += speed * delta_time

                    elif sprite.center_y > self.sprite.center_y:
                        self.sprite.center_y -= speed * delta_time


class Bullet:
    def __init__(self, x, y, speed, t_x, t_y):
        self.sprite = arcade.Sprite(get_path("Bullet.png"), (1, 1), x, y)
        d_x, d_y = t_x - x, t_y - y
        d = math.sqrt(d_x ** 2 + d_y ** 2)
        self.speed_x = speed / d * d_x
        self.speed_y = speed / d * d_y

    def update(self, delta_time):
        self.sprite.center_x += self.speed_x * delta_time
        self.sprite.center_y += self.speed_y * delta_time


class Location:
    def __init__(self, wd, size):
        self.size = size
        self.wd = wd
        self.spawns_objects = arcade.SpriteList()
        self.create_spawn()
        self.objects = arcade.SpriteList()
        self.floor = arcade.SpriteList()
        self.create_location()
        self.bullets = []
        self.bullets_sprites = arcade.SpriteList()

    def create_spawn(self):
        police_car = arcade.Sprite(get_path("PoliceCar.png"), (1, 1), self.wd.width / 30, self.wd.height / 2)
        self.spawns_objects.append(police_car)

    def create_location(self):
        self.locations = []
        with open(get_path("locations.json"), "r", encoding="utf8") as f:
            self.locations = json.load(f)

        height = self.wd.height / 2
        wd = arcade.Sprite(get_path("HWall.png"), (1, 1), 0, 0).width
        ht = arcade.Sprite(get_path("VWall.png"), (1, 1), 0, 0).height
        location = choice(self.locations[self.size])
        mx_wd = 0
        width = self.wd.width / 2
        location2 = []
        for i in location[:-1]:
            if i == "hallway":
                location2.append("hallway")
                continue

            location2.append([choice(self.locations[size + "_rooms"]) for size in i])

        mx_wd = len(max([''.join([k.split('\n')[0] for k in i]) for i in location2 if i != "hallway"], key=len)) * 3 - 1
        for ind1, rooms in enumerate(location2):
            # if i == "hallway":
            #     height -= ht
            #     width = self.wd.width / 2
            #     if i == "hallway":
            #         hallway_height = height
            #         height -= ht * 3
            #     continue
            height -= ht
            if rooms == "hallway":
                hallway_height = height
                height -= ht * 3
                continue

            width = self.wd.width / 2

            #rooms = [choice(self.locations[size + "_rooms"]) for size in i]
            height2 = []
            cur_wd = len(''.join([k.split('\n')[0] for k in rooms])) * 3 - 1
            if cur_wd < mx_wd:
                rooms.append(f'{"-" * ((mx_wd - cur_wd) // 3)}')

            for ind, room in enumerate(rooms):
                cur_height = height
                if ind != 0:
                    width = self.wd.width / 2
                    for index in range(ind):
                        width += len(rooms[index].split('\n')[0] * 60)
                    #width = len(rooms[ind - 1].split('\n')[0]) * 60 + self.wd.width / 2
                    # if len(room.split('\n')) > 1:
                    #     if "d" == location[ind1][ind][0]:
                    #         height -= ((len(max(rooms, key=(lambda x: len(x.split('\n')[0]))).split('\n')) -
                    #                     len(room.split('\n'))) * 20)

                    if "d" == location[ind1][0][0]:
                        cur_height -= ((len(max(rooms, key=(lambda x: len(x.split('\n')[0]))).split('\n')) -
                                        len(room.split('\n'))) * 20)

                h, _ = self.load_room(room, width, cur_height, wd, ht)
                height2.append(h)

            height = min(height2)
            width = self.wd.width / 2

        hallway = f"""|{' ' * mx_wd}|\nE{' ' * mx_wd}|\n{' ' * mx_wd}|\n|{' ' * mx_wd}|\n"""
        self.load_room(hallway, width, hallway_height, wd, ht)

    def draw(self):
        self.spawns_objects.draw()
        self.floor.draw()
        self.objects.draw()
        # for i in self.objects:
        #     i.draw_hit_box((255, 0, 0))
        self.bullets_sprites.draw()

    def update(self, delta_time):
        del_indexes = []
        for i in range(len(self.bullets)):
            bullet = self.bullets[i]
            bullet.update(delta_time)
            if bullet.sprite.collides_with_list(self.spawns_objects) or bullet.sprite.collides_with_list(self.objects):
                del_indexes.append(i)
                self.bullets_sprites.remove(bullet.sprite)

        for ind in del_indexes:
            del self.bullets[ind]

    def load_room(self, room, width, height, wd, ht):
        original_width = width
        for s in room:
            if s == "\n":
                width = original_width
                height -= ht
                continue

            if s == "-":
                sprite = arcade.Sprite(get_path("HWall.png"), (1, 1), width, height)

            elif s == "|":
                width -= wd / 3
                sprite = arcade.Sprite(get_path("VWall.png"), (1, 1), width, height)
                width += sprite.width
                self.objects.append(sprite)
                continue

            elif s == "W":
                sprite = arcade.Sprite(get_path("Window.png"), (1, 1), width, height)

            elif s == "d":
                sprite = arcade.Sprite(get_path("HDDoor.png"), (1, 1), width, height)
                for n in range(-1, 2):
                    floor = arcade.Sprite(get_path("Floor.png"), (1, 1), width + (wd / 3) * n, height)
                    self.floor.append(floor)

            elif s == "E":
                width -= wd / 3
                height -= ht
                for n in range(-2, 2):
                    floor = arcade.Sprite(get_path("Floor.png"), (1, 1), width, height + ht * n)
                    self.floor.append(floor)
                sprite = arcade.Sprite(get_path("LDoor.png"), (1, 1), width, height)
                height += ht
                width += sprite.width
                self.objects.append(sprite)
                continue

            else:
                sprite = arcade.Sprite(get_path("Floor.png"), (1, 1), width, height)
                width += sprite.width
                self.floor.append(sprite)
                continue

            width += wd
            self.objects.append(sprite)
        return height, width

