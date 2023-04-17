import imageio.v3 as iio
import numpy as np
import os
from pathlib import Path
import subprocess
import re
import cv2
from collections import Counter

PATH_SEP = os.path.sep


def results_to_gif(result_paths, gif_save_path):
    apps_images = Counter()
    apps_start = Counter()
    max_len = 0
    for app, result_path in result_paths:
        video_file_path, analyse_file_path = get_video_and_log_file_path(result_path)
        start, end = get_start_and_end_index(analyse_file_path)
        max_len = max(max_len, end - start)
        images = convert_video_to_images(video_file_path)
        apps_images[app] = images
        apps_start[app] = start

    all_app_images = []
    for key in apps_images.keys():
        start = apps_start[key]
        images = apps_images[key]
        images = [cv2.cvtColor(image, cv2.COLOR_BGR2RGB) for image in images[start - 5: start + max_len + 5]]
        draw_name_to_images(key, images)
        all_app_images.append(images)

    all_app_images = zip(*all_app_images)
    new_img = [np.concatenate(imgs, axis=1) for imgs in all_app_images]
    frames = np.stack(new_img, axis=0)
    iio.imwrite(gif_save_path, frames, duration=40)


def get_video_and_log_file_path(result_path):
    video_path = log_path = ''
    for path in os.listdir(result_path):
        if ".mp4" in path:
            video_path = f'{result_path}{PATH_SEP}{path}'
        elif "analyse.log" in path:
            log_path = f'{result_path}{PATH_SEP}{path}'

    if len(video_path) == 0 or len(log_path) == 0:
        raise ValueError

    return video_path, log_path


def get_start_and_end_index(analyse_file_path):
    with open(analyse_file_path) as file:
        analyse_log = file.read()
        times = re.findall(r'time:[0-9]*?.0ms', analyse_log)

        res = []
        for time in times:
            s = time.find(':')
            e = time.find('.')
            res.append(int(int(time[s + 1:e]) / 40))
    return res


def draw_name_to_images(app_name, images):
    for image in images:
        cv2.putText(image, app_name, (5, 50), cv2.FONT_HERSHEY_COMPLEX, 2, [0, 128, 128], 5)


def convert_video_to_images(video_file_path):
    video_file_path = Path(video_file_path)
    tmp_path = str(video_file_path.parent) + f'{PATH_SEP}frame_tmp'
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)
    else:
        p = subprocess.Popen(f'rm -rf {tmp_path}', shell=True)
        p.communicate()
        os.mkdir(tmp_path)

    cmd = f'ffmpeg -i {str(video_file_path)}  -r 25  ' \
          f'-q:v 2 -f image2  {tmp_path}/%08d.png'
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    p.communicate()
    return [cv2.imread(f'{tmp_path}{PATH_SEP}{image}') for image in sorted(os.listdir(tmp_path))]

if __name__ == '__main__':
    results_to_gif([("QB", "/Users/geralt/Desktop/abc/第三方调用文档打开速度-Word/QB-1397.6"),
                ("Office", "/Users/geralt/Desktop/abc/第三方调用文档打开速度-Word/Office-4672.8"),
                ("WPS", "/Users/geralt/Desktop/abc/第三方调用文档打开速度-Word/WPS-4140")],
               "/Users/geralt/Desktop/abc/第三方调用文档打开速度-Word.gif" )
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
