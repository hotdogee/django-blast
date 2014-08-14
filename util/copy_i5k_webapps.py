#!/usr/bin/env python
from os import listdir
from os.path import isdir, join, isfile
from shutil import copy2

if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description='Copy source file to all organism directories.')
    #parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='source file to copy')
    #args = parser.parse_args()
    WEBAPPS_ROOT = r'/app/local/tomcat/webapps'
    FILE_LIST = [r'anogla/jbrowse/contrib_styles.css']
    #FILE_LIST = args.files
    #print FILE_LIST
    # get dir list
    organism_dir_list = [f for f in listdir(WEBAPPS_ROOT) if isdir(join(WEBAPPS_ROOT, f)) and len(f) == 6]

    # work through file list
    for filename in FILE_LIST:
        source_dir, filename = filename.split('/', 1)
        if isfile(join(WEBAPPS_ROOT, source_dir, filename)):
            for target_dir in organism_dir_list:
                if source_dir != target_dir:
                    copy2(join(WEBAPPS_ROOT, source_dir, filename), join(WEBAPPS_ROOT, target_dir, filename))