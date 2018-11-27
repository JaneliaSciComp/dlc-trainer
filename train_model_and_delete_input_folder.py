#! /usr/bin/python3

import sys
import os
import shutil
#import pathlib
#import delectable.dlct as dlct
from delectable.train_model import train_model


def train_model_and_delete_input_folder(targets_folder_path,
                                        lock_file_path,
                                        model_folder_path):
    try:
        train_model(targets_folder_path, model_folder_path)
    except Exception as e:
        # Remove the lock file
        if os.path.exists(lock_file_path) :
            os.remove(lock_file_path)
        raise e

    # Remove the lock file
    if os.path.exists(lock_file_path) :
        os.remove(lock_file_path)

    # Remove the targets folder
    if os.path.exists(targets_folder_path) :
        shutil.rmtree(targets_folder_path)


#
# main
#
if __name__ == "__main__" :
    # Get the arguments
    targets_folder_path = os.path.abspath(sys.argv[1])
    lock_file_path = os.path.abspath(sys.argv[2])
    model_folder_path = os.path.abspath(sys.argv[3])
    train_model_and_delete_input_folder(targets_folder_path,
                                        lock_file_path,
                                        model_folder_path)
