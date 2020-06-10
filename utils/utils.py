# -*- coding: utf-8 -*-
# @Time    : 2020/3/27 16:03
# @Author  : xuyiqing
# @File    : utils.py
import os
import time
import datetime


def iter_file_paths(path, size):
    # 生成路径
    file_infos = []
    for file in os.listdir(path):
        file_infos.append(dict(
            file_name=''.join(file.split('.')[:-1]),
            file_path=os.path.join(path, file)
        ))
        if all([file_infos, len(file_infos) % size == 0]):
            yield file_infos
            file_infos = []
    if file_infos:
        yield file_infos


def from_unix_timestamp(unix_ts):
    # 时间戳转普通时间
    normal_time = datetime.datetime.fromtimestamp(unix_ts)
    return normal_time


def to_unix_timestamp(normal_time):
    # 普通时间转时间戳
    unix_ts = time.mktime(normal_time.timetuple())
    return unix_ts
