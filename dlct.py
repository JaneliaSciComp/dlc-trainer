#! /usr/bin/python3

import sys
import os
import tempfile
import shutil
#import pwd
import getpass
#import matplotlib.pyplot as plt
import subprocess
import pathlib


def get_username():
    #return pwd.getpwuid(os.getuid())[0]
    return getpass.getuser()

def determine_scratch_folder_path():
    # If a /scratch folder exists, use that.  Otherwise, use /tmp.
    username = get_username()
    my_scratch_folder_path = '/scratch/%s' % username
    if os.path.isdir(my_scratch_folder_path) :
        return my_scratch_folder_path
    else:
        #return '/tmp'
        return tempfile.gettempdir()

def is_empty(list) :
    return len(list)==0

def file_name_without_extension_from_path(path):
    file_name = os.path.basename(path)
    return os.path.splitext(file_name)[0]

def does_match_extension(file_name, target_extension) :
    # target_extension should include the dot
    extension = os.path.splitext(file_name)[1]
    return (extension == target_extension)

def find_files_matching_extension(output_folder_path, output_file_extension):
    # get a list of all files and folders in the output_folder_path
    try:
        names_of_files_and_subfolders = os.listdir(output_folder_path)
    except FileNotFoundError:
        # if we can't list the dir, warn but continue
        raise RuntimeError("Warning: Folder %s doesn't seem to exist" % output_folder_path)
    except PermissionError:
        # if we can't list the dir, warn but continue
        raise RuntimeError("Warning: can't list contents of folder %s due to permissions error" % output_folder_path)

    names_of_files = list(filter((lambda item_name: os.path.isfile(os.path.join(output_folder_path, item_name))),
                                 names_of_files_and_subfolders))
    names_of_matching_files = list(filter((lambda file_name: does_match_extension(file_name, output_file_extension)),
                                          names_of_files))
    return names_of_matching_files

def replace_extension(file_path, new_extension) :
    # new_extension should include the dot
    return os.path.splitext(file_path)[0] + new_extension

class add_path:
    def __init__(self, path):
        self.original_sys_path = sys.path.copy()
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.path = self.original_sys_path.copy()

def load_configuration_file(file_path):
    my_globals = {}
    my_globals.update({
        "__file__": file_path,
        "__name__": "__main__",
    })
    my_locals = {}
    file_path = os.path.abspath(file_path)
    parent_folder_path = os.path.dirname(file_path)
    with add_path(parent_folder_path):
        with open(file_path, 'rt') as file:
            exec(compile(file.read(), file_path, 'exec'), my_globals, my_locals)
    return my_locals

def system(command_as_list):
    process = subprocess.Popen(command_as_list,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # wait for the process to terminate
    out, err = process.communicate()
    errcode = process.returncode
    return (errcode, out.decode(), err.decode())

def common_prefix_path(path1_as_string, path2_as_string) :
    # Re-implement os.path.commonpath(), b/c Python 3.4 doesn't have it.
    path1_as_tuple = pathlib.Path(path1_as_string).parts
    path2_as_tuple = pathlib.Path(path2_as_string).parts
    n1 = len(path1_as_tuple)
    n2 = len(path2_as_tuple)
    max_n = min(n1, n2)
    n = max_n  # fallback number of common elements if all elements turn out to be equal
    for i in range(max_n) :
        if path1_as_tuple[i] != path2_as_tuple[i] :
            n = i
            break
    result_as_tuple = path1_as_tuple[:n]
    result_as_string = os.path.join(*result_as_tuple)
    return result_as_string
