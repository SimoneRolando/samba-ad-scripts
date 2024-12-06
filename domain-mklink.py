#!/usr/bin/env python3

import os
import getpass
import pwd
import grp
import sys
import argparse
from sys import exit
import modules.fp_ad_tools as tools

config_manager = tools.Configuration()
config_manager.load()

# Convert user first names and last names from spaces to underscores
def convert_user_names(last_name, first_name) -> str:
    return last_name.replace(" ", "_") + "_" + first_name.replace(" ", "_")

# Add users from csv
def add_from_csv(filepath):
    user_loader = tools.UserLoader(filepath)
    users = user_loader.load()

    for user in users:
        if not tools.check_user_validity(user):
            print('Received invalid user: ', user)
            continue
        
        if user.group == "" and user.classroom == "":
            print(f"error: user {user.username} has no parent group, skipping link creation...")
            continue

        # create directories
        if not os.path.exists(f'{config_manager.pool_path}/{user.classroom}'):
            os.mkdir(f'{config_manager.pool_path}/{user.classroom}')
            uid = pwd.getpwnam(f"{config_manager.nt_domain_name}{config_manager.winbind_separator}{user.username}").pw_uid
            gid = grp.getgrnam(f'{config_manager.nt_domain_name}{config_manager.winbind_separator}{config_manager.pool_owner}').gr_gid
            os.chown(f'{config_manager.pool_path}/{user.classroom}', uid, gid)

        # create symlink
        src = f'{config_manager.home_dirs_path}/{user.username}'
        dst = f'{config_manager.pool_path}/{user.classroom}/{user.username}'
        if not os.path.exists(dst):
            print(f'linking {src} to {dst}')
            os.symlink(f'{config_manager.home_dirs_path}/{user.username}', f'{config_manager.pool_path}/{user.classroom}/{user.username}_{convert_user_names(user.last_name, user.first_name)}', target_is_directory=True)

def main():
    # check for admin privileges
    if getpass.getuser() != 'root' and os.geteuid != 0:
        print('error: this command must be run as root user')
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help="create links for all users in file")

    # Check number of arguments
    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    args = parser.parse_args()

    if args.filename:
        add_from_csv(args.filename)
        exit(0)

if __name__ == "__main__":
    main()