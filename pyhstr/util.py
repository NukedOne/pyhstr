class Counter:
	def __init__(self):
		self.value = 0

	def inc(self, boundary):
		if self.value == boundary - 1:
			self.value = 0
		else:
			self.value += 1

	def dec(self, boundary):
		if self.value == 0:
			self.value = boundary - 1
		else:
			self.value -= 1

