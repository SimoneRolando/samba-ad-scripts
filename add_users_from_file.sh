#!/bin/bash

# Help function
show_help() {
  cat << EOF
Usage: $0 <user_data_file>

This script creates Samba users from a CSV file.

Arguments:
  user_data_file      Path to CSV file containing user data

CSV format:
  login_name,first_name,last_name,email,group,default_password

Example:
  $0 users.txt
  $0 /path/to/users.csv

Options:
  -h, --help          Show this help message
EOF
}

# Parse command line arguments
if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  show_help
  exit 0
fi

# Define the path to the user data file
# user_data_file="users.txt"
user_data_file="$1"

# Define the command to add a user (adjust parameters as needed)
add_user_command="samba-tool user create"

# Define the command to set the password
set_password_command="samba-tool user setpassword"

group_add_command="samba-tool group addmembers"

# Define the default password (or generate a random one)

# Check if the user data file exists
if [ ! -f "$user_data_file" ]; then
  echo "Error: User data file not found: $user_data_file"
  exit 1
fi

# Read the user data file line by line
while IFS=',' read -r login_name first_name last_name email group default_password; do
  # Properly escape the first name and last name
  escaped_first_name=$(printf '%q' "$first_name")
  escaped_last_name=$(printf '%q' "$last_name")

  # Construct the command to add the user
  user_args=(
    "$login_name"
    "$default_password",
    --must-change-at-next-login
    --use-username-as-cn
    --given-name "$first_name"
    --surname "$last_name"
    --mail-address "$email"
    --profile-path="\\\\claude\\userdis\\$login_name\\.profiles"
  )

  # Execute the command to add the user
  echo "Adding user: $login_name"
  samba-tool user create "${user_args[@]}"

  # Check if the user was added successfully
  if [ $? -eq 0 ]; then
    # Construct the command to set the password
    #full_set_password_command="$set_password_command $login_name --newpassword=$default_password --must-change-at-next-login"

    # Execute the command to set the password
    #echo "Setting password for $login_name"
    #$full_set_password_command

    # Check if password was set successfully
    if [ $? -eq 0 ]; then
       echo "User $login_name created and password set."

       #construct the command to add user to group
       full_group_add_command="$group_add_command $group $login_name"

       # Execute the command to add the user to the group
       echo "Setting group for $login_name"
       $full_group_add_command

       if [ $? -eq 0 ]; then
          echo "User $login_name added to the right group."
       else
          echo "Error: Failed to set group for $login_name"
       fi
    else
       echo "Error: Failed to set password for $login_name"
    fi
  else
    echo "Error: Failed to add user $login_name"
  fi
done < "$user_data_file"

echo "User creation script completed."
