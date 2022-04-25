import argparse
import json
from pathlib import Path

import numpy as np
from tqdm import tqdm

from uw_distortion_utils.metrics import (M1, M2, M3, M4, metric1, metric2,
                                   metric_from_markup)
from uw_distortion_utils.undistortion import find_map, undistort_formula2

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run different salnity')
    parser.add_argument(
        '--json_path', '-j',required=True, type=Path,
        help='Path to json folder')
    parser.add_argument(
        '--cols', default=9, type=int,
        help='Number of vertical lines. Default=9')
    parser.add_argument(
        '--rows', default=6, type=int,
        help='Number of horizontal lines. Default=6')
    parser.add_argument(
        '--air_calib_coeffs_path', '-c', required=True, type=Path,
        help='Path to .yaml or .yml file with camera parameters in the air.')
       
    args = parser.parse_args()

    jsonlist = sorted(args.json_path.glob('*.json'))

    with open(args.air_calib_coeffs_path, "r") as f:
        air_cam_data = json.load(f)
    
    camera_matrix_air = np.array(air_cam_data["camera_matrix"]["data"], dtype=np.float64, copy=True).reshape(
                            (air_cam_data["camera_matrix"]["cols"], air_cam_data["camera_matrix"]["rows"])
                        )

    dist_coeffs_air = np.array(air_cam_data["distortion_coefficients"]["data"], dtype=np.float64, copy=True).reshape(
                            (air_cam_data["distortion_coefficients"]["cols"], air_cam_data["distortion_coefficients"]["rows"])
                        )

    refr_index = np.linspace(1.33, 1.4, 8)
    for n in refr_index:
        metric_1 = []
        metric_2 = []
        for path_json in tqdm(jsonlist):
            with open(path_json, "r") as f:
                data = json.load(f)

            x_mark_tmp = {}
            y_mark_tmp = {}
            point_tag = data["objects"]
            for p in point_tag:
                x_mark_tmp.update({int(p["tags"][0]) : p["data"][0]})
                y_mark_tmp.update({int(p["tags"][0]) : p["data"][1]})

            x_mark_tmp_air, y_mark_tmp_air = find_map(x_mark_tmp, y_mark_tmp, dist_coeffs_air, camera_matrix_air)
            x_mark_tmp_k, y_mark_tmp_k = undistort_formula2(x_mark_tmp_air, y_mark_tmp_air, n, camera_matrix_air)

            metric_1.append(metric_from_markup(metric1, x_mark_tmp_k, y_mark_tmp_k, args.cols, args.rows))
            metric_2.append(metric_from_markup(metric2, x_mark_tmp_k, y_mark_tmp_k, args.cols, args.rows))
        
        metric_1 = np.array(metric_1)
        metric_2 = np.array(metric_2)

        print ("Using refraction index n = " + str(n) + ": ")
        print ("M1 :", M1(metric_1))
        print ("M2 :", M2(metric_1))
        print ("M3 :", M3(metric_2))
        print ("M4 :", M4(metric_2))

    



