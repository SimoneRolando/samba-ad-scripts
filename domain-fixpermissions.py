#!/usr/bin/env python3

import os
import subprocess
import pwd
import grp
import argparse
import getpass
from sys import exit
import modules.fp_ad_tools as tools

config_manager = tools.Configuration()
config_manager.load()

# Fix user permissions
def fix_user_permissions(username):
    domuser = f"{config_manager.nt_domain_name}{config_manager.winbind_separator}{username}"
    print(f"fixing permissions for {domuser}")

    uid = pwd.getpwnam(f"{domuser}").pw_uid
    gid = grp.getgrnam(f"{domuser}").gr_gid
    for root, dirs, files in os.walk(f"{config_manager.home_dirs_path}/{username}"):
        for d in dirs:
            os.chown(os.path.join(root, d), uid, gid)
        for f in files:
            os.chown(os.path.join(root, f), uid, gid)

# Get user list as array of strings
def get_users_list():
    process = subprocess.Popen([config_manager.samba_path, 'user', 'list'], stdout=subprocess.PIPE)
    output = process.communicate()[0]
    output = output.decode('utf-8').splitlines()
    return output

# Fix user permissions from file
def fix_from_file(filepath):
    user_loader = tools.UserLoader(filepath)
    users = user_loader.load()

    for user in users:
        fix_user_permissions(user.username)

def main():
    # check admin privileges
    if getpass.getuser() != 'root' and os.geteuid != 0:
        print("error: this command must be run as root user")
        exit(1)

    parser = argparse.ArgumentParser()

    # command options and arguments
    parser.add_argument("-f", "--filename", help="path for input csv file")
    parser.add_argument("-a", "--all", help="fixes all users permissions")
    parser.add_argument("USERNAME", nargs='?', help="user logon name", default='')

    # parse arguments
    args = parser.parse_args()

    # fix permissions for all users in the domain
    if args.all:
        users = get_users_list()

        for user in users:
            if user == "Administrator" or user == "krbtgt":
                continue
            fix_user_permissions(user)

        exit(0)

    if args.filename:
        fix_from_file(args.filename)
        exit(0)

    if args.USERNAME == "":
        parser.print_usage()
        exit(1)

    fix_user_permissions(args.USERNAME)

if __name__ == "__main__":
    main()