import numpy as np
import Table
import Rectangle

class TableTemplate:
	def __init__(self):
		self
		
def formatTable(tables,borders):
	border = Rectangle.combine(borders[0],borders[-1])
	tRectT = titleRectangularTable(tables,border)
	if not tRectT is None:
			print "Rectangular table with title" 
			return trt
			
	rectT = rectangularTable(tables,border)
	if not rectT is None:
		print "Rectangular table"
		return rectT

	titleUnforTable = titleUnformattedTable(tables,border)
	if not titleUnforTable is None:
		print "Title with unformatted table"
		return titleUnforTable

	print "No template match"

	return None# Table.Table(None,tables,False)


def titleUnformattedTable(tables,border):
	if len(tables[0]) == 1:
		if len(tables) == 2:
			return Table.Table(tables[0],tables[1:-1],False,border)
	return None



def titleRectangularTable(tables,border):
	if len(tables) > 2:
		if len(tables[0]) == 1:
			if rectangularTable(tables[1:-1],border):
				return Table.Table(tables[0],tables[1:-1],True,border)
			
	return None



def rectangularTable(tables,border):
	#Each must have same amount of columns (necesairy because of checks below??)
	columns = len(tables[0])
	for i in range(1,len(tables)):
		if not len(tables[i]) == columns:
			return None
	
	checkX = np.zeros((len(tables),columns + 1))
	checkY = np.zeros((len(tables)+1,columns))

	for i in range(0,len(tables)):
		for j in range(0,columns):
			checkX[i,j] = tables[i][j].p1.x
			checkY[i,j] = tables[i][j].p1.y
	
	for i in range(0,len(tables)):
		checkX[i,-1] = tables[i][-1].p4.x

	for j in range(0,columns):
		checkY[-1,j] = tables[-1][j].p2.y

	stdevX = np.std(checkX,axis = 0)
	stdevY = np.std(checkX,axis = 0)

	threshod = 3
	for i in range(0,stdevX.shape[0]):
		if stdevX[i] >= 3:
			return None

	for i in range(0,stdevY.shape[0]):
		if stdevY[i] >= 3:
			return None

	return Table.Table(None,tables,True,border)
		
	
def seperateFormatedUnformatted(tablesTemplates):
	formatted = []
	unformatted = []
	for tt in tablesTemplates:
		if tt.formatted:
			formatted.append(tt)
		else:
			unformatted.append(tt)
	return formatted, unformatted
