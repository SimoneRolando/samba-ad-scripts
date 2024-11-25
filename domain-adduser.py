#!/usr/bin/env python3

import os
import subprocess
import argparse
import getpass
import pwd
import grp
import sys
from sys import exit
import modules.fp_ad_tools as tools

config_manager = tools.Configuration()
config_manager.load()

# path and server separator
PATH_DELIM = r"\\"
SRV_DELIM = r"\\\\"

# Add users from csv
def add_from_csv(filepath):
        user_loader = tools.UserLoader(filepath)
        users = user_loader.load()
        
        for user in users:
            if not tools.check_user_validity(user):
                print('Received invalid user: ', user)
                continue
            
            groups = [user.group, user.classroom] if user.classroom != "" or user.classroom is not None else [user.group]
            adduser(user.username, user.password, user.last_name, user.first_name, groups)
            print(f"processed user {user.username} - add performed")

# Update user from file
def update_from_file(filepath):
    user_loader = tools.UserLoader(filepath)
    users = user_loader.load()
    
    for user in users:
        groups = [user.group, user.classroom] if user.classroom != "" or user.classroom is not None else [user.group]
        update(user.username, user.password, user.last_name, user.first_name, groups)
        print(f"processed user {user.username} - update performed")

# Check for group existence
def check_group(group):
    command = f'{config_manager.samba_path} group list | grep "{group}\\b" > /dev/null'
    exit_code = os.system(command)

    if exit_code != 0:
        return False

    return True

# Check for user existence
def check_user(username):
    command = f'{config_manager.samba_path} user list | grep "\\{username}\\b" > /dev/null'
    exit_code = os.system(command)

    if exit_code != 0:
        return False

    return True

# Create new group on system
def create_group(group_name):
    command = f'{config_manager.samba_path} group add "{group_name}"'
    os.system(command)

# Add a member to existing group
def add_member(group_name, member_name):
    command = f'{config_manager.samba_path} group addmembers "{group_name}" "{member_name}"'
    os.system(command)

# Create user home directory
def user_mkhomedir(username):
    if not os.path.exists(f'{config_manager.home_dirs_path}/{username}'):
        os.mkdir(f'{config_manager.home_dirs_path}/{username}')
    uid = pwd.getpwnam(f'{config_manager.nt_domain_name}{config_manager.winbind_separator}{username}').pw_uid
    gid = grp.getgrnam(f'{config_manager.nt_domain_name}{config_manager.winbind_separator}{username}').gr_gid
    os.chown(f'{config_manager.home_dirs_path}/{username}', uid, gid)

# Read password from console input, with silent prompt
def read_password():
    for i in range(0, 3):
        passwd = getpass.getpass('Enter new password: ')
        passwd_r = getpass.getpass('Retype new password: ')

        if passwd == passwd_r:
            return passwd
        else:
            print('\nPassword mismatch, please retry!')
    
    print('\nAuthentication token manipulation error. Password mismatch')

# Add a new user to the domain
def adduser(username, password, last_name, first_name, groups):
    create_command = f'{config_manager.samba_path} user create "{username}" {password} --use-username-as-cn '
    user_info = f'--surname="{last_name}" --given-name="{first_name}" '
    home_info = f'--home-drive=H: --home-directory="{SRV_DELIM}{config_manager.server_name}{PATH_DELIM}users{PATH_DELIM}{username }" '
    profile_info = f'--profile-path="{SRV_DELIM}{config_manager.server_name}{PATH_DELIM}users{PATH_DELIM}{username}{PATH_DELIM}.profiles{PATH_DELIM}{username}"'

    full_command = create_command + user_info + home_info + profile_info

    # add new user
    os.system(full_command)
    # create home dir
    user_mkhomedir(username)
    
    # add user to each group or create it if it does not exist
    for group in groups:
        if not check_group(group):
            create_group(group)
        add_member(group, username)

def update(username, password, last_name, first_name, groups):
    if not check_user(username):
        adduser(username, password, last_name, first_name, groups)
        return
    
    # Update user, resetting password and groups
    change_passwd = f'{config_manager.samba_path} user setpassword --newpassword={password} "{username}"'
    os.system(change_passwd)

    # Update groups, by removing everything but basic domain elements
    process = subprocess.Popen([config_manager.samba_path, 'user', 'getgroups', username], stdout=subprocess.PIPE)
    p_output = process.communicate()[0]

    # remove all groups except Domain Users and Domain Admins
    output = p_output.decode('utf-8').splitlines()
    for g in output:
        if g != 'Domain Admins' and g != 'Domain Users':
            os.system(f'{config_manager.samba_path} group removemembers "{g}" "{username}"')

    # add user to new groups
    for g in groups:
        print(f'group {g}')
        if not check_group(g):
            create_group(g)
        os.system(f'{config_manager.samba_path} group addmembers "{g}" "{username}"')


def main():
    # check for admin privileges
    if getpass.getuser() != 'root' and os.geteuid != 0:
        print('error: this command must be run as root user')
        exit(1)

    parser = argparse.ArgumentParser()

    # command options and arguments
    parser.add_argument("-f", "--filename", help="path of input csv file")
    parser.add_argument("-i", "--interactive", help="enables interactive user creation",
                        action="store_true")
    parser.add_argument("-u", "--update", help="enables update mode, changing existing user information")
    parser.add_argument("USERNAME", nargs='?', help="user logon name")

    # Check number of arguments
    if len(sys.argv) == 1:
        parser.print_usage()
        exit(1)

    # Parse arguments
    args = parser.parse_args()

    # if interactive mode, read user inputs and start messing around
    # with the user creation process
    if args.interactive:
        # check presence of username argument
        if not args.USERNAME or args.USERNAME.strip() == "":
            parser.print_usage()
            exit(1)

        # Check user existence before proceeding
        if check_user(args.USERNAME):
            exit(0)
        
        # read last name and first name from console
        print(f'Changing the user information for {args.USERNAME}')
        last_name = input('\tLast name []: ')
        first_name = input('\tFirst name []: ')
        groups = input('\tGroups []: ').split(',')
        password = read_password()

        adduser(args.USERNAME, password, last_name, first_name, groups)
        exit(0)

    if args.update:
        update_from_file(args.update)
        exit(0)

    if args.filename:
        add_from_csv(args.filename)
        exit(0)
        
if __name__ == "__main__":
    main()
