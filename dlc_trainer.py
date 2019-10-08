#! /usr/bin/python3

import sys
import os
import subprocess
import time
import pathlib
import shutil
import delectable
import dlct

def process_targets_folder(singularity_image_path, leaf_script_path, mount_folder_path, targets_folder_path, model_folder_path,
                           n_submitted) :
    # Go training for each targets folder
    print("Going to do training for targets in %s" % targets_folder_path)
    if os.path.exists(model_folder_path) :
        if os.path.isfile(model_folder_path) :
            print("An file exists at output location %s.  Not submitting a job."
                  % model_folder_path)
            do_it = False
        else :
            if os.path.isdir(model_folder_path) :
                # Run the script only if the source is more recent than the target
                # and also if the the source has not been modified in the waiting period.
                # This last is to prevent files that are currently being written from being analyzed.
                waiting_period = 300  # seconds
                current_time = time.time()
                source_modification_time = os.path.getmtime(targets_folder_path)
                target_modification_time = os.path.getmtime(model_folder_path)
                print("current time: %s" % current_time)
                print("source mod time: %s" % source_modification_time)
                print("target mod time: %s" % target_modification_time)                      
                do_it = ( ( source_modification_time >= target_modification_time ) and 
                          ( current_time > source_modification_time + waiting_period ) )
            else :
                # The file exists, but is neither a file or a folder.  WTF?
                print(("An object exists at output location %s, but it's neither a file nor a folder.  " +
                       "Not submitting a job.")
                      % model_folder_path)
                do_it = False
    else :
        # target file does not exist
        do_it = True

    lock_file_path = model_folder_path + ".lock"
    do_it_for_reals = do_it and not os.path.exists(lock_file_path)
    if do_it_for_reals :
        #subprocess.call(['/usr/bin/touch', lock_file_path])
        pathlib.Path(lock_file_path).touch()
        if os.path.exists(model_folder_path) :
            shutil.rmtree(model_folder_path)
        stdout_file_path = model_folder_path + '-training-stdout.txt'
        stderr_file_path = model_folder_path + '-training-stderr.txt'
        print("stdout_file_path: %s" % stdout_file_path)
        print("stderr_file_path: %s" % stderr_file_path)
        #print("root_input_folder_path: %s" % root_input_folder_path)
        print("targets_folder_path: %s" % targets_folder_path)
        print("lock_file_path: %s"   % lock_file_path)
        print("output_folder_path: %s" % model_folder_path)
        print("PATH: %s" % os.environ['PATH'])
        print("PWD: %s" % os.environ['PWD'])
        #bsub -o $2-training-stdout.txt -e $2-training-stderr.txt -q gpu_any -n2 -gpu "num=1" singularity exec -B /scratch --nv $PATH_OF_THIS_SCRIPT_FOLDER/dlc.simg python3 $PATH_OF_THIS_SCRIPT_FOLDER/train_model.py $1 $2
        command_list = ['bsub', '-o', stdout_file_path, '-e', stderr_file_path, 
                        '-q', 'gpu_any', 
                        '-n2', 
                        '-gpu', 'num=1',
                        'singularity', 'exec', 
                        '-B', '/scratch',
                        '-B', mount_folder_path,
                        '--nv', singularity_image_path, 
                        'python3', leaf_script_path, targets_folder_path, lock_file_path, model_folder_path]
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


def process_root_folder(singularity_image_path, leaf_script_path, mount_folder_path, input_folder_path, output_folder_path, n_submitted) :
    # print something to show progress
    print("Processing root folder: %s" % input_folder_path)

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

    # Separate the subfolders from the files
    names_of_subfolders = [item 
                           for item 
                           in input_folder_contents 
                           if os.path.isdir(os.path.join(input_folder_path, item))]
    # names_of_files = [item 
    #                   for item 
    #                   in input_folder_contents 
    #                   if os.path.isfile(os.path.join(input_folder_path, item))]

    # For each folder in names_of_subfolders, recurse
    for subfolder_name in names_of_subfolders:
        n_submitted = process_targets_folder(singularity_image_path, 
                                             leaf_script_path,
                                             mount_folder_path,
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
    singularity_image_path = os.path.join(this_folder_path, 'delectable', 'dlc.simg')
    leaf_script_path = os.path.join(this_folder_path, 'train_model_and_delete_input_folder.py')

    root_input_folder_path = os.path.abspath(sys.argv[1])
    root_output_folder_path = os.path.abspath(sys.argv[2])

    # Get the path to mount explicitly in call to bsub.
    # This heuristic works for several installs, but
    # not clear how well it will generalize in the future...
    # Using commonprefix instead of common path b/c this runs on login one, which is running SL 7,
    # which runs Python 3.4, which doesn't yet support commonpath()
    mount_folder_path = dlct.common_prefix_path(root_input_folder_path, root_output_folder_path)
    print("mount_folder_path: %s" % mount_folder_path)

    n_submitted = 0
    n_submitted = process_root_folder(singularity_image_path,
                                      leaf_script_path,
                                      mount_folder_path,  
                                      root_input_folder_path, 
                                      root_output_folder_path,
                                      n_submitted)
    print("%d jobs submitted total" % n_submitted)
