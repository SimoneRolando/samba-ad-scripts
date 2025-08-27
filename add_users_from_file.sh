#!/bin/bash

# Define the path to the user data file
user_data_file="users.txt"

# Define the command to add a user (adjust parameters as needed)
add_user_command="samba-tool user create"

# Define the command to set the password
set_password_command="samba-tool user setpassword"

group_add_command="samba-tool user setprimarygroup"

# Define the default password (or generate a random one)

# Check if the user data file exists
if [ ! -f "$user_data_file" ]; then
  echo "Error: User data file not found: $user_data_file"
  exit 1
fi

# Read the user data file line by line
while IFS=' ' read -r login_name first_name last_name email group default_password; do
  # Construct the command to add the user
  full_add_user_command="$add_user_command $login_name --given-name $first_name --surname $last_name --mail-address $email"

  # Execute the command to add the user
  echo "Adding user: $login_name"
  $full_add_user_command

  # Check if the user was added successfully
  if [ $? -eq 0 ]; then
    # Construct the command to set the password
    full_set_password_command="$set_password_command $login_name --newpassword=$default_password --must-change-at-next-login"

    # Execute the command to set the password
    echo "Setting password for $login_name"
    $full_set_password_command

    # Check if password was set successfully
    if [ $? -eq 0 ]; then
       echo "User $login_name created and password set."

       #construct the command to add user to group
       full_group_add_command="$group_add_command $login_name $group"

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
