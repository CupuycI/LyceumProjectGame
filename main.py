import arcade.color

from Classes import *

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1280
SCREEN_TITLE = "RUC\nResponding to an urgent call"

class MainWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True, fullscreen=True)
        arcade.set_background_color(arcade.color.GRAY_BLUE)
        self.buttons_lst = []
        self.status = "MainMenu"
        self.was = ""
        self.level = ""
        self.game_size = ""

    def on_draw(self):
        self.clear()
        self.default_camera.use()
        if self.status == "MainMenu":
            if self.was != self.status:
                self.buttons_lst = [MyButton(self, SCREEN_WIDTH / 2.3, SCREEN_HEIGHT / 1.55,
                                             "На вызов", (lambda: change_status(self, "ChoosingLevel")),
                                             (125, 125, 125), (255, 0, 0), 50),
                                    MyButton(self, SCREEN_WIDTH / 2.35, SCREEN_HEIGHT / 2,
                                             "Настройки", (lambda: change_status(self, "Settings")),
                                             (125, 125, 125), (255, 0, 0), 50),
                                    MyButton(self, SCREEN_WIDTH / 2.2, SCREEN_HEIGHT / 2.7,
                                             "Выход", (lambda: self.close()),
                                             (125, 125, 125), (255, 0, 0), 50)
                                    ]
                self.was = self.status

            set_background("MainMenuBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
            for btn in self.buttons_lst:
                btn.draw()

        elif self.status == "ChoosingLevel":
            if self.was != self.status:
                self.buttons_lst = [MyButton(self, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 6, "Лёгкий",
                                             (lambda: change_status(self, "ChoosingSize", "Easy")),
                                             (125, 125, 125), (0, 255, 0), 40),
                                    MyButton(self, SCREEN_WIDTH / 2.25, SCREEN_HEIGHT / 6, "Средний",
                                             (lambda: change_status(self, "ChoosingSize", "Middle")),
                                             (125, 125, 125), (255, 192, 0), 40),
                                    MyButton(self, SCREEN_WIDTH / 1.275, SCREEN_HEIGHT / 6, "Сложный",
                                             (lambda: change_status(self, "ChoosingSize", "Hard")),
                                             (125, 125, 125), (255, 30, 30), 40),
                                    MyButton(self, SCREEN_WIDTH / 25, SCREEN_HEIGHT / 1.25, "Назад",
                                             (lambda: change_status(self, "MainMenu")),
                                             (125, 125, 125), (30, 30, 255), 30)]
                self.was = self.status

            set_background("ChooseLevelBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
            text = arcade.Text("Уровень сложности", SCREEN_WIDTH / 4.5, SCREEN_HEIGHT / 1.4, (255, 255, 255),
                               100)
            text.draw()
            set_image("ChooseEasyLevel.jpg", SCREEN_WIDTH / 6, SCREEN_HEIGHT / 2.25)
            set_image("ChooseMiddleLevel.jpg", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.25)
            set_image("ChooseHardLevel.jpg", SCREEN_WIDTH / 1.2, SCREEN_HEIGHT / 2.25)
            for btn in self.buttons_lst:
                btn.draw()

        elif self.status == "ChoosingSize":
            if self.was != self.status:
                self.buttons_lst = [MyButton(self, SCREEN_WIDTH / 25, SCREEN_HEIGHT / 1.25, "Назад",
                                             (lambda: change_status(self, "ChoosingLevel")),
                                             (125, 125, 125), (30, 30, 255), 30),
                                    MyButton(self, SCREEN_WIDTH / 8, SCREEN_HEIGHT / 6, "Малый",
                                             (lambda: change_status(self, "Game", "Small")),
                                             (125, 125, 125), (0, 255, 0), 40),
                                    MyButton(self, SCREEN_WIDTH / 2.25, SCREEN_HEIGHT / 6, "Средний",
                                             (lambda: change_status(self, "Game", "Middle")),
                                             (125, 125, 125), (255, 192, 0), 40),
                                    MyButton(self, SCREEN_WIDTH / 1.275, SCREEN_HEIGHT / 6, "Большой",
                                             (lambda: change_status(self, "Game", "Big")),
                                              (125, 125, 125), (255, 30, 30), 40)]
                self.was = self.status

            set_background("ChooseLevelBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
            text = arcade.Text("Размер локации", SCREEN_WIDTH / 3.75, SCREEN_HEIGHT / 1.4, (255, 255, 255),
                               100)
            text.draw()
            set_image("ChooseSmallSize.jpg", SCREEN_WIDTH / 6, SCREEN_HEIGHT / 2.25)
            set_image("ChooseMiddleSize.jpg", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2.25)
            set_image("ChooseBigSize.jpg", SCREEN_WIDTH / 1.2, SCREEN_HEIGHT / 2.25)
            for btn in self.buttons_lst:
                btn.draw()

        elif self.status == "Game":
            if self.was != "Game":
                self.keys = []
                if self.was != "Pause":
                    self.game_location = Location(self)
                    self.player = Detective(self, 200, self.height / 2, self.game_location)
                    self.sprite_lst = arcade.SpriteList()
                    self.sprite_lst.append(self.player)
                    self.camera = arcade.Camera2D()

                self.was = self.status

            self.clear(color=arcade.color.BLACK)
            self.camera.use()
            self.game_location.draw()
            self.sprite_lst.draw()
            self.player.draw()

        elif self.status == "Pause":
            if self.was != self.status:
                self.buttons_lst = [MyButton(self, SCREEN_WIDTH / 2.42, SCREEN_HEIGHT / 1.55,
                                             "Продолжить", (lambda: change_status(self, "Game")),
                                             (125, 125, 125), (255, 0, 0), 50),
                                    MyButton(self, SCREEN_WIDTH / 2.35, SCREEN_HEIGHT / 2,
                                             "Настройки", (lambda: change_status(self, "Settings")),
                                             (125, 125, 125), (0, 0, 255), 50),
                                    MyButton(self, SCREEN_WIDTH / 2.23, SCREEN_HEIGHT / 2.7,
                                             "На базу", (lambda: change_status(self, "MainMenu")),
                                             (125, 125, 125), (0, 0, 255), 50)
                                    ]
                self.background_texture = arcade.load_texture(get_path(f"PauseBackground{randint(1, 3)}.jpg"))
                self.was = self.status

            # set_background(self.backround_image, self.width, self.height)
            arcade.draw_texture_rect(self.background_texture,
                                     arcade.Rect(*arcade.LBWH(0, 0, self.width, self.height)))
            for btn in self.buttons_lst:
                btn.draw()

        elif self.status == "GameEnd":
            if self.was != self.status:
                self.was = self.status
                self.buttons_lst = [MyButton(self, SCREEN_WIDTH / 25, SCREEN_HEIGHT / 1.25, "В меню",
                                             (lambda: change_status(self, "MainMenu")),
                                             (125, 125, 125), (30, 30, 255), 30)]

            font_size = 20
            text1 = arcade.Text(f"Зафиксировано улик:           "
                                f"{len(self.player.collected_evidence.sprite_list)}/"
                                f"{len(self.game_location.evidence_sprites.sprite_list) +
                                   len([i for i in self.player.collected_evidence.sprite_list
                                        if "ClothPart" in str(i.texture.file_path)]) +
                                   len(self.game_location.handprints.sprite_list)}",
                                250, self.height - 300, font_size=font_size)
            text2 = arcade.Text(f"Преступник:                            "
                                f"{'Ликвидирован' if self.game_location.criminal_is_spawned and
                                                     self.game_location.criminal.hp <= 0 else 'Сбежал' if
                                self.game_location.criminal_is_spawned
                                else 'Не был обнаружен на месте преступления'}", 250, self.height - 350,
                                font_size=font_size)
            text3 = arcade.Text(f"Уровень сложности:             {self.level}", 250, self.height - 400,
                                font_size=font_size)
            text4 = arcade.Text(f"Размер локации:                   {self.game_size}", 250, self.height - 450,
                                font_size=font_size)
            text5 = arcade.Text(f"Детектив:                                 "
                                f"{'Жив' if self.player.hp > 0 else 'Погиб'}",
                                250, self.height - 500, font_size=font_size)
            set_background("GameEndBackground.jpg", SCREEN_WIDTH, SCREEN_HEIGHT)
            arcade.draw_lbwh_rectangle_filled(200, 100, self.width - 400, self.height - 200,
                                              (119, 119, 119, 160))
            arcade.draw_lbwh_rectangle_outline(198, 98, self.width - 396, self.height - 196,
                                               (29, 29, 29), 10)

            text1.draw()
            text2.draw()
            text3.draw()
            text4.draw()
            text5.draw()


            for btn in self.buttons_lst:
                btn.draw()


    def on_update(self, delta_time: float):
        try:
            if self.status == "Game":
                self.player.update(self.keys, delta_time)
                self.game_location.update(delta_time)
                move_camera_to_player(self, 0.1)

        except AttributeError as e:
            print(e)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        for btn in self.buttons_lst:
            btn.on_hover_update(x, y)

        if self.status == "Game":
            try:
                x += self.camera.position.x - self.center_x
                self.player.update_angle(x, y)

            except AttributeError:
                pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.status == "Game":
            if self.player.item == self.player.items[0]:
                x += self.camera.position.x - self.center_x
                bullet = Bullet(self.player.center_x, self.player.center_y, 600, x, y)
                self.game_location.bullets_sprites.append(bullet)
                self.game_location.bullets.append(bullet)
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons_lst:
                btn.on_press()

    def on_key_press(self, symbol: int, modifiers: int):
        if "Pause" != self.status != "Game":
            return
        if symbol == arcade.key.ESCAPE:
            self.status = "Pause" if self.status != "Pause" else "Game"
            return
        self.keys.append(symbol)

    def on_key_release(self, symbol: int, modifiers: int):
        if not self.status == "Game" or symbol == arcade.key.ESCAPE:
            return

        del self.keys[self.keys.index(symbol)]


def setup_game(width, height, title):
    game = MainWindow(width, height, title)
    return game


def main():
    setup_game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()