import argparse
import glob
import json
import math
import os.path as osp

import imageio as io
import numpy as np
from tqdm import tqdm

from uw_distortion_utils.lines import lines_from_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run detector error')
    parser.add_argument(
        '--input', '-i', type=str, required=True,
        help='Path to input dir')
    parser.add_argument(
        '--cols', default=9, type=int,
        help='Number of vertical lines. Default=9')
    parser.add_argument(
        '--rows', default=6, type=int,
        help='Number of horizontal lines. Default=6')
   
    args = parser.parse_args()

    imagelist = np.array(sorted(glob.glob(args.input+'/photo/*.jpg')))
    json_path = args.input+'/markup'

    x_opencv = []
    y_opencv = []

    diff = []
    max_ = []
    for path_img in tqdm(list(imagelist)):
        uw_d_ = io.imread(path_img)
        _, lines_opencv = lines_from_image(uw_d_, args.cols, args.rows)
        if lines_opencv is not None:
            x_opencv_tmp = {}
            y_opencv_tmp = {}
            pt_number = 0
            for i in range(args.rows):
                for j in range(args.cols):
                    x_opencv_tmp.update({pt_number : lines_opencv[i][j][0]})
                    y_opencv_tmp.update({pt_number : lines_opencv[i][j][1]})
                    pt_number += 1
            if osp.exists(osp.join(json_path, osp.basename(path_img+'.json'))):
                with open(osp.join(json_path, osp.basename(path_img+'.json')), "r") as f:
                    data = json.load(f)

                x_mark_tmp = {}
                y_mark_tmp = {}
                point_tag = data["objects"]
                for p in point_tag:
                    x_mark_tmp.update({int(p["tags"][0]) : p["data"][0]})
                    y_mark_tmp.update({int(p["tags"][0]) : p["data"][1]})

                err = 0.0
                max_tmp = 0
                for j in range(args.cols*args.rows):
                    x_o = x_opencv_tmp.get(j)
                    y_o = y_opencv_tmp.get(j)
                    min_err = 1000
                    k_tmp = -1
                    for k, y_m_tmp in y_mark_tmp.items():
                        x_m_tmp = x_mark_tmp.get(k)
                        if (min_err > math.sqrt((x_o - x_m_tmp) ** 2 + (y_o - y_m_tmp) ** 2)):
                            min_err = math.sqrt((x_o - x_m_tmp) ** 2 + (y_o - y_m_tmp) ** 2)
                            y_m = y_m_tmp
                            x_m = x_m_tmp
                            k_tmp = k

                    err += math.sqrt((x_o - x_m) ** 2 + (y_o - y_m) ** 2)
                    if (max_tmp < math.sqrt((x_o - x_m) ** 2 + (y_o - y_m) ** 2)):
                        max_tmp = math.sqrt((x_o - x_m) ** 2 + (y_o - y_m) ** 2)
        
                max_.append(max_tmp)
                err = err / float(args.cols*args.rows)

                diff.append(err)
            
    
    print ("mean:", np.array(diff).mean())
    print ("max mean:", np.array(diff).max())
    print ("max:", np.array(max_).max())
    print ("mean max:", np.array(max_).mean())



