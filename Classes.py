import json
import math
from math import atan2
from random import choice, randint

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
        self.sprite = arcade.Sprite(get_path("Detective.png"), 0.9, x, y)
        self.sprite.append_texture(arcade.load_texture(get_path("DetectiveWithGun.png")))
        self.sprite_2 = arcade.Sprite(get_path("DetectiveHitBoxImage.png"), 0.9, x, y)
        self.location = location
        self.collected_evidence = arcade.SpriteList()

    def draw(self):
        draw_possibility_interaction(self.sprite_2, self.location.evidence_sprites, self.collected_evidence)
        draw_possibility_interaction(self.sprite_2, self.location.exits, self.collected_evidence)
        draw_possibility_interaction(self.sprite_2, self.location.entries, self.collected_evidence)
        self.sprite_2.draw_hit_box((255, 0, 0))


    def update(self, keys: list, delta_time=False):
        if keys and delta_time:
            if arcade.key.KEY_1 in keys:
                self.item = self.items[0]
                self.sprite.set_texture(1)
                self.sprite.sync_hit_box_to_texture()

            elif arcade.key.KEY_4 in keys:
                self.item = self.items[3]
                self.sprite.set_texture(0)
                self.sprite.sync_hit_box_to_texture()

            if arcade.key.E in keys:
                for i in self.sprite_2.collides_with_list(self.location.evidence_sprites):
                    if i not in self.collected_evidence:
                        if "ClothPart" in str(i.texture.file_path):
                            i.remove_from_sprite_lists()
                        self.collected_evidence.append(i)

                for i in self.sprite_2.collides_with_list(self.location.entries):
                    if i not in self.collected_evidence:
                        i.append_texture(arcade.load_texture(get_path("OpenedEntry.png")))
                        print(i.textures)
                        i.set_texture(-1)
                        i.sync_hit_box_to_texture()
                        i.center_x -= i.width / 2.75
                        i.center_y += i.height * 3.25
                        self.collected_evidence.append(i)

                if self.sprite_2.collides_with_list(self.location.exits):
                    change_status(self.wd, "MainMenu")
                    return


            speed = self.speed / math.sqrt(2) if len(keys) > 1 else self.speed
            for key in keys:
                if key == arcade.key.W:
                    self.sprite.center_y += speed * delta_time

                elif key == arcade.key.S:
                    self.sprite.center_y -= speed * delta_time

                elif key == arcade.key.A:
                    self.sprite.center_x -= speed * delta_time

                elif key == arcade.key.D:
                    self.sprite.center_x += speed * delta_time

                for i in self.location.doors_sprites:
                    if self.sprite.collides_with_sprite(i):
                        i: arcade.Sprite
                        if len(i.textures) < 2:
                            i.append_texture(self.location.opened_door_texture)
                            i.set_texture(1)
                            i.sync_hit_box_to_texture()
                            i.center_x -= self.location.opened_door_texture.width * 3
                            i.center_y -= self.location.opened_door_texture.height / 2.75

                    elif abs(self.sprite.center_x - i.center_x) > 60:
                        if len(i.textures) >= 2:
                            i.set_texture(0)
                            i.sync_hit_box_to_texture()
                            i.textures = i.textures[:-1]
                            i.center_x += self.location.opened_door_texture.width * 3
                            i.center_y += self.location.opened_door_texture.height / 2.75

                check_collisions(self.sprite, self.location.spawns_objects, speed, delta_time)
                check_collisions(self.sprite, self.location.objects, speed, delta_time)
                check_collisions(self.sprite, self.location.interior, speed, delta_time)
                check_collisions(self.sprite, self.location.entries, speed, delta_time)

                self.sprite_2.center_x = self.sprite.center_x
                self.sprite_2.center_y = self.sprite.center_y


    def update_angle(self, x, y):
        t_x, t_y = get_speed(self.sprite.center_x, self.sprite.center_y, self.speed, x, y)
        angle = atan2(t_x, t_y)
        self.sprite.angle = math.degrees(angle)
        self.sprite_2.angle = self.sprite.angle



class Bullet:
    def __init__(self, x, y, speed, t_x, t_y):
        self.sprite = arcade.Sprite(get_path("Bullet.png"), (1, 1), x, y)
        self.speed_x, self.speed_y = get_speed(x, y, speed, t_x, t_y)

    def update(self, delta_time):
        self.sprite.center_x += self.speed_x * delta_time
        self.sprite.center_y += self.speed_y * delta_time


