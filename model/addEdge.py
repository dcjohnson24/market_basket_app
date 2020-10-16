# -*- coding: utf-8 -*-
"""
Created on Fri May 15 11:45:07 2020

@author: aransil
"""

import math
from typing import Tuple


def addEdge(start: tuple, end: tuple, edge_x: list, edge_y: list,
            lengthFrac: float = 1, arrowPos: str = None,
            arrowLength: float = 0.025, arrowAngle: int = 30,
            dotSize: int = 20) -> Tuple[list, list]:
    """ Create an edge with an arrow between two nodes

    Args:
        start (tuple): starting point
        end (tuple): end point
        edge_x (list): list of x coordinates
        edge_y (list): list of y coordinates
        lengthFrac (float, optional): length of edge as fraction of distance
            between nodes. Defaults to 1.
        arrowPos (str, optional): where the arrow appears on the edge.
            Can be None, 'middle', or 'end'. Defaults to None.
        arrowLength (float, optional): the length of the arrow head.
            Defaults to 0.025.
        arrowAngle (int, optional): The angle the arrow makes with the edge.
            Defaults to 30.
        dotSize (int, optional): plotly scatter dot size you are using
            (used to even out line spacing when you have a mix of edge lengths).
            Defaults to 20.

    Returns:
        Tuple[list, list]: lists of x and y coordinates.
    """
    # Get start and end cartesian coordinates
    x0, y0 = start
    x1, y1 = end

    # Incorporate the fraction of this segment covered by a dot into total reduction
    length = math.sqrt((x1-x0)**2 + (y1-y0)**2)
    dotSizeConversion = .0565 / 20  # length units per dot size
    convertedDotDiameter = dotSize * dotSizeConversion
    lengthFracReduction = convertedDotDiameter / length
    lengthFrac = lengthFrac - lengthFracReduction

    # If the line segment should not cover the entire distance, get actual start and end coords
    skipX = (x1-x0)*(1-lengthFrac)
    skipY = (y1-y0)*(1-lengthFrac)
    x0 = x0 + skipX/2
    x1 = x1 - skipX/2
    y0 = y0 + skipY/2
    y1 = y1 - skipY/2

    # Append line corresponding to the edge
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)  # Prevents a line being drawn from end of this edge to start of next edge
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

    # Draw arrow
    if arrowPos is not None:

        # Find the point of the arrow; assume is at end unless told middle
        pointx = x1
        pointy = y1

        eta = math.degrees(math.atan((x1-x0)/(y1-y0))) if y1 != y0 else 90.0

        if arrowPos == 'middle' or arrowPos == 'mid':
            pointx = x0 + (x1-x0)/2
            pointy = y0 + (y1-y0)/2

        # Find the directions the arrows are pointing
        signx = (x1-x0)/abs(x1-x0) if x1 != x0 else +1    # verify this once
        signy = (y1-y0)/abs(y1-y0) if y1 != y0 else +1    # verified

        # Append first arrowhead
        dx = arrowLength * math.sin(math.radians(eta + arrowAngle))
        dy = arrowLength * math.cos(math.radians(eta + arrowAngle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx**2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx**2 * signy * dy)
        edge_y.append(None)

        # And second arrowhead
        dx = arrowLength * math.sin(math.radians(eta - arrowAngle))
        dy = arrowLength * math.cos(math.radians(eta - arrowAngle))
        edge_x.append(pointx)
        edge_x.append(pointx - signx**2 * signy * dx)
        edge_x.append(None)
        edge_y.append(pointy)
        edge_y.append(pointy - signx**2 * signy * dy)
        edge_y.append(None)

    return edge_x, edge_y
