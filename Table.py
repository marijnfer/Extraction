
class Table:
	def __init__(self,title,table,formatted,border):
		self.title = title
		self.table = table
		self.border = border
		self.formatted = formatted

	def setDirection(self,direction):
		self.direction = direction #True = hor