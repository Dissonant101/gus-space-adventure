from model import *
import tkinter as tk
from os import listdir
from random import randint
from abc import abstractmethod, ABCMeta
from typing import List


class GameView:
	"""Stores all game views."""
	resources = {}  # Static dictionary of Tkinter PhotoImages

	def __init__(self):
		"""Inits GameView."""
		self.object_views = {}
		self.screen_width = 800
		self.screen_height = 900
		self.game_width = 800
		self.game_height = 800
		self.background = "black"

		self.root = tk.Tk()
		self.root.title("Gus' Space Adventure")
		self.root.minsize(self.screen_width, self.screen_height)
		self.screen = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height,
								background=self.background)
		self.screen.pack()

		self.load_resources()
		self.menu = Menu(self.screen)  # Creates instance of Menu object

	def __setitem__(self, key: str, value: "ObjectView"):
		"""Assigns a view to a key in object_views."""
		self.object_views[key] = value

	def __getitem__(self, item: str) -> "ObjectView":
		"""Returns view for a specified key."""
		return self.object_views[item]

	def load_resources(self):
		"""Adds Tkinter PhotoImages to GameView.resources.

		Automatically creates a Tkinter PhotoImage for every file in resources and assigns it a key.
		"""
		for file_name in listdir("resources"):
			GameView.resources[file_name] = tk.PhotoImage(file=f"resources/{file_name}")

	def draw_all(self, game_model: "GameModel"):
		"""Draws all views using models."""
		for obj in self.object_views:
			if type(self.object_views[obj]) == list:
				for i in range(len(self.object_views[obj])):
					self.object_views[obj][i].draw(game_model[obj][i])
			else:
				self.object_views[obj].draw(game_model[obj])

	def delete_all(self):
		"""Deletes all views."""
		for obj in self.object_views:
			if type(self.object_views[obj]) == list:
				for i in range(len(self.object_views[obj])):
					self.object_views[obj][i].delete()
			else:
				self.object_views[obj].delete()

	def update(self):
		"""Updates Canvas."""
		self.screen.update()


