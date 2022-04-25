import argparse
import glob
import os
import os.path as osp

import imageio as io
import numpy as np
from sklearn.model_selection import KFold

from uw_distortion_utils.calib_classical import (calib_classical,
                                           rectify_imgs_classical)
from uw_distortion_utils.metrics import metric1, metric_from_img

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Run cross validation')
    parser.add_argument(
        '--input', '-i', type=str, required=True,
        help='Path to input dir')
    parser.add_argument(
        '--executable_file', '-e', type=str, required=True,
        help='Path to executable file')
    parser.add_argument(
        '--output', '-o', default=os.getcwd(), type=str,
        help='Path to output dir. Default=cwd')
    parser.add_argument(
        '--camera', '-c', default='main', type=str,
        help='Camera name. Default=main')
    parser.add_argument(
        '--number_of_folds', '-n', default=4, type=int,
        help='Number of folds. Default=4')
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
    project_path = args.executable_file
    executable_base_path = project_path

    calib_params = ['-c', str(args.cols),
                    '-r', str(args.rows),
                    '-s', str(args.square_size),
                    '--aw']

    imagelist = np.array(sorted(glob.glob(args.input+'/*.jpg')))

    delayedimages = imagelist[:10]
    imagelist = np.array(imagelist[10:])

    output_path = osp.join(args.output, 'calib_params/')
    if not osp.exists(output_path):
        os.mkdir(output_path)

    kf = KFold(n_splits=args.number_of_folds)
    kf.get_n_splits(imagelist)

    foldnumber = 1
    for train_index, test_index in kf.split(imagelist):
        train = imagelist[train_index]
        test = imagelist[test_index]


        output_path_fold = osp.join(output_path, 'fold_' + str(foldnumber) + '/')
        if not osp.exists(output_path_fold):
            os.mkdir(output_path_fold)

        # calibrate camera
        if args.camera == 'main':
            params_file_name = 'main.yml'
        if args.camera == 'wide':
            params_file_name = 'wide.yml'

        calib_classical(executable_base_path, calib_params, output_path_fold, train, params_file_name)

        output_path_fold_rect = osp.join(output_path_fold, 'rectified/')
        if not osp.exists(output_path_fold_rect):
            os.mkdir(output_path_fold_rect)
            
        # rectificate camera validation
        rectify_imgs_classical(executable_base_path, output_path_fold, output_path_fold_rect, test, params_file_name)

        output_path_fold_rect_del = osp.join(output_path_fold, 'rectified_delayed/')
        if not osp.exists(output_path_fold_rect_del):
            os.mkdir(output_path_fold_rect_del)

        # rectificate camera delayed
        rectify_imgs_classical(executable_base_path, output_path_fold, output_path_fold_rect_del, delayedimages, params_file_name)

        imagelist_rect = sorted(glob.glob(osp.join(output_path_fold_rect + '/*.jpg')))
        imagelist_rect_del = sorted(glob.glob(osp.join(output_path_fold_rect_del + '/*.jpg')))

        quals = []
        quals_del = []

        for path in imagelist_rect:
            uw_ = io.imread(path)
            q = metric_from_img(metric1, uw_, args.cols, args.rows)
            if q is not None:
                quals.append(q)

        for path in imagelist_rect_del:
            uw_ = io.imread(path)
            q = metric_from_img(metric1, uw_, args.cols, args.rows)
            if q is not None:
                quals_del.append(q)

        quals = np.array(quals)
        quals_del = np.array(quals_del)
        if len(quals) > 0:
            print("fold No " + str(foldnumber) + f": mean sqrmean: {quals[:, 0].mean():.3f}, mean max: {quals[:, 1].mean():.3f}, count: {len(quals)}")
        else:
            print("fold No " + str(foldnumber) + f": count: {len(quals)}")

        if len(quals_del) > 0:
            print("fold No " + str(foldnumber) + f": mean sqrmean (delayed): {quals_del[:, 0].mean():.3f}, mean max (delayed): {quals_del[:, 1].mean():.3f}, count: {len(quals_del)}")
        else:
            print("fold No " + str(foldnumber) + f": count: {len(quals_del)}")

        foldnumber += 1
