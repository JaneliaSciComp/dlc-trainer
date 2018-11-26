#! /usr/bin/python3

import sys
import os
import tempfile
import dlct
#import shutil
import pathlib
from compress_video import compress_video


# def frame_rate_as_rational_string_from_video_file_name(video_file_name) :
#     # Use ffprobe to get the LCM frame rate of a video.
#     # These LCM frame rates seem to be better preserved than the average frame rate.
#     command = ['ffprobe', '-v', '0', '-of', 'csv=p=0', '-select_streams', '0', '-show_entries', 'stream=r_frame_rate', video_file_name]
#     (return_code, stdout_as_string, stderr_as_string) = dlct.system(command)
#     if return_code != 0:
#         raise RuntimeError(
#             'There was a problem running ffprobe to determine the frame rate of %s, return code %d:\n\nstdout: %s\n\nstderr: %s\n' % (
#                 video_file_name, return_code, stdout_as_string, stderr_as_string))
#     return stdout_as_string.strip()  # should be a string that looks like a rational number, e.g. '1/1', '30000/1001'


def delete_input_file_and_empty_ancestral_folders(input_file_path_as_string, root_input_folder_path_as_string) :
    input_file_path = pathlib.Path(input_file_path_as_string)
    root_input_folder_path = pathlib.Path(root_input_folder_path_as_string)

    # Remove the input file itself
    try :
        os.remove(str(input_file_path))
    except Exception as e :
        print('Tried to delete input file %s, but was unable to do so because:' % str(input_file_path))
        print(e)
        return        
    
    # We want to remove that contained the input file, if it is now
    # empty.  And we want to do this recursively up the containing
    # super-folders, until we reach the root input folder, which we do
    # *not* want to delete

    # Check that the input file was actually inside the root input folder before we do this
    common_path = pathlib.Path(dlct.common_prefix_path(str(root_input_folder_path), str(input_file_path)))
    if common_path != root_input_folder_path :
        print('Internal error: When checking for empty input folders, the single network path (%s) is not the common path for it and the input file path (%s)' %
              (str(root_input_folder_path), 
               str(input_file_path)))
        return

    # Delete the parent of the input file if it's now empty, and then
    # recurse up the containing folders, stopping at the root input
    # folder.
    target_folder_path = input_file_path.parent
    is_done = ( target_folder_path == root_input_folder_path )
    while not is_done :
        contents = os.listdir(str(target_folder_path)) 
        if dlct.is_empty(contents) :
            try :
                os.rmdir(str(target_folder_path)) 
            except Exception as e :
                print('Tried to delete folder %s, but was unable to do so for some reason' % str(target_folder_path))
                return    
            target_folder_path = target_folder_path.parent
            is_done = ( target_folder_path == root_input_folder_path )
        else :
            is_done = True 
# end of function


def compress_video_and_delete_input_file(root_input_video_path, 
                                         input_video_path,
                                         lock_file_path,
                                         output_video_path):
    try:
        compress_video(input_video_path, output_video_path)
    except Exception as e:
        # Remove the lock file
        if os.path.exists(lock_file_path) :
            os.remove(lock_file_path)
        raise e
    # Remove the lock file
    if os.path.exists(lock_file_path) :
        os.remove(lock_file_path)
    delete_input_file_and_empty_ancestral_folders(input_video_path, root_input_video_path)

#
# main
#

if __name__ == "__main__" :
    # Get the arguments
    root_input_video_path = os.path.abspath(sys.argv[1])
    input_video_path = os.path.abspath(sys.argv[2])
    lock_file_path = os.path.abspath(sys.argv[3])
    output_video_path = os.path.abspath(sys.argv[4])
    compress_video_and_delete_input_file(root_input_video_path,
                                         input_video_path,
                                         lock_file_path,
                                         output_video_path)