class Location:
    def __init__(self, wd, size):
        self.size = size
        self.wd = wd
        self.spawns_objects = arcade.SpriteList()
        self.exits = arcade.SpriteList()
        self.create_spawn()
        self.objects = arcade.SpriteList()
        self.entries = arcade.SpriteList()
        self.interior = arcade.SpriteList()
        self.floor = arcade.SpriteList()
        self.doors_sprites = arcade.SpriteList()
        self.create_location()
        self.bullets = []
        self.bullets_sprites = arcade.SpriteList()
        self.opened_door_texture = arcade.load_texture(get_path("OpenedDoor.png"))


    def create_spawn(self):
        police_car = arcade.Sprite(get_path("PoliceCar.png"), (1, 1), self.wd.width / 30, self.wd.height / 2)
        self.police_car = police_car
        self.exits.append(police_car)
        self.spawns_objects.append(police_car)
        self.spawn_floor = arcade.SpriteList()
        side_walk_texture = arcade.load_texture(get_path("sidewalk.png"))
        road_texture = arcade.load_texture(get_path("Road.png"))
        grass_texture = arcade.load_texture(get_path("Grass.png"))
        for i in range(self.wd.height // side_walk_texture.height + 2):
            for k in range(1, 4):
                sprite = arcade.Sprite(grass_texture, 1, police_car.center_x + police_car.width / 2.5 +
                                       side_walk_texture.width * k, side_walk_texture.height * i)
                self.spawn_floor.append(sprite)
            sprite = arcade.Sprite(road_texture, 1, police_car.center_x - police_car.width / 2.5, road_texture.height * i)
            self.spawn_floor.append(sprite)
            sprite = arcade.Sprite(side_walk_texture, 1, police_car.center_x + police_car.width / 2.5, side_walk_texture.height * i)
            self.spawn_floor.append(sprite)

    def create_location(self):
        self.locations = []
        self.evidence = []
        with (open(get_path("locations.json"), "r", encoding="utf8") as f,
              open(get_path("evidence.json"), "r", encoding="utf8") as f2):
            self.locations = json.load(f)
            self.evidence = json.load(f2)[self.size]
            self.evidence = self.evidence[choice([i for i in self.evidence.keys()])]

        height = self.wd.height / 1.5
        wd = arcade.Sprite(get_path("HWall.png"), (1, 1), 0, 0).width
        ht = arcade.Sprite(get_path("VWall.png"), (1, 1), 0, 0).height
        location = choice(self.locations[self.size])
        start_x = self.wd.width / 4
        width = start_x
        location2 = []
        for i in location[:-1]:
            if i == "hallway":
                location2.append("hallway")
                continue

            location2.append([choice(self.locations[size + "_rooms"]) for size in i])

        mx_wd = len(max([''.join([k[0].split('\n')[0] for k in i]) for i in location2 if i != "hallway"], key=len)) * 3 - 1
        for ind1, rooms in enumerate(location2):
            height -= ht
            if rooms == "hallway":
                hallway_height = height
                height -= ht * 3
                continue

            width = start_x
            height2 = []

            for ind, room in enumerate(rooms):
                cur_height = height
                if ind != 0:
                    width = start_x
                    for index in range(ind):
                        cur_room = rooms[index][0].replace("-", "   ").replace("W", "   ")
                        width += len(max(cur_room.split('\n'), key=len)[:-1] * 20)

                if True:
                    if "d" == location[ind1][0][0]:
                        try:
                            cur_height -= ((len(max(rooms, key=(lambda x: len(x[0].split('\n'))))[0].split('\n')) -
                                            len(room[0].split('\n'))) * 20)

                        except Exception as e:
                            print(e)
                            print(rooms)


                h, _ = self.load_room(room[0], width, cur_height, wd, ht)
                interior_name = location[ind1][ind]+ "_interior_" + room[1]
                self.load_interior(choice(self.locations[interior_name]), width, cur_height, wd, ht)
                height2.append(h)
                arcade.texture.default_texture_cache.flush()

            height = min(height2)
            width = start_x

        hallway = f"""|{' ' * mx_wd}|\nE{' ' * mx_wd}|\n{' ' * mx_wd}|\n{' ' * mx_wd}|\n"""
        self.load_room(hallway, width, hallway_height, wd, ht, True)
        self.load_evidence(self.evidence)
        sidewalk_texture = arcade.load_texture(get_path("sidewalk.png")).rotate_90()

        for i in range(int(start_x - (self.police_car.center_x + self.police_car.width / 2.5)) //
                       sidewalk_texture.width - 1):
            x = self.police_car.center_x + self.police_car.width + i * sidewalk_texture.width
            sprite = arcade.Sprite(sidewalk_texture, 1, x, hallway_height - sidewalk_texture.height / 2.5)
            self.spawn_floor.append(sprite)

        wall_texture = arcade.load_texture(get_path("VWall.png"))
        x = start_x - wall_texture.width
        for i in range(int(self.wd.height - hallway_height) // wall_texture.height + 1):
            sprite = arcade.Sprite(wall_texture, 1, x, hallway_height + wall_texture.height * i)
            self.objects.append(sprite)
            if i < 20:
                sprite = arcade.Sprite(wall_texture, 1, x, wall_texture.height * i)
                self.objects.append(sprite)

    def draw(self):
        self.spawn_floor.draw()
        self.spawns_objects.draw()
        self.floor.draw()
        self.interior.draw()
        self.entries.draw()
        self.objects.draw()
        self.evidence_sprites.draw()
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

    def load_evidence(self, evidence):
        self.evidence_sprites = arcade.SpriteList()
        if evidence["forced entry"]:
            entry = self.entries.sprite_list[0]
            entry: arcade.Sprite
            entry.append_texture(arcade.load_texture(get_path("ForcedDoor.png")))
            entry.set_texture(1)

        shoe_print_texture = arcade.load_texture(get_path("Footprints.png"))
        for i in range(randint(0, evidence["shoeprints"])):
            floor = choice(self.floor.sprite_list)
            while floor.collides_with_list(self.objects) or floor.collides_with_list(self.interior):
                floor = choice(self.floor.sprite_list)
            prints = arcade.Sprite(shoe_print_texture, 1, floor.center_x, floor.center_y, randint(0, 360))
            self.evidence_sprites.append(prints)

        hand_print_texture = arcade.load_texture(get_path("Handprint.png"))
        for i in range(randint(0, evidence["handprints"])):
            interior_obj = choice(self.interior.sprite_list)
            path = str(interior_obj.texture.file_path)
            while "Wardrobe" in path or "Sink" in path or "Bath" in path or "TV" in path:
                interior_obj = choice(self.interior.sprite_list)
                path = str(interior_obj.texture.file_path)
            prints = arcade.Sprite(hand_print_texture, 1, interior_obj.center_x, interior_obj.center_y,
                                   randint(0, 360))

            self.evidence_sprites.append(prints)

        cloth_part_texture = arcade.load_texture(get_path("ClothPart.png"))
        for i in range(randint(0, evidence["cloth part"])):
            obj = choice(choice([self.interior, self.floor]).sprite_list)
            while (obj in self.floor.sprite_list and (obj.collides_with_list(self.objects) or
                                                      obj.collides_with_list(self.interior)) or
                   obj in self.interior and "Stove" in str(obj.texture.file_path)):
                obj = choice(choice([self.interior, self.floor]).sprite_list)

            cloth_part = arcade.Sprite(cloth_part_texture, 1, obj.center_x, obj.center_y, randint(0, 360))

            self.evidence_sprites.append(cloth_part)

    def load_interior(self, interior: list, width: float, height: float, wd: float, ht: float):
        for i in interior:
            cur_wd = width + wd / 3 * i[0]
            cur_ht = height + ht * i[1]

            sprite = arcade.Sprite(get_path(i[2] + ".png"), (1, 1), cur_wd, cur_ht)
            self.interior.append(sprite)

    def load_room(self, room: str, width: float, height: float, wd: float, ht: float, is_hallway=False):
        original_width = width
        for ind, s in enumerate(room):
            if is_hallway and s not in ['\n', "|"]:
                if room.find('\n') > ind:
                    sprite = arcade.Sprite(get_path("VWall.png"), (1, 1), width, height + ht)
                    if not sprite.collides_with_list(self.objects):
                        self.objects.append(sprite)
                elif room[:-1].rfind('\n') < ind:
                    sprite = arcade.Sprite(get_path("VWall.png"), (1, 1), width, height - ht)
                    if not sprite.collides_with_list(self.objects):
                        self.objects.append(sprite)
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
                self.doors_sprites.append(sprite)

            elif s == "D":
                sprite = arcade.Sprite(get_path("HUDoor.png"), (1, 1), width, height)
                for n in range(-1, 2):
                    floor = arcade.Sprite(get_path("Floor.png"), (1, 1), width + (wd / 3) * n, height)
                    self.floor.append(floor)
                self.doors_sprites.append(sprite)

            elif s == "E":
                width -= wd / 3
                height -= ht
                for n in range(-2, 2):
                    floor = arcade.Sprite(get_path("Floor.png"), (1, 1), width, height + ht * n)
                    self.floor.append(floor)
                sprite = arcade.Sprite(get_path("LDoor.png"), (1, 1), width, height)
                height += ht
                width += sprite.width
                self.entries.append(sprite)
                continue

            else:
                sprite = arcade.Sprite(get_path("Floor.png"), (1, 1), width, height)
                width += sprite.width
                self.floor.append(sprite)
                continue

            width += wd
            self.objects.append(sprite)
        return height, width

