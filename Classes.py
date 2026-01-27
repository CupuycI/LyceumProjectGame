import json
import math
from itertools import product
from math import atan2
from random import choice, randint, random

import arcade
from arcade.future.light import Light, LightLayer

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


class Criminal(arcade.Sprite):
    def __init__(self, wd, x: float, y: float, location, hp=100, speed=90):
        super().__init__(get_path("Criminal.png"), 0.9, x, y)
        level = wd.level
        self.wd = wd
        self.location = location
        self.hp = hp
        self.speed = speed
        self.speed_x = 0
        self.speed_y = 0
        self.last_speed_x = 0
        self.last_speed_y = 0
        self.last_target = ""
        self.status = ""
        self.append_texture(arcade.load_texture(get_path("Criminal_with_knife.png")))
        self.append_texture(arcade.load_texture(get_path("Criminal0.png")))
        with open("criminals.json", "r", encoding="utf8") as f:
            self.type = json.load(f)[level]

        self.MAX_ATTACK_COOLDOWN = 60
        self.MIN_ATTACK_COOLDOWN = 15
        self.MAX_ATTACK_DURATION = 30
        self.MIN_ATTACK_DURATION = 10
        self.attack_cooldown_timer = 0
        self.attack_timer = 0
        self.HIT_COOLDOWN = 1.5
        self.hit_timer = 0
        self.MAX_HIDE_COOLDOWN = 30
        self.MIN_HIDE_COOLDOWN = 10
        self.MAX_HIDE_DURATION = 40
        self.MIN_HIDE_DURATION = 5
        self.hide_cooldown_timer = 0
        self.hide_timer = 0
        self.animation_textures = []
        for i in range(2):
            self.animation_textures.append(arcade.load_texture(get_path(f'Criminal{i}.png')))

        self.ANIMATION_COOLDOWN = 0.5
        self.animation_timer = 0

    def hide(self):
        self.set_texture(0)
        target = min(self.location.hiding_poses, key=(lambda i: get_distance(self.center_x, self.center_y, i[0], i[1])))
        self.main_x = target[0]
        self.main_y = target[1]
        cur_room = self.location.get_current_room(self)
        target_room = self.location.get_current_room(arcade.Sprite(get_path("Bullet.png"), 1,
                                                                                 target[0], target[1]))
        if cur_room and cur_room != target_room:
            try:
                door = cur_room[1].sprite_list[0]
                target = min(self.location.doors_points,
                             key=(lambda i: get_distance(i[0], i[1], door.center_x, door.center_y)))
                self.main_x = target[0]
                self.main_y = target[1]

            except Exception as e:
                pass

        elif not cur_room and target_room:
            try:
                door = target_room[1].sprite_list[0]
                target = min(self.location.doors_points, key=(lambda i: get_distance(i[0], i[1], door.center_x, door.center_y)))
                self.main_x = target[0]
                self.main_y = target[1]

            except Exception as e:
                pass

    def escape(self):
        self.set_texture(0)
        self.main_x = -20
        self.main_y = -20

    def attack(self):
        self.set_texture(1)
        cur_room = self.location.get_current_room(self)
        if cur_room and cur_room != self.location.get_current_room(self.wd.player):
            door = cur_room[1].sprite_list[0]
            target = min(self.location.doors_points, key=(lambda i: get_distance(i[0], i[1], door.center_x, door.center_y)))
            self.main_x = target[0]
            self.main_y = target[1]
            return
        self.main_x = self.wd.player.center_x
        self.main_y = self.wd.player.center_y

    def surrender(self):
        self.main_x, self.main_y = self.location.police_car.center_x, self.location.police_car.center_y
        self.set_texture(2)

    def update(self, delta_time: float = 1 / 60, *args, **kwargs) -> None:
        if self.hp <= 0:
            if self.cur_texture_index < len(self.animation_textures):
                if self.animation_timer >= self.ANIMATION_COOLDOWN:
                    self.animation_timer = 0
                    self.texture = self.animation_textures[self.cur_texture_index + 1]
                else:
                    self.animation_timer += delta_time
            return

        elif self.hp <= 20 or self.type["Fear"] > 0.8 and self.type["Cool-headedness"] < 0.5:
            self.surrender()
            return
        self.update_targets()
        self.update_timers()
        if self.collides_with_sprite(self.wd.player) and self.texture == self.textures[1]:
            if self.hit_timer >= self.HIT_COOLDOWN:
                self.hit_timer = 0
                self.wd.player.hp = max(self.wd.player.hp - 20, 0)
            else:
                self.hit_timer += delta_time

        nearest_points = sorted(self.location.points, key=(lambda i: get_distance(i[0], i[1], self.center_x, self.center_y)))[:2]
        self.cur_target = min(nearest_points, key=(lambda i: get_distance(i[0], i[1], self.main_x, self.main_y)))
        if (get_distance(self.center_x, self.center_y, self.main_x, self.main_y) <=
                get_distance(*self.cur_target[:2], self.main_x, self.main_y)):
            self.cur_target = [self.main_x, self.main_y, "t"]
        self.t_x = self.cur_target[0]
        self.t_y = self.cur_target[1]

        self.change_x, self.change_y = get_speed(self.center_x, self.center_y, self.speed, self.t_x, self.t_y)
        self.center_x += self.change_x * delta_time
        self.center_y += self.change_y * delta_time

        check_doors(self, self.location)
        if self.check_collisions(self):
            self.move_if_collides(delta_time)
        check_collisions(self, self.location.objects, abs(self.change_x), delta_time)
        check_collisions(self, self.location.interior, abs(self.change_y), delta_time)
        self.update_angle()

    def update_timers(self):
        if self.status == "hiding":
            self.hide_timer += 1

        else:
            self.hide_cooldown_timer += 1
            self.hide_timer = 0

        if self.status == "attacking":
            self.attack_timer += 1

        else:
            self.attack_cooldown_timer += 1
            self.attack_timer = 0

    def update_targets(self):
        if self.type["Fear"] >= 1.0:
            self.escape()
            self.status = "escaping"

        elif (self.type["Fear"] < self.type["Rage"] > random() and self.attack_cooldown_timer >= self.MIN_ATTACK_COOLDOWN or
              self.attack_cooldown_timer >= self.MAX_ATTACK_COOLDOWN):
            self.attack()
            self.status = "attacking"

        else:
            self.hide()
            self.status = "hiding"
            self.hide_cooldown_timer = 0

    def draw(self):
        try:
            arcade.draw_circle_filled(self.t_x, self.t_y, 5, (0, 0, 255))
            arcade.draw_circle_filled(self.main_x, self.main_y, 5, (0, 255, 0))

        except Exception as e:
            print(e)

    def move_if_collides(self, delta_time: float = 1/60):
        tmp = Criminal(self.wd, self.center_x, self.center_y, self.location)
        k = randint(1, 12)
        tmp_x = self.change_x * delta_time * k
        tmp_y = self.change_y * delta_time * k
        for i in product([self.center_x - tmp_x, self.center_x, self.center_x + tmp_x],
                         [self.center_y - tmp_y, self.center_y, self.center_y + tmp_y]):
            tmp.center_x = i[0]
            tmp.center_y = i[1]
            if not self.check_collisions(tmp):
                self.center_x = tmp.center_x
                self.center_y = tmp.center_y
                return

    def check_collisions(self, obj):
        return obj.collides_with_list(self.location.objects) or obj.collides_with_list(self.location.interior)

    def update_angle(self):
        t_x, t_y = get_speed(self.center_x, self.center_y, self.speed, self.t_x, self.t_y)
        angle = atan2(t_x, t_y)
        self.angle = math.degrees(angle)


