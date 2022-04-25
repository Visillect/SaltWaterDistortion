import numpy as np


def parse_pinhole_camera_matrix(C):
    wild = -1
    template = np.array([
        [wild,     0, wild],
        [   0,  wild, wild],
        [   0,     0,    1],
    ])
    assert C.shape == template.shape and (np.isclose(C, template) | (template == wild)).all(),\
            "Camera matrix should have kind [[fx, 0, x0], [0, fy, y0], [0, 0, 1]]"

    ((fx,  _, x0),
     ( _, fy, y0),
     ( _,  _,  _)) = C

    return fx, fy, x0, y0


def undistort_classical(point, c, f, k):
    x = float(point[0] - c[0]) / f[0]
    y = float(point[1] - c[1]) / f[1]

    r2 = x**2 + y**2
    r2_new = r2 * ((1 + k[0] * r2 + k[1] * r2 * r2 + k[4] * r2 * r2 * r2) / (1 + k[5] * r2 + k[6] * r2 * r2 + k[7] * r2 * r2 * r2))**2
    r2 = r2_new

    xDistort = x * (1 + k[5] * r2 + k[6] * r2 * r2 + k[7] * r2 * r2 * r2) / (1 + k[0] * r2 + k[1] * r2 * r2 + k[4] * r2 * r2 * r2) 
    yDistort = y * (1 + k[5] * r2 + k[6] * r2 * r2 + k[7] * r2 * r2 * r2) / (1 + k[0] * r2 + k[1] * r2 * r2 + k[4] * r2 * r2 * r2) 

    xDistort = xDistort * f[0] + c[0]
    yDistort = yDistort * f[1] + c[1]
    
    return np.array([float(xDistort), float(yDistort)])

def find_map(dots_x, dots_y, k, cam):
    new_dots_x = {}
    new_dots_y = {}
    c = np.array([cam[0,2], cam[1,2]])
    f = np.array([cam[0,0], cam[1,1]])

    for number, x in dots_x.items():
        point = np.array([x, dots_y.get(number)])
        best_point = undistort_classical(point, c, f, k)
        new_dots_x.update({number : best_point[0]})
        new_dots_y.update({number : best_point[1]})

    return new_dots_x, new_dots_y

def undistort_formula2(dots_x, dots_y, n, cam_matrix):
    """
    Undistort pixels coordinates using formula (2)

    xy - ndarray of shape (..., 2), where xy[..., 0] - x-coordinates and xy[..., 1] - y-coordinates
    n - refraction index
    camera_matrix - pinhole camera parameters matrix of kind [[fx 0 x0] [0 fy y0] [0 0 1]]
    """
    fx, fy, x0, y0 = parse_pinhole_camera_matrix(cam_matrix)
    new_dots_x = {}
    new_dots_y = {}
    for number, x in dots_x.items():
        y = dots_y.get(number)
        x_ = (x - x0) / fx
        y_ = (y - y0) / fy

        r2 = x_** 2 + y_** 2
        k = 1 / np.sqrt(n**2 + (n**2 - 1) * r2)
        
        new_dots_x.update({number : k*x_ * fx + x0})
        new_dots_y.update({number : k*y_ * fy + y0})

    return new_dots_x, new_dots_y
