#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : xuyiqing
# @Time    : 2019/8/3 10:19
# @File    : ThreadDownload.py
from threading import Thread


class ThreadDownload(Thread):
    """
    多线程
    """
    def __init__(self, func, queue, *args, **kwargs):
        super(ThreadDownload, self).__init__(*args, **kwargs)
        self.func = func
        self.queue = queue
        self.kwargs = kwargs.get("kwargs")

    def run(self):
        while True:
            if self.queue.empty():
                break
            data = self.queue.get()
            try:
                if self.kwargs:
                    self.func(data, self.kwargs)
                else:
                    self.func(data)
            finally:
                self.queue.task_done()

