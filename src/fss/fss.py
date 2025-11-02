import os
from fss_helper import *

# User's settings for modification + creation time - for now, dummies variable
# It should be the fss intaker responsibility to control if these values are valid (lower << upper, only 2 values in a list, etc.)
create_time_crit = [None, None]
mod_time_crit = [None, None]

def search(input_path, excluded_path):

    exclude_flag = True
    num_of_files_scanned = 0

    if not excluded_path:
        #If there is not included exclusion, the flag will be set to false to skip comparisons
        exclude_flag = False

    if not os.path.exists(input_path):
        #invalid returns -1
        return -1

    input_path = os.path.abspath(input_path)

    if exclude_flag:
        #ensures that the excluded paths input is a set
        if isinstance(excluded_path, str):
            excluded_path = {excluded_path}
        else:
            excluded_path = set(excluded_path)


        excluded_set = set()
        for e_path in excluded_path:
            e_path = os.path.abspath(e_path)
            excluded_set.add(e_path)

            #if exclusion includes a dir, it will add all files within the dir to exclusion
            if os.path.isdir(e_path):
                for root, dirs, files in os.walk(e_path):
                    for file in files:
                        excluded_set.add(os.path.join(root, file))
        
        excluded_path = excluded_set

    if os.path.isfile(input_path):
        if not excluded_path:
            #single file with no exclusion
            return 1
        elif input_path not in excluded_path:
            #single file accounting for exclusion
            return 1
        else:
            return 0

    for root, dirs, files in os.walk(input_path, topdown=True):

        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)
            if exclude_flag:
                if file_path not in excluded_path and time_check(create_time_crit, file_path, "create") and time_check(mod_time_crit, file_path, "mod"): # Added time checkers to abide criteria here
                    #This is where specifics of files can be extracted.
                    num_of_files_scanned += 1
            else:
                #Given no exclusion this is where details about scanned files can be extracted.
                num_of_files_scanned += 1

    return num_of_files_scanned
