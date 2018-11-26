#! /usr/bin/python3

import sys
import os
import subprocess
import time
import dlct


def process_files_in_one_folder(leaf_script_path, root_input_folder_path, source_folder_path, names_of_source_files, output_folder_path, n_submitted) :
    # Scan the source files, spawn a job for any without a target file,
    # or that are newer than the target file.
    print("In subfolder %s, found %d files" % (source_folder_path, len(names_of_source_files)))
    has_been_run_on_one_file_in_this_folder = False
    for source_file_name in names_of_source_files:
        if ( dlct.does_match_extension(source_file_name, ".avi") or
             dlct.does_match_extension(source_file_name, ".mp4") or
             dlct.does_match_extension(source_file_name, ".mov") ):
            source_file_path = os.path.join(source_folder_path, source_file_name)
            lock_file_path = os.path.join(output_folder_path, source_file_name + ".lock")
            target_file_path = os.path.join(output_folder_path, dlct.replace_extension(source_file_name, ".mp4"))
            if os.path.exists(target_file_path) :
                if os.path.isdir(target_file_path) :
                    # An object exists at the target path, but (oddly) it's a folder
                    print("An object exists at target location %s, but it's a folder.  Not submitting a job." % target_file_path)
                    do_it = False
                else :
                    if os.path.isfile(target_file_path) :
                        # run the script only if the source is more recent than the target
                        # and also if the the source has not been modified in the waiting period
                        # This last is to prevent files that are currently being written from being analyzed.
                        waiting_period = 300  # seconds
                        current_time = time.time()
                        source_modification_time = os.path.getmtime(source_file_path)
                        target_modification_time = os.path.getmtime(target_file_path) 
                        print("current time: %s" % current_time)
                        print("source mod time: %s" % source_modification_time)
                        print("target mod time: %s" % target_modification_time)                      
                        do_it = ( ( source_modification_time >= target_modification_time ) and 
                                  ( current_time > source_modification_time + waiting_period ) )
                    else :
                        # The file exists, but is neither a file or a folder.  WTF?
                        print("An object exists at target location %s, but it's neither a file nor a folder.  Not submitting a job." 
                              % target_file_path)
                        do_it = False
            else :
                # target file does not exist
                do_it = True

            do_it_for_reals = do_it and not os.path.exists(lock_file_path)
            if do_it_for_reals :    
                if not has_been_run_on_one_file_in_this_folder :
                    os.makedirs(output_folder_path, exist_ok=True)
                    has_been_run_on_one_file = True            
                    subprocess.call(['/usr/bin/touch', lock_file_path])
                    stdout_file_path = os.path.join(output_folder_path, dlct.replace_extension(source_file_name, '-stdout.txt'))
                    stderr_file_path = os.path.join(output_folder_path, dlct.replace_extension(source_file_name, '-stderr.txt'))
                    print("stdout_file_path: %s" % stdout_file_path)
                    print("stderr_file_path: %s" % stderr_file_path)
                    print("root_input_folder_path: %s" % root_input_folder_path)
                    print("source_file_path: %s" % source_file_path)
                    print("lock_file_path: %s"   % lock_file_path)
                    print("target_file_path: %s" % target_file_path)
                    print("PATH: %s" % os.environ['PATH'])
                    print("PWD: %s" % os.environ['PWD'])
                    command_list = ['bsub', '-o', stdout_file_path, '-e', stderr_file_path, 
                                    'python3', leaf_script_path, root_input_folder_path, source_file_path, lock_file_path, target_file_path]
                    print('About to subprocess.call(): %s' % repr(command_list))
                    return_code = subprocess.call(command_list)
                    if return_code == 0 :
                        n_submitted = n_submitted + 1
                    else :
                        print('bsub call failed!')
                        try :
                            if os.path.exists(lock_file_path) :
                                os.remove(lock_file_path)
                        except Exception as e :
                            print('...and unable to delete lock file %s for some reason' % lock_file_path)                            

    # return the updated count of copied files
    return n_submitted
# end of function


def process_folder(leaf_script_path, root_input_folder_path, input_folder_path, output_folder_path, n_submitted) :
    # print something to show progress
    print("Processing subfolder: %s" % input_folder_path)

    # get a list of all files and dirs in the source, dest dirs
    try:
        input_folder_contents = os.listdir(input_folder_path)
    except FileNotFoundError :
        # if we can't list the dir, warn but continue
        print("Warning: Folder %s doesn't seem to exist" % input_folder_path)
        return n_submitted
    except PermissionError :
        # if we can't list the dir, warn but continue
        print("Warning: can't list contents of folder %s due to permissions error" % input_folder_path)
        return n_submitted

    # separate the subfolders from the files
    names_of_subfolders = [item 
                           for item 
                           in input_folder_contents 
                           if os.path.isdir(os.path.join(input_folder_path, item))]
    names_of_files = [item 
                      for item 
                      in input_folder_contents 
                      if os.path.isfile(os.path.join(input_folder_path, item))]

    # Process the files in this folder
    n_submitted = process_files_in_one_folder(leaf_script_path,
                                              root_input_folder_path,
                                              input_folder_path, 
                                              names_of_files, 
                                              output_folder_path, 
                                              n_submitted)
        
    # For each folder in names_of_subfolders, recurse
    for subfolder_name in names_of_subfolders:
        n_submitted = process_folder(leaf_script_path,
                                     root_input_folder_path,
                                     os.path.join(input_folder_path, subfolder_name),
                                     os.path.join(output_folder_path, subfolder_name),
                                     n_submitted)
                    
    # return the updated count of copied files
    return n_submitted
# end of function   


#
# main
#
if __name__ == "__main__":
    this_script_path = os.path.realpath(__file__)
    this_folder_path = os.path.dirname(this_script_path)
    leaf_script_path = os.path.join(this_folder_path, 'compress_video_and_delete_input_file.py')

    root_input_folder_path = os.path.abspath(sys.argv[1])
    root_output_folder_path = os.path.abspath(sys.argv[2])
    n_submitted = 0
    n_submitted = process_folder(leaf_script_path, 
                                 root_input_folder_path, 
                                 root_input_folder_path, 
                                 root_output_folder_path,
                                 n_submitted)
    print("%d jobs submitted total" % n_submitted)
