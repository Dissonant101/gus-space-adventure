from model import *
from view import *
from tkinter import EventType
from time import sleep
from random import randint, choice


class Game:
	"""Controller for game.

	Handles inputs and passes it to the model.
	"""

	def __init__(self):
		"""Inits Game."""
		self.model = GameModel()
		self.view = GameView()
		self.leaderboard = LeaderboardModel()

		self.frame_rate = 0.02
		self.keys_pressed = set()
		self.fuel_consumption = None

	def generate_asteroid_model(self):
		"""Generates a new AsteroidModel."""
		return AsteroidModel(randint(self.view.game_width, 2 * self.view.game_width),
							 randint(40, self.view.game_height - 40), randint(20, 40), -randint(4, 6), 0)

	def generate_powerup(self):
		"""Generates a new PowerUpModel and a corresponding PowerUpView."""
		if self.model["spaceship"].fuel < 40:
			return (
			FuelPowerUpModel(self.view.game_width + 100, randint(36, self.view.game_height - 36), 36, -randint(4, 6),
							 0), FuelPowerUpView(self.view.screen))

		powerups = [(HpPowerUpModel(self.view.screen_width + 100, randint(36, self.view.game_height - 36), 36,
									-randint(4, 6), 0), HpPowerUpView(self.view.screen)), (
					FuelPowerUpModel(self.view.game_width + 100, randint(36, self.view.game_height - 36), 36,
									 -randint(4, 6), 0), FuelPowerUpView(self.view.screen)), (
					ScorePowerUpModel(self.view.game_width + 100, randint(36, self.view.game_height - 36), 36,
									  -randint(4, 6), 0), ScorePowerUpView(self.view.screen))]
		return choice(powerups)

	def set_initial_values(self, difficulty: str):
		"""Initializes models and views."""
		if difficulty == "easy":
			num_asteroids = 10
			base_hp = 5
			self.fuel_consumption = 0.2
		elif difficulty == "medium":
			num_asteroids = 15
			base_hp = 4
			self.fuel_consumption = 0.2
		elif difficulty == "hard":
			num_asteroids = 20
			base_hp = 3
			self.fuel_consumption = 0.25

		self.model["spaceship"] = SpaceshipModel(150, 400, 40, base_hp, 100)
		self.view["spaceship"] = SpaceshipView(self.view.screen)
		self.model["asteroids"] = [self.generate_asteroid_model() for i in range(num_asteroids)]
		self.view["asteroids"] = [AsteroidView(self.view.screen) for i in range(num_asteroids)]
		self.model["stats"] = self.model["spaceship"]
		self.view["stats"] = SpaceshipStatsView(self.view.screen)
		self.model["powerup"], self.view["powerup"] = self.generate_powerup()

	def run(self):
		"""Binds events and shows username input screen."""
		self.bind_events()
		self.view.menu.draw_username_input(self.view.root)
		self.view.screen.mainloop()

	def start(self, difficulty: str):
		"""Runs all game functions."""
		self.view.menu.clear()
		self.set_initial_values(difficulty)

		while self.model["spaceship"].hp > 0 and "q" not in self.keys_pressed:
			if self.model["spaceship"].fuel > 0:
				self.model["spaceship"].move(self.keys_pressed, self.view.game_width, self.view.game_height,
											 self.fuel_consumption)

			for asteroid in self.model["asteroids"]:
				self.model["spaceship"].collided(asteroid)
			self.model["spaceship"].collided(self.model["powerup"])

			offscreen_asteroids = Driftable.drift_all(self.model["asteroids"])
			for i in offscreen_asteroids:
				self.model["asteroids"][i] = self.generate_asteroid_model()
			if Driftable.drift_all([self.model["powerup"]]):
				self.model["powerup"], self.view["powerup"] = self.generate_powerup()
			self.view.draw_all(self.model)
			self.view.update()
			sleep(self.frame_rate)
			self.view.delete_all()
			self.model["spaceship"].score += 10

		self.end_game(difficulty)

	def end_game(self, difficulty: str):
		"""Shows game over screen and uploads score to leaderboard database."""
		self.view.menu.draw_game_over(self.model["spaceship"].score)
		self.leaderboard.update(difficulty, self.view.menu.username, self.model["spaceship"].score)

	def bind_events(self):
		"""Binds key down, key up, and left click."""
		self.view.screen.bind("<Key>", self.key_down_handler)
		self.view.screen.bind("<KeyRelease>", self.key_up_handler)
		self.view.screen.bind("<ButtonRelease-1>", self.mouse_up_handler)

	def key_down_handler(self, event: "EventType.KeyPress"):
		"""Adds keys being pressed to keys_pressed."""
		self.keys_pressed.add(event.keysym)

	def key_up_handler(self, event: "EventType.KeyRelease"):
		"""Remove keys from keys_pressed when released."""
		if event.keysym in self.keys_pressed:
			self.keys_pressed.remove(event.keysym)

	def mouse_up_handler(self, event: "EventType.ButtonRelease"):
		"""Takes mouse inputs."""

		def is_clicked(button_name: str):
			"""Checks if buttons are clicked."""
			button_x, button_y, = self.view.menu.button_pos[button_name]
			button_width_offset, button_height_offset = GameView.resources[f"{button_name}.png"].width() // 2, \
														GameView.resources[f"{button_name}.png"].height() // 2

			if button_x - button_width_offset <= event.x <= button_x + button_width_offset and button_y - button_height_offset <= event.y <= button_y + button_height_offset:
				return True

		if self.view.menu.current_display == "menu":
			if is_clicked("play_button"):
				self.view.menu.draw_levels()
			elif is_clicked("instructions_button"):
				self.view.menu.draw_instructions()
			elif is_clicked("leaderboard_button"):
				self.view.menu.draw_leaderboard()
			elif is_clicked("quit_button"):
				self.view.root.destroy()

		elif self.view.menu.current_display == "levels":
			if is_clicked("main_menu_button"):
				self.view.menu.draw_menu()
			elif is_clicked("easy_button"):
				self.start("easy")
			elif is_clicked("medium_button"):
				self.start("medium")
			elif is_clicked("hard_button"):
				self.start("hard")

		elif self.view.menu.current_display == "instructions":
			if is_clicked("main_menu_button"):
				self.view.menu.draw_menu()

		elif self.view.menu.current_display == "leaderboard":
			if is_clicked("main_menu_button"):
				self.view.menu.draw_menu()
			elif is_clicked("easy_button"):
				self.view.menu.draw_easy_leaderboard(self.leaderboard)
			elif is_clicked("medium_button"):
				self.view.menu.draw_medium_leaderboard(self.leaderboard)
			elif is_clicked("hard_button"):
				self.view.menu.draw_hard_leaderboard(self.leaderboard)

		elif self.view.menu.current_display == "easy leaderboard":
			if is_clicked("leaderboard_button"):
				self.view.menu.draw_leaderboard()

		elif self.view.menu.current_display == "medium leaderboard":
			if is_clicked("leaderboard_button"):
				self.view.menu.draw_leaderboard()

		elif self.view.menu.current_display == "hard leaderboard":
			if is_clicked("leaderboard_button"):
				self.view.menu.draw_leaderboard()

		elif self.view.menu.current_display == "game_over":
			if is_clicked("main_menu_button"):
				self.view.menu.draw_menu()


if __name__ == "__main__":
	game = Game()

	game.run()