class Detective(arcade.Sprite):
    def __init__(self, wd: arcade.Window, x, y, location, hp=100, speed=100):
        super().__init__()
        self.wd = wd
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.items = ["Pistol", "UVFlashlight", "Handcuffs", "Hands"]
        self.item = "Hands"
        self.scale = 0.9
        self.center_x = x
        self.center_y = y
        self.append_texture(arcade.load_texture(get_path("Detective.png")))
        self.set_texture(0)
        self.append_texture(arcade.load_texture(get_path("DetectiveWithGun.png")))
        self.sprite_2 = arcade.Sprite(get_path("DetectiveHitBoxImage.png"), 0.9, x, y)
        self.location = location
        self.collected_evidence = arcade.SpriteList()
        self.newly_collected_evidence = []
        self.checked_interior = arcade.SpriteList()
        self.is_dead = False
        self.DIE_ANIMATION_SPEED = 0.5
        self.die_animation_timer = 0
        self.die_animation_textures = [arcade.load_texture(get_path(f"Detective{i}.png")) for i in range(2)]
        self.die_texture_ind = -1
        self.DIE_COOLDOWN = 1
        self.die_timer = 0

    def draw(self):
        draw_possibility_interaction(self)
        x = self.wd.width - self.max_hp - 60 if self.center_x <= self.wd.width / 2 else self.wd.width - self.max_hp - 60 + (self.center_x - self.wd.width / 2)
        arcade.draw_lbwh_rectangle_outline(x, 10, self.max_hp + 5, 50,
                                           arcade.color.GRAY_BLUE)
        hp_color = arcade.color.GREEN if self.hp >= self.max_hp / 4 * 3 else (
            arcade.color.YELLOW) if self.hp >= self.max_hp / 2 else arcade.color.RED
        arcade.draw_lbwh_rectangle_filled(x + 2, 13, self.hp, 45, hp_color)
        x = 60 if self.center_x <= self.wd.width / 2 else self.center_x - self.wd.width / 2 + 60
        for i in range(1, 5):
            bottom = 40
            item_text = arcade.Text(self.items[i - 1], 0, bottom + 15, anchor_x="center", anchor_y="center")

            item_text.x = x + item_text.content_width / 2 + 5
            if self.item == item_text.text:
                arcade.draw_lbwh_rectangle_filled(x, bottom, item_text.content_width + 10, 30,
                                                  arcade.color.GRAY_BLUE)
            arcade.draw_lbwh_rectangle_outline(x, bottom, item_text.content_width + 10, 30, arcade.color.GRAY_BLUE)
            text = arcade.Text(str(i), item_text.x, bottom - 10, anchor_x="center", anchor_y="center")
            item_text.draw()
            text.draw()

            x += item_text.content_width + 20

        for ind, i in enumerate(self.newly_collected_evidence):
            if i[0] >= 0.5:
                del self.newly_collected_evidence[ind]

            else:
                evidence_text = arcade.Text(i[-1], i[1], i[2])
                evidence_text.draw()

    def update(self, keys: list, delta_time=1/60):
        for i in self.newly_collected_evidence:
            i[0] += delta_time
        if self.hp <= 0 and not self.is_dead:
            if self.texture == self.die_animation_textures[-1]:
                self.is_dead = True
                return

            if self.die_animation_timer >= self.DIE_ANIMATION_SPEED:
                self.die_animation_timer = 0
                self.die_texture_ind += 1
                self.texture = self.die_animation_textures[self.die_texture_ind]

            else:
                self.die_animation_timer += delta_time
            return

        if self.is_dead:
            if self.die_timer >= self.DIE_COOLDOWN:
                change_status(self.wd, "GameEnd")
            else:
                self.die_timer += delta_time
            return
        if keys:
            if arcade.key.KEY_1 in keys:
                self.item = self.items[0]
                self.set_texture(1)
                self.sync_hit_box_to_texture()

            elif arcade.key.KEY_2 in keys:
                self.item = self.items[1]
                self.set_texture(0)
                self.sync_hit_box_to_texture()

            elif arcade.key.KEY_3 in keys:
                self.item = self.items[2]
                self.set_texture(0)
                self.sync_hit_box_to_texture()

            elif arcade.key.KEY_4 in keys:
                self.item = self.items[3]
                self.set_texture(0)
                self.sync_hit_box_to_texture()

            if arcade.key.E in keys:
                for i in self.sprite_2.collides_with_list(self.location.evidence_sprites):
                    if i not in self.collected_evidence:
                        name = get_evidence_name(i)
                        if "clothpart" in name:
                            i.remove_from_sprite_lists()
                        self.collected_evidence.append(i)
                        self.newly_collected_evidence.append([0, i.center_x, i.center_y, name])

                if self.item == self.items[1]:
                    for i in self.sprite_2.collides_with_list(self.location.handprints):
                        if i not in self.collected_evidence:
                            self.collected_evidence.append(i)
                            self.newly_collected_evidence.append([0, i.center_x, i.center_y, get_evidence_name(i)])

                for i in self.sprite_2.collides_with_list(self.location.interior):
                    if i not in self.checked_interior:
                        self.checked_interior.append(i)

                for i in self.sprite_2.collides_with_list(self.location.entries):
                    if i not in self.collected_evidence:
                        i.append_texture(arcade.load_texture(get_path("OpenedEntry.png")))
                        i.set_texture(-1)
                        i.sync_hit_box_to_texture()
                        i.center_x -= i.width / 2.75
                        i.center_y += i.height * 3.25
                        self.collected_evidence.append(i)

                if self.sprite_2.collides_with_list(self.location.exits):
                    change_status(self.wd, "GameEnd")
                    return

            speed = self.speed / math.sqrt(2) if len(keys) > 1 else self.speed
            for key in keys:
                if key == arcade.key.W:
                    self.center_y += speed * delta_time

                elif key == arcade.key.S:
                    self.center_y -= speed * delta_time

                elif key == arcade.key.A:
                    self.center_x -= speed * delta_time

                elif key == arcade.key.D:
                    self.center_x += speed * delta_time
                check_doors(self, self.location)

                print("#")
                check_collisions(self, self.location.spawns_objects, speed, delta_time)
                check_collisions(self, self.location.objects, speed, delta_time)
                check_collisions(self, self.location.interior, speed, delta_time)
                check_collisions(self, self.location.entries, speed, delta_time)

                print(True)
                self.sprite_2.center_x = self.center_x
                self.sprite_2.center_y = self.center_y


    def update_angle(self, x, y):
        if self.hp <= 0:
            return
        t_x, t_y = get_speed(self.center_x, self.center_y, self.speed, x, y)
        angle = atan2(t_x, t_y)
        self.angle = math.degrees(angle)
        self.sprite_2.angle = self.angle


