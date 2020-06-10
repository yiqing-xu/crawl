import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor


def iter_file_paths(path, size):
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


def doc_txt(file_info):
    file_path = file_info['file_path']
    out = subprocess.check_output('antiword {}'.format(file_path), shell=True)
    return out.decode()


def run(path):
    start = time.time()
    data = []
    with ProcessPoolExecutor() as executor:
        for file_infos in iter_file_paths(path=path, size=100):
            futures = [executor.submit(doc_txt, file_info) for file_info in file_infos]
            for future in as_completed(futures):
                error = future.exception()
                data.append(future.result())
                if time.time() - start >= 1:
                    print(len(data))
                    return


if __name__ == '__main__':
    run('/opt/docs/')
