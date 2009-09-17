class particleManager():
	def __init__(self):
		self.particles = []
	def addNew(self, obj):
		self.particles += [obj]
	def updateAll(self):
		for i in self.particles:
			i.update()
			if i.ticks > i.lifetime:
				self.particles.remove(i)
				
	def count(self):
		return len(self.particles)

class weaponManager():
	def __init__(self, screen):
		self.parent = screen
		self.bullets = []

	def shoot(self, ship_id, class_name):
		self.bullets.append(class_name(self.parent.particleManager, self.parent.statki[ship_id].pos[:], self.parent.statki[ship_id].rot))

	def count(self):
		return len(self.bullets)

	def updateAll(self):
		for i in self.bullets:
			i.update()
			d = i.distance()
			if d > i.distance_max:
				i.hit()
				self.bullets.remove(i)