class Menu:
	"""All views not directly related to the running game."""

	def __init__(self, screen: "tk.Canvas"):
		"""Inits Menu."""
		self.screen = screen
		self.button_pos = {}  # Stores the x, y coordinates of the center of buttons
		self.current_display = None  # Saves what screen is currently being displayed to be used by click handler.
		self.username = None

	def clear(self):
		"""Clears the Canvas"""
		self.screen.delete("all")
		self.current_display = None

	def draw_background(self):
		"""Draws stars and copyright text."""
		for i in range(100):
			a = randint(0, int(self.screen["width"]))
			b = randint(0, int(self.screen["height"]))
			self.screen.create_oval(a - 1, b - 1, a + 1, b + 1, fill="yellow", outline="yellow")
		self.screen.create_text(15, int(self.screen["height"]) - 15, text="Steven Chen © 2022. All rights reserved.",
								font="Helvetica 14", fill="white", anchor="sw")

	def draw_username_input(self, root: "tk.Tk"):
		"""Draws username input screen."""

		def submit_handler(*args):
			"""Saves username and displays main menu when given a valid username.

			Destroys submit button and input field.
			"""
			self.username = input_field.get()
			if 0 < len(self.username) <= 12:
				input_field.destroy()
				submit_button.destroy()
				self.screen.focus_set()
				self.draw_menu()

		self.current_display = "username input"
		self.draw_background()
		self.title = self.screen.create_image(int(self.screen["width"]) // 2, 200,
											  image=GameView.resources["title.png"], anchor="center")
		self.screen.create_text(int(self.screen["width"]) // 2, int(self.screen["height"]) // 2 - 80, text="Username",
								font="Helvetica 26", fill="white")
		self.screen.create_text(int(self.screen["width"]) // 2, int(self.screen["height"]) // 2 - 45,
								text="(12 characters max)", font="Helvetica 12", fill="white")
		input_field = tk.Entry(root, font="Helvetica 24")
		input_field.place(width=400, height=50, relx=0.5, y=int(self.screen["height"]) // 2, anchor="center")
		input_field.bind("<Return>", submit_handler)
		input_field.focus_set()
		submit_button = tk.Button(root, text="Submit", font="Helvetica 18", command=submit_handler)
		submit_button.place(width=100, height=50, relx=0.5, y=int(self.screen["height"]) // 2 + 75, anchor="center")

	def draw_menu(self):
		"""Draws main menu screen."""
		self.clear()
		self.current_display = "menu"
		self.draw_background()
		self.button_pos["quit_button"] = int(self.screen["width"]) - 150, int(self.screen["height"]) - 75
		self.quit_button = self.screen.create_image(*self.button_pos["quit_button"],
													image=GameView.resources["quit_button.png"], anchor="center")
		self.title = self.screen.create_image(int(self.screen["width"]) // 2, 200,
											  image=GameView.resources["title.png"], anchor="center")
		self.button_pos["play_button"] = (int(self.screen["width"]) // 2, 400)
		self.play_button = self.screen.create_image(*self.button_pos["play_button"],
													image=GameView.resources["play_button.png"], anchor="center")
		self.button_pos["instructions_button"] = (int(self.screen["width"]) // 2, 500)
		self.instructions_button = self.screen.create_image(*self.button_pos["instructions_button"],
															image=GameView.resources["instructions_button.png"],
															anchor="center")
		self.button_pos["leaderboard_button"] = (int(self.screen["width"]) // 2, 600)
		self.leaderboard_button = self.screen.create_image(*self.button_pos["leaderboard_button"],
														   image=GameView.resources["leaderboard_button.png"],
														   anchor="center")

	def draw_levels(self):
		"""Draws difficulty selection screen."""
		self.clear()
		self.current_display = "levels"
		self.draw_background()
		self.button_pos["main_menu_button"] = (150, 100)
		self.main_menu_button = self.screen.create_image(*self.button_pos["main_menu_button"],
														 image=GameView.resources["main_menu_button.png"],
														 anchor="center")
		self.button_pos["easy_button"] = (int(self.screen["width"]) // 2, 400)
		self.easy_button = self.screen.create_image(*self.button_pos["easy_button"],
													image=GameView.resources["easy_button.png"], anchor="center")
		self.button_pos["medium_button"] = (int(self.screen["width"]) // 2, 500)
		self.medium_button = self.screen.create_image(*self.button_pos["medium_button"],
													  image=GameView.resources["medium_button.png"], anchor="center")
		self.button_pos["hard_button"] = (int(self.screen["width"]) // 2, 600)
		self.hard_button = self.screen.create_image(*self.button_pos["hard_button"],
													image=GameView.resources["hard_button.png"], anchor="center")

	def draw_instructions(self):
		"""Draws instructions for game."""
		self.clear()
		self.current_display = "instructions"
		self.draw_background()
		self.button_pos["main_menu_button"] = (150, 100)
		self.main_menu_button = self.screen.create_image(*self.button_pos["main_menu_button"],
														 image=GameView.resources["main_menu_button.png"],
														 anchor="center")
		self.instructions_page = self.screen.create_image(int(self.screen["width"]) // 2, 475,
														  image=GameView.resources["instructions_page.png"],
														  anchor="center")

	def draw_leaderboard(self):
		"""Draws leaderboard display selection screen."""
		self.clear()
		self.current_display = "leaderboard"
		self.draw_background()
		self.button_pos["main_menu_button"] = (150, 100)
		self.main_menu_button = self.screen.create_image(*self.button_pos["main_menu_button"],
														 image=GameView.resources["main_menu_button.png"],
														 anchor="center")
		self.button_pos["easy_button"] = (int(self.screen["width"]) // 2, 400)
		self.easy_button = self.screen.create_image(*self.button_pos["easy_button"],
													image=GameView.resources["easy_button.png"], anchor="center")
		self.button_pos["medium_button"] = (int(self.screen["width"]) // 2, 500)
		self.medium_button = self.screen.create_image(*self.button_pos["medium_button"],
													  image=GameView.resources["medium_button.png"], anchor="center")
		self.button_pos["hard_button"] = (int(self.screen["width"]) // 2, 600)
		self.hard_button = self.screen.create_image(*self.button_pos["hard_button"],
													image=GameView.resources["hard_button.png"], anchor="center")

	def draw_scores(self, lb: List[dict]):
		"""Draws top 10 scores from leaderboard."""
		for i in range(10):
			self.screen.create_text(100, i * 50 + 250, text=f"{i + 1}.", font="Helvetica 30", fill="white", anchor="e")
			self.screen.create_text(130, i * 50 + 250, text=f"{lb[i]['username']}", font="Helvetica 30", fill="white",
									anchor="w")
			self.screen.create_text(int(self.screen["width"]) - 100, i * 50 + 250, text=f"{lb[i]['score']}",
									font="Helvetica 30", fill="deep sky blue", anchor="e")

	def draw_easy_leaderboard(self, lb_model: "LeaderboardModel"):
		"""Draws easy mode leaderboard screen."""
		self.clear()
		self.current_display = "easy leaderboard"
		self.draw_background()
		self.button_pos["leaderboard_button"] = (150, 100)
		self.leaderboard_button = self.screen.create_image(*self.button_pos["leaderboard_button"],
														   image=GameView.resources["leaderboard_button.png"],
														   anchor="center")
		lb = lb_model.get("easy")
		self.draw_scores(lb)

	def draw_medium_leaderboard(self, lb_model: "LeaderboardModel"):
		"""Draws medium mode leaderboard screen."""
		self.clear()
		self.current_display = "medium leaderboard"
		self.draw_background()
		self.button_pos["leaderboard_button"] = (150, 100)
		self.leaderboard_button = self.screen.create_image(*self.button_pos["leaderboard_button"],
														   image=GameView.resources["leaderboard_button.png"],
														   anchor="center")
		lb = lb_model.get("medium")
		self.draw_scores(lb)

	def draw_hard_leaderboard(self, lb_model: "LeaderboardModel"):
		"""Draws hard mode leaderboard screen."""
		self.clear()
		self.current_display = "hard leaderboard"
		self.draw_background()
		self.button_pos["leaderboard_button"] = (150, 100)
		self.leaderboard_button = self.screen.create_image(*self.button_pos["leaderboard_button"],
														   image=GameView.resources["leaderboard_button.png"],
														   anchor="center")
		lb = lb_model.get("hard")
		self.draw_scores(lb)

	def draw_game_over(self, score: int):
		"""Draws death screen."""
		self.clear()
		self.current_display = "game_over"
		self.draw_background()
		self.final_score_display = self.screen.create_text(int(self.screen["width"]) // 2, 400,
														   text=f"Final score: {score}", font="Helvetica 40",
														   fill="white")
		self.button_pos["main_menu_button"] = (int(self.screen["width"]) // 2, 500)
		self.main_menu_button = self.screen.create_image(*self.button_pos["main_menu_button"],
														 image=GameView.resources["main_menu_button.png"],
														 anchor="center")


class ObjectView(metaclass=ABCMeta):
	"""Contains all objects with views."""

	def __init__(self, screen: "Canvas"):
		"""Inits ObjectView"""
		self.screen = screen
		self.components = []

	def delete(self):
		"""Deletes all components of itself."""
		self.screen.delete(*self.components)

	@abstractmethod
	def draw(self, model: "ObjectModel"):
		"""Draws view from model."""
		pass


class SpaceshipView(ObjectView):
	"""View for spaceship."""

	def draw(self, model: "SpaceshipModel"):
		"""Draws spaceship."""
		self.components = [
			self.screen.create_image(model.x + 3, model.y - 5, image=GameView.resources["spaceship.png"],
									 anchor="center"),
			self.screen.create_oval(model.x - model.r, model.y - model.r, model.x + model.r, model.y + model.r, fill="",
									outline="white")]


class SpaceshipStatsView(ObjectView):
	"""View for spaceship stats."""

	def draw(self, model: "SpaceshipModel"):
		"""Draws hp, fuel bar, and score."""
		self.components = [
			self.screen.create_line(0, 800, int(self.screen["width"]), 800, fill="white", width=10),
			self.screen.create_text(10, 810, text="HP: ", font="Helvetica 20", fill="white", anchor="nw"),
			self.screen.create_text(10, 853, text="Fuel: ", font="Helvetica 20", fill="white", anchor="nw"),
			self.screen.create_text(790, 810, text="Score", font="Helvetica 20", fill="white", anchor="ne"),
			self.screen.create_text(790, 853, text=f"{model.score}", font="Helvetica 20", fill="deep sky blue",
									anchor="ne"),
			self.screen.create_rectangle(80, 860, 280, 880, fill="white", outline="white"),
			self.screen.create_rectangle(80, 860, 80 + 200 * model.fuel / 100, 880, fill="yellow", outline="white")]
		for i in range(model.hp):
			self.components.append(
				self.screen.create_image(i * 30 + 60, 813, image=GameView.resources["heart.gif"], anchor="nw"))

		if model.hp == 9:
			self.components.append(self.screen.create_text(330, 840, text="(Max)", font="Helvetica 10", fill="white", anchor="w"))


class AsteroidView(ObjectView):
	"""View for asteroid."""

	def draw(self, model: "AsteroidModel"):
		"""Draws asteroid."""
		self.components = [
			self.screen.create_oval(model.x - model.r, model.y - model.r, model.x + model.r, model.y + model.r,
									fill="grey")]


class HpPowerUpView(ObjectView):
	"""View for HP power-up."""

	def draw(self, model: "HpPowerUpModel"):
		"""Draws heart and bubble."""
		self.components = [
			self.screen.create_image(model.x, model.y, image=GameView.resources["heart.gif"], anchor="center"),
			self.screen.create_image(model.x, model.y, image=GameView.resources["bubble.png"], anchor="center")]


class FuelPowerUpView(ObjectView):
	"""View for fuel power-up."""

	def draw(self, model: "FuelPowerUpModel"):
		"""Draws lightning bolt and bubble."""
		self.components = [
			self.screen.create_image(model.x, model.y, image=GameView.resources["lightning.png"], anchor="center"),
			self.screen.create_image(model.x, model.y, image=GameView.resources["bubble.png"], anchor="center")]


class ScorePowerUpView(ObjectView):
	"""View for score power-up."""

	def draw(self, model: "ScorePowerUpModel"):
		"""Draws fish and bubble."""
		self.components = [
			self.screen.create_image(model.x, model.y, image=GameView.resources["fish.png"], anchor="center"),
			self.screen.create_image(model.x, model.y, image=GameView.resources["bubble.png"], anchor="center")]
