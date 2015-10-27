# Returns 1 if the given point is within the bounds of the given rectangle
#	point: (x,y)
#	rect:  (x,y,width,height)
def pointInRect(point, rect):
	if point[0] > rect[0] and point[1] > rect[1] and point[0] < rect[0]+rect[2] and point[1] < rect[1]+rect[3]:
		return 1
	else:
		return 0
