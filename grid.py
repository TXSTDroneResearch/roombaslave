import numpy as np

class GridPoint(object):
    """ Defines a point on the grid. Simple enough.
    A point /must/ have neighbors to be a member of a grid!
    """

    def __init__(self, pos):
        self._neighbors = []

    def AddNeighbor(self, neighbor):
        if neighbor in self._neighbors:
            # Pass on duplicates.
            return

        self._neighbors.append(neighbor)

        # Just to make this simple, we'll add ourselves to the point's neighbors.
        neighbor.AddNeighbor(self)
    
    def RemoveNeighbor(self, neighbor):
        if not isinstance(neighbor, GridPoint):
            raise ValueError("neighbor is of an invalid type!")

        if neighbor not in self._neighbors:
            # Neighbor is not part of our neighbors!
            return

        self._neighbors.remove(neighbor)
        neighbor.RemoveNeighbor(self)
    
    def HasNeighbors(self):
        return len(self._neighbors) != 0

class Grid(object):
    """ The Grid. A bunch of connected points.
    """
    
    def __init__(self):
        self._points = []
    
    def AddPoint(self, point):
        if not isinstance(point, GridPoint):
            raise ValueError("Point is of an invalid type! (must be GridPoint)")

        if not point.HasNeighbors():
            raise ValueError("Isolated points are not allowed!")