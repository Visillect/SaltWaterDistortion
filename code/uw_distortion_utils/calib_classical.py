import os.path as osp
import subprocess
from multiprocessing import Pool


def calib_classical(executable_base_path, calib_params, mono_output_path, imagelist, file_name = "main.yml"):
    cmd_calib_mono_left = [osp.join(executable_base_path, 'calib_mono')] + \
                            calib_params + ['--nr'] + \
                            ['-o', osp.join(mono_output_path, file_name)] + \
                            [imagelist[i] for i in range(len(imagelist))]
                            
    pool = Pool(processes=1)
    pool.map(subprocess.check_call, [cmd_calib_mono_left])
    pool.close()
    pool.join()

def rectify_imgs_classical(executable_base_path, input_params_path, output_path, imagelist, file_name = "main.yml"):
    cmd_rect = [osp.join(executable_base_path, 'rectify_images')] + \
                    ['-c', osp.join(input_params_path, file_name)] + \
                    ['-o', output_path] + \
                    [imagelist[i] for i in range(len(imagelist))]      

    pool = Pool(processes=1)
    pool.map(subprocess.check_call, [cmd_rect])
    pool.close()
