#!/usr/bin/env python3

import os
import shutil
import argparse
import tarfile
import getpass
import modules.fp_ad_tools as tools

config_manager = tools.Configuration()
config_manager.load()

# check for admin privileges
if getpass.getuser() != 'root' and os.geteuid != 0:
    print('error: this command must be run as root user')
    exit(1)

# Check for user existence
def check_user(username):
    command = f'{config_manager.samba_path} user list | grep "\\{username}\\b" > /dev/null'
    exit_code = os.system(command)

    if exit_code != 0:
        return False

    return True

# Create tar file of provided directory
def make_tarfile(output_file, source_dir):
    with tarfile.open(output_file, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# Delete user from system
def delete_user(username, tar):
    command = f'{config_manager.samba_path} user delete \'{username}\''
    # if tar is true, create a tar file
    if tar:
        make_tarfile(f'{config_manager.home_dirs_path}/{username}.tar.gz', f'{config_manager.home_dirs_path}/{username}')
    os.system(command)
    
    # remove user home dir
    shutil.rmtree(f'{config_manager.home_dirs_path}/{username}', ignore_errors=True)

# Delete users from csv file
def delete_from_file(filename, tar):
    user_loader = tools.UserLoader(filename)
    users = user_loader.load()

    for user in users:
        delete_user(user.username, tar)
        print(f"processed user {user.username} - add performed - tar: {tar}")

def main():
    # arguments parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="path of input csv file")
    parser.add_argument("-t", "--tar", help="creates a tar file with the content of user's home directory", action="store_true")
    parser.add_argument("USERNAME", nargs='?', help="logon user name", default='')

    args = parser.parse_args()

    if args.filename:
        delete_from_file(args.filename, args.tar)
        exit(0)

    if args.USERNAME != '':
        if not check_user(args.USERNAME):
            exit(0)
        delete_user(args.USERNAME, args.tar)
        exit(0)

if __name__ == "__main__":
    main()
