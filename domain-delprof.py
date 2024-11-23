#!/usr/bin/env python3

import os
import getpass
import argparse
import shutil
import subprocess
import modules.fp_ad_tools as tools

config_manager = tools.Configuration()
config_manager.load()

# program body
def main():
    # check for admin privileges
    if getpass.getuser() != 'root' and os.geteuid != 0:
        print('error: this command must be run as root user')
        exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("GROUP", help="group name to delete profiles", nargs='?', default='')
    parser.add_argument("-u", "--username", help="delete profile for single user")
    args = parser.parse_args()

    if args.username:
        print(f'now deleting profiles for user {args.username}..')
        shutil.rmtree(f'{config_manager.home_dirs_path}/{args.username}/.profiles', ignore_errors=True)
        print(f'profiles for user {args.username} deleted!')
        exit(0)

    if args.GROUP:
        process = subprocess.Popen([config_manager.samba_path, 'group', 'listmembers', args.GROUP], stdout=subprocess.PIPE)
        p_output = process.communicate()[0]
        output = p_output.decode('utf-8').splitlines()

        for user in output:
            print(f'now deleting profiles for user {user}..')
            shutil.rmtree(f'{config_manager.home_dirs_path}/{user}/.profiles', ignore_errors=True)
            print(f'profiles for user {user} deleted!')

        exit(0)

if __name__ == "__main__":
    main()