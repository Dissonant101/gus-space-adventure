import datetime as dt
import firebase_admin
from firebase_admin import credentials, firestore
from abc import abstractmethod, ABCMeta
from typing import List, Set


class GameModel:
	"""Stores all game data.

	Includes object coordinates, speeds, hitbox radius, hp, fuel, and score.
	"""

	def __init__(self):
		"""Inits GameModel."""
		self.object_models = {}

	def __setitem__(self, key: str, value: "ObjectModel"):
		"""Assigns a model to a key in object_models."""
		self.object_models[key] = value

	def __getitem__(self, item: str) -> "ObjectModel":
		"""Returns model for a specified key."""
		return self.object_models[item]


class LeaderboardModel:
	"""Handles leaderboard connection and updates."""

	def __init__(self):
		"""Inits LeaderboardModel.

		Creates connection to firestore database.
		Stores a reference to leaderboard document.
		"""
		self.cred = credentials.Certificate("config/service_creds.json")
		firebase_admin.initialize_app(self.cred)
		self.db = firestore.client()
		self.doc_ref = self.db.collection("gsa").document("leaderboard")
		self.doc_ref.get()
		self.datetime_format = "%Y/%m/%d %H:%M:%S.%f"  # Format for time: YYYY/MM/DD HH:MM:SS.MMMMMM

	def get(self, difficulty: str) -> List[dict]:
		"""Gets current leaderboard from database."""
		leaderboard = self.doc_ref.get().to_dict()[difficulty]
		for entry in leaderboard:
			entry["timestamp"] = dt.datetime.strptime(entry["timestamp"], self.datetime_format)
		return leaderboard

	def update(self, difficulty: str, username: str, score: int):
		"""Adds current entry to leaderboard if it is a high score."""
		timestamp = dt.datetime.now()
		entry = {"username": username, "score": score, "timestamp": timestamp}
		leaderboard = self.get(difficulty)
		leaderboard.append(entry)
		leaderboard.sort(key=lambda e: (-e["score"], e["timestamp"], e[
			"username"]))  # Sorts leaderboard by highest score, then lowest time, then alphabetically
		leaderboard.pop()  # Removes last entry in leaderboard, also known as the lowest score
		for entry in leaderboard:
			entry["timestamp"] = entry["timestamp"].strftime(self.datetime_format)
		self.doc_ref.update({difficulty: leaderboard})


class ObjectModel(metaclass=ABCMeta):
	"""Contains all objects with models that may update."""

	def __init__(self, x: int, y: int):
		"""Inits ObjectModel."""
		self.x = x
		self.y = y


class Collidable(ObjectModel):
	"""Contains all objects that may collide with others."""

	def __init__(self, x: int, y: int, r: int):
		"""Inits Collidable."""
		super().__init__(x, y)
		self.r = r  # Radius of hitbox

	def update_pos(self, x_offset: int, y_offset: int):
		"""Updates the x, y position by offsets."""
		self.x += x_offset
		self.y += y_offset

	def collided(self, other: "Driftable"):
		"""Checks if a Collidable has collided with a Driftable."""
		distance = ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5  # Distance between Collidables

		if distance < self.r + other.r:
			other.aftermath(self)  # Runs what should happen once Collidables touch


class Driftable(Collidable):
	"""Contains all objects that move at a constant speed and collide."""

	def __init__(self, x: int, y: int, r: int, dx: int, dy: int):
		"""Inits Driftable."""
		super().__init__(x, y, r)
		self.dx = dx
		self.dy = dy

	def destroy(self):
		"""Moves Driftable objects offscreen when collided to be handled by drift_all function."""
		self.x = float("-inf")  # Moves x-coordinate of Driftable to negative infinity

	def drift(self):
		"""Moves x, y position by the defined deltas."""
		self.update_pos(self.dx, self.dy)

	@staticmethod
	def drift_all(driftables: List["Driftable"]) -> list:
		"""Moves all Driftables and checks if it is offscreen.

		Returns a list of indexes of offscreen Driftables.
		"""
		offscreen = []

		for i in range(len(driftables)):
			driftables[i].drift()
			if driftables[i].x + driftables[i].r < 0:
				offscreen.append(i)

		return offscreen

	@abstractmethod
	def aftermath(self, spaceship_model: "SpaceshipModel"):
		"""Runs what happens after a Collidable has collided with a Driftable."""
		pass


class SpaceshipModel(Collidable):
	"""Model for spaceship."""

	def __init__(self, x: int, y: int, r: int, hp: int, fuel: int):
		"""Inits SpaceshipModel."""
		super().__init__(x, y, r)
		self.hp = hp
		self.fuel = fuel
		self.score = 0
		self.movement_speed = 10

	def move(self, keys_pressed: Set[str], game_width: int, game_height: int, fuel_consumption: int):
		"""Moves spaceship within bounds of screen based on keys pressed."""
		vx = 0
		vy = 0

		if "a" in keys_pressed:
			vx -= 1
		if "d" in keys_pressed:
			vx += 1
		if "w" in keys_pressed:
			vy -= 1
		if "s" in keys_pressed:
			vy += 1

		if vx != 0 or vy != 0:
			self.fuel -= fuel_consumption  # Subtracts fuel from spaceship if it is moving

		if vx < 0 and self.x > self.r:
			self.update_pos(-self.movement_speed, 0)  # Move left
		elif vx > 0 and self.x < game_width - self.r:
			self.update_pos(self.movement_speed, 0)  # Move right

		if vy < 0 and self.y > self.r:
			self.update_pos(0, -self.movement_speed)  # Move up
		elif vy > 0 and self.y < game_height - self.r:
			self.update_pos(0, self.movement_speed)  # Move down


class AsteroidModel(Driftable):
	"""Model for asteroid."""

	def aftermath(self, spaceship_model: "SpaceshipModel"):
		"""Removes 1 hp from spaceship and destroys itself."""
		spaceship_model.hp -= 1
		self.destroy()


class HpPowerUpModel(Driftable):
	"""Model for HP power-up."""

	def aftermath(self, spaceship_model: "SpaceshipModel"):
		"""Adds 1 HP to spaceship (9 max) and destroys itself."""
		spaceship_model.hp = min(spaceship_model.hp + 1, 9)
		self.destroy()


class FuelPowerUpModel(Driftable):
	"""Model for fuel power-up."""

	def aftermath(self, spaceship_model: "SpaceshipModel"):
		"""Adds 20 fuel to spaceship (100 max) and destroys itself."""
		spaceship_model.fuel = min(spaceship_model.fuel + 20, 100)
		self.destroy()


class ScorePowerUpModel(Driftable):
	"""Model for score power-up."""

	def aftermath(self, spaceship_model: "SpaceshipModel"):
		"""Adds 5000 score to spaceship and destroys itself."""
		spaceship_model.score += 5000
		self.destroy()
