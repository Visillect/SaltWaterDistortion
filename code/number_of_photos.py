import argparse
import glob
import itertools
import json
import os
import os.path as osp
import random

import numpy as np
from tqdm import tqdm

from uw_distortion_utils.calib_classical import calib_classical
from uw_distortion_utils.metrics import (M1, M2, M3, M4, metric1, metric2,
                                   metric_from_markup)
from uw_distortion_utils.undistortion import find_map

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run experiment')
    parser.add_argument(
        '--input_central', '-ic', type=str, required=True,
        help='Path to input dir with "central" photos.')
    parser.add_argument(
        '--executable_file', '-e', type=str, required=True,
        help='Path to executable file')
    parser.add_argument(
        '--output', '-o', default=os.getcwd(), type=str,
        help='Path to output dir. Default=cwd')
    parser.add_argument(
        '--input_border', '-ib', type=str, required=True,
        help='Path to input dir with "border" photos.')
    parser.add_argument(
        '--camera', '-c', default='main', type=str,
        help='Camera name. Default=main')
    parser.add_argument(
        '--json_path', '-j', default=os.getcwd(), type=str,
        help='Path to folder with json markup files.')
    parser.add_argument(
        '--calib_photos_path', '-cp', default=os.getcwd(), type=str,
        help='Path to calib_photos folder')    
    parser.add_argument(
        '--yml', '-y', type=str, required=True,
        help='Path to yml with cam params')  
    parser.add_argument(
        '--cols', default=9, type=int,
        help='Number of vertical lines. Default=9')
    parser.add_argument(
        '--rows', default=6, type=int,
        help='Number of horizontal lines. Default=6') 
    parser.add_argument(
        '--square_size', default=0.013, type=float,
        help='The size of the board square. Default=0.013')
    args = parser.parse_args()
    
    executable_base_path = args.executable_file

    calib_params = ['-c', str(args.cols),
                    '-r', str(args.rows),
                    '-s', str(args.square_size),
                    '--aw']

    imagelist_central = sorted(glob.glob(args.input_central+'/*.jpg'))
    imagelist_border = sorted(glob.glob(args.input_border+'/*.jpg'))
    mono_output_path = osp.join(args.output, 'mono')
    if not osp.exists(mono_output_path):
        os.mkdir(mono_output_path)

    M = []
    for nb, nc in itertools.product(range(len(imagelist_border)), range(len(imagelist_central))):
            if nb == 0 and nc == 0:
                continue

            M1_curr = []
            M2_curr = []
            M3_curr = []
            M4_curr = []
            for i in tqdm(range(10)):
                imagelist = []
                imagelist_central = sorted(glob.glob(args.input_central+'/*.jpg'))
                imagelist_border = sorted(glob.glob(args.input_border+'/*.jpg'))
                if nb != 0:
                    for i in range(nb):
                        imagelist.append(imagelist_border.pop(random.randint(0, len(imagelist_border) -1))) 
                if nc != 0:
                    for i in range(nc):
                        imagelist.append(imagelist_central.pop(random.randint(0, len(imagelist_central) -1))) 

                calib_classical(executable_base_path, calib_params, mono_output_path, imagelist, args.camera+".yml")  
                
                with open(osp.join(mono_output_path, args.camera+".yml"), "r") as f:
                    calib_coeffs = json.load(f)
                
                camera_matrix_water = np.array(calib_coeffs["camera_matrix"]["data"], dtype=np.float64, copy=True).reshape(
                        (calib_coeffs["camera_matrix"]["cols"], calib_coeffs["camera_matrix"]["rows"])
                    )
                dist_coeffs_water = np.array(calib_coeffs["distortion_coefficients"]["data"], dtype=np.float64, copy=True).reshape(
                                        (calib_coeffs["distortion_coefficients"]["cols"], calib_coeffs["distortion_coefficients"]["rows"])
                                    )

                metric_1 = []
                metric_2 = []
                jsonlist = np.array(sorted(glob.glob(args.json_path+'/*.jpg.json')))
                for path_json in tqdm(list(jsonlist)):
                    with open(path_json, "r") as f:
                        data = json.load(f)

                    x_mark_tmp = {}
                    y_mark_tmp = {}
                    point_tag = data["objects"]
                    for p in point_tag:
                        x_mark_tmp.update({int(p["tags"][0]) : p["data"][0]})
                        y_mark_tmp.update({int(p["tags"][0]) : p["data"][1]})
                    x_mark_tmp_water, y_mark_tmp_water = find_map(x_mark_tmp, y_mark_tmp, dist_coeffs_water, camera_matrix_water)

                    metric_1.append(metric_from_markup(metric1, x_mark_tmp_water, y_mark_tmp_water, args.cols, args.rows))
                    metric_2.append(metric_from_markup(metric2, x_mark_tmp_water, y_mark_tmp_water, args.cols, args.rows))

                metric_1 = np.array(metric_1)
                metric_2 = np.array(metric_2)

                M1_curr.append(M1(metric_1))
                M2_curr.append(M2(metric_1))
                M3_curr.append(M3(metric_2))
                M4_curr.append(M4(metric_2))

            M.append(
                {"n_border" : nb, 
                "n_central" : nc, 
                "mean M1" : round(np.array(M1_curr).mean(),4),
                "mean M2" : round(np.array(M2_curr).mean(),4), 
                "mean M3" : round(np.array(M3_curr).mean(),4), 
                "mean M4" : round(np.array(M4_curr).mean(),4)
                }
            )

    with open(osp.join(args.output,"res.txt"), 'a') as fw:
        json.dump(M, fw)

    


