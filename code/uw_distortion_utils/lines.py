from ctypes import Array

import cv2
import numpy as np


def lines_from_markup(pts_x, pts_y, n_lines_vertical, n_lines_horizontal):
    lines = []
    for i in range(1, n_lines_horizontal+1):
        n = []
        for k in range(1, n_lines_vertical+1):
            n.append(k + (i - 1) * n_lines_vertical)
        line = []
        for j in n:
            line.append(np.array([pts_x.get(j), pts_y.get(j)]))
        lines.append(np.array(line))
    for i in range(1, n_lines_vertical+1):
        n = []
        for k in range(0, n_lines_horizontal):
            n.append(n_lines_vertical * k + i)
        line = []
        for j in n:
            line.append(np.array([pts_x.get(j), pts_y.get(j)]))
        lines.append(np.array(line))
    return lines

def lines_from_image(img: Array, n_lines_vertical: int, n_lines_horizontal: int):
    """_summary_

    Args:
        img (Array): _description_
        n_lines_vertical (int): _description_
        n_lines_horizontal (int): _description_

    Returns:
        _type_: _description_
    """    
    cols = n_lines_vertical
    rows = n_lines_horizontal
    sz = (cols, rows)
    found, pts = cv2.findChessboardCorners(img, sz)
    if not found:
        return None, None
    else:
        lines = [] # [(N, 2), ...]

        for row in pts.reshape((rows, cols, 2)):
            lines.append(row)
        for col in pts.reshape((rows, cols, 2)).swapaxes(0, 1):
            lines.append(col)
        return pts.reshape((-1, 2)), lines

