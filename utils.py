import os

def get_all_file_paths(directory_path):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths

