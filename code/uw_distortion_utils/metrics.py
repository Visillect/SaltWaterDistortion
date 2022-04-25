import math
from ctypes import Array

import numpy as np
import scipy.linalg

from uw_distortion_utils.lines import lines_from_image, lines_from_markup


def metric1(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    """_summary_

    Args:
        lines (Array): _description_
        n_lines_vertical (int): _description_
        n_lines_horizontal (int): _description_

    Returns:
        _type_: _description_
    """
    errors = allLinesQuality_metric1(lines, n_lines_vertical, n_lines_horizontal)
    sqrmean = errors.mean()**0.5
    max_dist = errors.max()**0.5

    return np.array([sqrmean, max_dist])

def allLinesQuality_metric2(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    maxLen = max(((np.array(line[0]) - np.array(line[-1])) ** 2).sum() for line in lines)**0.5
    
    maxs = []
    n = [0, n_lines_vertical-1, n_lines_vertical, n_lines_vertical + n_lines_horizontal-1]
    for i in n:
        line = lines[i]
        _, max_ = lineQuality_metric2(line * 1000 / maxLen)
        maxs.append(max_)
    maxs = np.array(maxs)
    
    return maxs.mean(), maxs.max()

def allLinesQuality_metric1(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    # returns array of squared errors (for every point)
    maxLen = max(
        ((line[0] - line[-1]) ** 2).sum()
        for line in lines
    )**0.5

    quals = []
    for line in lines:
        mse = lineQuality_metric1(line * 1000 / maxLen)
        quals.extend(mse)
    quals = np.array(quals)
    return quals

def lineQuality_metric2(pts: Array):
    x1,y1 = pts[0]
    x2,y2 = pts[-1]
    errs = []
    for i in range(1, pts.shape[0]- 1):
        x0,y0 = pts[i]
        dist = abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1) / math.sqrt((y2-y1)**2+(x2-x1)**2)
        errs.append(dist)
    errs = np.array(errs)

    return errs.mean(), errs.max()

def lineQuality_metric1(pts: Array):
    assert len(pts.shape) == 2 and pts.shape[1] == 2
    origin, direction = fitLine(pts)
    errs = np.cross(pts - origin, direction) ** 2
    return errs

def fitLine(pts: Array):
    """
    pts - ndarray of shape [N, 2] - points coords
    returns - tuple (origin, delta) - ndarrays of shape (2)
    """
    assert len(pts.shape) == 2 and pts.shape[1] == 2
    mid = pts.mean(axis=0)
    cov = np.cov(pts - pts.mean(axis=0), rowvar=False)
    _, eig_vecs = scipy.linalg.eigh(cov, eigvals=(1, 1))

    return pts.mean(axis=0), eig_vecs[:, 0] / np.linalg.norm(eig_vecs[:, 0])

def metric2(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    
    mean, max_ = allLinesQuality_metric2(lines, n_lines_vertical, n_lines_horizontal)
    return np.array([mean, max_])

def metric_from_markup(metric, pts_x, pts_y, n_lines_vertical: int, n_lines_horizontal: int):
    lines = lines_from_markup(pts_x, pts_y, n_lines_vertical, n_lines_horizontal)

    return metric(np.array(lines), n_lines_vertical, n_lines_horizontal)

def metric_from_img(metric, img, n_lines_vertical: int, n_lines_horizontal: int):
    dots, lines = lines_from_image(img, n_lines_vertical, n_lines_horizontal)
    if dots is None or lines is None:
        return None
 
    return metric(np.array(lines), n_lines_vertical, n_lines_horizontal)

def M1(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    return np.array(metric1(lines, n_lines_vertical, n_lines_horizontal)[:, 0]).mean()

def M2(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    return np.array(metric1(lines, n_lines_vertical, n_lines_horizontal)[:, 1]).max()

def M3(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    return np.array(metric1(lines, n_lines_vertical, n_lines_horizontal)[:, 0]).mean()

def M4(lines: Array, n_lines_vertical: int, n_lines_horizontal: int):
    return np.array(metric1(lines, n_lines_vertical, n_lines_horizontal)[:, 1]).max()

def M1(metric1_values):
    return np.array(metric1_values[:, 0]).mean()

def M2(metric1_values):
    return np.array(metric1_values[:, 1]).max()

def M3(metric2_values):
    return np.array(metric2_values[:, 0]).mean()

def M4(metric2_values):
    return np.array(metric2_values[:, 1]).mean()