class Bullet(arcade.Sprite):
    def __init__(self, x, y, speed, t_x, t_y):
        super().__init__(get_path("Bullet.png"), (1, 1), x, y)
        self.speed_x, self.speed_y = get_speed(x, y, speed, t_x, t_y)

    def update(self, delta_time):
        self.center_x += self.speed_x * delta_time
        self.center_y += self.speed_y * delta_time


class Location:
    def __init__(self, wd):
        self.size = wd.game_size
        self.wd = wd
        self.spawns_objects = arcade.SpriteList()
        self.exits = arcade.SpriteList()
        self.create_spawn()
        self.objects = arcade.SpriteList()
        self.entries = arcade.SpriteList()
        self.interior = arcade.SpriteList()
        self.floor = arcade.SpriteList()
        self.doors_sprites = arcade.SpriteList()
        self.criminal_list = arcade.SpriteList()
        self.create_location()
        self.bullets = []
        self.bullets_sprites = arcade.SpriteList()
        self.opened_door_texture = arcade.load_texture(get_path("OpenedDoor.png"))
        self.opened_door_texture_2 = arcade.load_texture(get_path("OpenedDoor2.png"))
        self.time = 0
        self.criminal_is_spawned = False
        self.particles = []
        # self.light_layer = LightLayer(self.wd.width, self.wd.height)
        # self.light_layer.set_background_color(arcade.color.BLACK)
        # self.light_mode = "soft"
        # self.player_light = Light(self.wd.player.center_x, self.wd.player.center_y, self.wd.player.width,
        #                           arcade.color.WHITE, self.light_mode)
        #
        # self.light_layer.add(self.player_light)
        self.light_mode = "soft"

    def get_current_room(self, sprite):
        cur_room = [i for i in self.rooms if sprite.collides_with_list(i[0])]
        return cur_room if not cur_room else cur_room[0]

    def spawn_criminal(self):
        self.criminal_is_spawned = True
        room = choice([i for i in self.rooms if not self.wd.player.collides_with_list(i[0])])
        spawn_place = choice(room[0])
        self.criminal = Criminal(self.wd, spawn_place.center_x, spawn_place.center_y, self)
        while self.criminal.collides_with_list(self.interior) or self.criminal.collides_with_list(self.objects):
            spawn_place = choice(room[0])
            self.criminal.center_x = spawn_place.center_x
            self.criminal.center_y = spawn_place.center_y

        self.criminal_list.append(self.criminal)

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
        self.rooms = []
        self.points = []
        self.hiding_poses = []
        self.doors_points = []
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
                            pass


                h = self.load_room(room[0], width, cur_height, wd, ht, self.rooms)
                interior_name = location[ind1][ind]+ "_interior_" + room[1]
                self.load_interior(choice(self.locations[interior_name]), width, cur_height, wd, ht)
                height2.append(h)
                arcade.texture.default_texture_cache.flush()

            height = min(height2)
            width = start_x

        hallway = f"""|{' ' * mx_wd}|\nE{' ' * mx_wd}|\n{' ' * mx_wd}|\n{' ' * mx_wd}|\n"""
        self.load_room(hallway, width, hallway_height, wd, ht, self.rooms, True)
        hallway_points = []
        for i in range(len(hallway.split('\n')[0]) // 2 - 1):
            hallway_points.append([i * 2, -1.5, "P"])

        self.load_interior(hallway_points, width, hallway_height, wd, ht)
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

    def cast_ray_to_wall(self, start_x, start_y, angle, step=2, distance=160):
        max_steps = int(distance / step)
        cos_ = math.cos(angle)
        sin_ = math.sin(angle)
        for i in range(max_steps):
            cur_distance = i * step
            test_x = start_x + cur_distance * cos_
            test_y = start_y + cur_distance * sin_
            if test_x <= 0 or test_x >= self.wd.width or test_y <= 0 or test_y >= self.wd.height:
                return test_x, test_y

            hit_list = arcade.check_for_collision_with_list(arcade.SpriteSolidColor(1, 1, test_x, test_y),
                                                            self.objects)

            if hit_list:
                return test_x, test_y

        end_x = start_x + distance * cos_
        end_y = start_y + distance * sin_
        return end_x, end_y

    def create_lights(self, fragments_num=2):
        # arcade.draw_circle_filled(self.wd.player.center_x, self.wd.player.center_y,
        #                           max(self.wd.player.height, self.wd.player.width) / 2 + 10,
        #                           (255, 255, 255, 60))
        self.light_layer = LightLayer(self.wd.width, self.wd.height)

        detective = self.wd.player
        self.light_layer.add(Light(detective.center_x, detective.center_y, detective.width, mode=self.light_mode))
        half_light_angle = 0.5
        new_pi = math.pi / 2 * 1.12
        self.left_angle = -math.radians(detective.angle) - half_light_angle + new_pi
        self.right_angle = -math.radians(detective.angle) + half_light_angle + new_pi
        self.left_hit_x, self.left_hit_y = self.cast_ray_to_wall(detective.center_x,
                                                                  detective.center_y,
                                                                  self.left_angle)
        self.right_hit_x, self.right_hit_y = self.cast_ray_to_wall(detective.center_x,
                                                                         detective.center_y,
                                                                         self.right_angle)
        self.points2 = [(detective.center_x, detective.center_y)]#, (self.left_hit_x, self.left_hit_y)]
        for i in range(1, fragments_num):
            angle = self.left_angle + (self.right_angle - self.left_angle) * i / fragments_num
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=90)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=50)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=70)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=30)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=110)
            self.points2.append((hit_x, hit_y))
            hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=130)
            self.points2.append((hit_x, hit_y))
            # hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=150)
            # self.points2.append((hit_x, hit_y))
            # hit_x, hit_y = self.cast_ray_to_wall(detective.center_x, detective.center_y, angle, distance=170)
            # self.points2.append((hit_x, hit_y))

        #self.points2.append((self.right_hit_x, self.right_hit_y))

        color = (157, 0, 214, 120) if self.wd.player.item == self.wd.player.items[1] else (255, 255, 255, 120)
        #arcade.draw_polygon_filled(sorted(self.points2), color)
        for i in self.points2:
            self.light_layer.add(Light(i[0], i[1], 40, color, mode=self.light_mode))

        # self.light_layer.add(Light(self.police_car.center_x + 80, self.police_car.center_y, 80,
        #                            arcade.color.DARK_BLUE))
        # self.light_layer.add(Light(self.police_car.center_x - 80, self.police_car.center_y, 80,
        #                            arcade.color.DARK_RED))
        # self.light_layer.add(Light(self.police_car.center_x + 80, self.police_car.center_y - 30, 80,
        #                            arcade.color.DARK_BLUE))
        self.light_layer.add(Light(self.police_car.center_x, self.police_car.center_y, 150,
                                   arcade.color.DARK_BLUE))

    def is_object_in_light(self, sprite):
        detective = self.wd.player
        half_w = sprite.width / 2
        half_h = sprite.height / 2
        corners = [(sprite.center_x - half_w, sprite.center_y - half_h),
                   (sprite.center_x + half_w, sprite.center_y - half_h),
                   (sprite.center_x - half_w, sprite.center_y + half_h),
                   (sprite.center_x + half_w, sprite.center_y + half_h),
                   (sprite.center_x, sprite.center_y)]

        for cx, cy in corners:
            dist = get_distance(detective.center_x, detective.center_y, cx, cy)
            if dist <= 200:
                if dist == 0:
                    return True

                try:
                    v0 = [self.points2[1][0] - detective.center_x, self.points2[1][1] - detective.center_y]
                    v1 = [self.points2[2][0] - detective.center_x, self.points2[2][1] - detective.center_y]
                    v2 = [cx - detective.center_x, cy - detective.center_y]

                    dot00 = v0[0] * v0[0] + v0[1] * v0[1]
                    dot01 = v0[0] * v1[0] + v0[1] * v1[1]
                    dot02 = v0[0] * v2[0] + v0[1] * v2[1]
                    dot11 = v1[0] * v1[0] + v1[1] * v1[1]
                    dot12 = v1[0] * v2[0] + v1[1] * v2[1]

                    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
                    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
                    v = (dot00 * dot12 - dot01 * dot02) * inv_denom

                    if (u >= 0) and (v >= 0) and (u + v <= 1):
                        return True

                except ZeroDivisionError:
                    pass
        return False

    def get_objects_in_light(self):
        objects = arcade.SpriteList()
        for sprite in self.evidence_sprites:
            if self.is_object_in_light(sprite):
                objects.append(sprite)
        if self.criminal_is_spawned and self.is_object_in_light(self.criminal):
            objects.append(self.criminal)
        if self.wd.player.item == self.wd.player.items[1]:
            for sprite in self.handprints:
                if self.is_object_in_light(sprite):
                    objects.append(sprite)
        return objects

    def draw(self):
        # self.light_layer = LightLayer(self.wd.width, self.wd.height)
        # self.light_layer.set_background_color(arcade.color.BLACK)
        # self.light_mode = "soft"
        # self.player_light = Light(self.wd.player.center_x, self.wd.player.center_y, self.wd.player.width,
        #                           arcade.color.WHITE, self.light_mode)
        #
        # self.light_layer.add(self.player_light)
        self.create_lights()
        with self.light_layer:
            self.spawn_floor.draw()
            self.spawns_objects.draw()
            self.floor.draw()
            self.interior.draw()
            self.entries.draw()
            self.objects.draw()

            self.evidence_sprites.draw()
            if self.wd.player.item == self.wd.player.items[1]: # UVFlashlight
                self.handprints.draw()
            # self.get_objects_in_light().draw()
            self.bullets_sprites.draw()
            self.doors_sprites.draw_hit_boxes((255, 0, 0))
            # self.draw_flashlight()

            for point in self.points:
                arcade.draw_circle_filled(*point[:-1], radius=5, color=(255, 0, 0))

            for point in self.doors_points:
                arcade.draw_circle_filled(*point[:-1], radius=5, color=(255, 0, 0))

            self.criminal_list.draw()

        self.light_layer.draw(ambient_color=(10, 10, 10))
        if self.criminal_is_spawned:
            self.criminal.draw_hit_box(color=(192, 255, 0))

        self.evidence_sprites.draw_hit_boxes((192, 255, 0))
        # if self.criminal_is_spawned and self.is_object_in_light(self.criminal):
        #     print("##$", True)
        #     self.criminal.draw()

        for i in self.particles:
            i.draw()


    def update(self, delta_time):
        for bullet in self.bullets_sprites:
            for _ in range(4):
                bullet.update(delta_time)
                if bullet.collides_with_list(self.spawns_objects) or bullet.collides_with_list(self.objects):
                    try:
                        bullet.remove_from_sprite_lists()
                        self.particles.append(make_wall_particles(bullet.center_x, bullet.center_y))
                        break

                    except ValueError:
                        pass

                if self.criminal_is_spawned and bullet.collides_with_sprite(self.criminal):
                    self.criminal.hp -= 20
                    if self.criminal.type["Cool-headedness"] < 0.6:
                        self.criminal.type["Fear"] += 0.2
                        if random():
                            self.criminal.type["Rage"] += 0.1

                    bullet.remove_from_sprite_lists()
                    break

        if not self.criminal_is_spawned:
            self.time += delta_time

            n = randint(0, int(self.time)) - random()
            if n > 3:
                self.spawn_criminal()

        else:
            self.criminal.update(delta_time)

        copy_particles = self.particles.copy()
        for i in copy_particles:
            i.update(delta_time)
            if i.can_reap():
                self.particles.remove(i)

    def load_evidence(self, evidence):
        self.evidence_sprites = arcade.SpriteList()
        self.handprints = arcade.SpriteList()
        if evidence["forced entry"]:
            entry = self.entries.sprite_list[0]
            entry: arcade.Sprite
            entry.append_texture(arcade.load_texture(get_path("ForcedDoor.png")))
            entry.set_texture(1)

        shoe_print_texture = arcade.load_texture(get_path("Footprints.png"))
        for _ in range(randint(0, evidence["shoeprints"])):
            floor = choice(self.floor.sprite_list)
            while floor.collides_with_list(self.objects) or floor.collides_with_list(self.interior):
                floor = choice(self.floor.sprite_list)
            prints = arcade.Sprite(shoe_print_texture, 1, floor.center_x, floor.center_y, randint(0, 360))
            self.evidence_sprites.append(prints)

        hand_print_texture = arcade.load_texture(get_path("Handprint.png"))
        for _ in range(randint(0, evidence["handprints"])):
            interior_obj = choice(self.interior.sprite_list)
            path = str(interior_obj.texture.file_path)
            while "Wardrobe" in path or "Sink" in path or "Bath" in path or "TV" in path:
                interior_obj = choice(self.interior.sprite_list)
                path = str(interior_obj.texture.file_path)
            prints = arcade.Sprite(hand_print_texture, 1, interior_obj.center_x, interior_obj.center_y,
                                   randint(0, 360))

            self.handprints.append(prints)

        for _ in range(randint(1, 3)):
            obj = choice(self.interior.sprite_list)
            while obj in self.evidence_sprites.sprite_list:
                obj = choice(self.interior.sprite_list)
            obj.evidence = choice(["knife", "lock_picks", "button"])
            self.evidence_sprites.append(obj)

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
            if i[2] == "P" or i[2] == "H":
                self.points.append([cur_wd, cur_ht, "P"])
                if i[2] == "H":
                    self.hiding_poses.append([cur_wd, cur_ht, "H"])
                continue

            sprite = arcade.Sprite(get_path(i[2] + ".png"), (1, 1), cur_wd, cur_ht)
            self.interior.append(sprite)

    def load_room(self, room: str, width: float, height: float, wd: float, ht: float, rooms: list, is_hallway=False):
        original_width = width
        cur_room = [arcade.SpriteList(), arcade.SpriteList()]
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
                cur_room[1].append(sprite)
                self.points.append([sprite.center_x, sprite.center_y + 20, "D"])
                self.doors_points.append([sprite.center_x, sprite.center_y - 20, "D"])

            elif s == "D":
                sprite = arcade.Sprite(get_path("HUDoor.png"), (1, 1), width, height)
                for n in range(-1, 2):
                    floor = arcade.Sprite(get_path("Floor.png"), (1, 1), width + (wd / 3) * n, height)
                    self.floor.append(floor)
                self.doors_sprites.append(sprite)
                cur_room[1].append(sprite)
                self.points.append([sprite.center_x, sprite.center_y - 20, "d"])
                self.doors_points.append([sprite.center_x, sprite.center_y + 20, "D"])

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
                cur_room[0].append(sprite)
                continue

            width += wd
            self.objects.append(sprite)

        if not is_hallway:
            rooms.append(cur_room)
        return height
