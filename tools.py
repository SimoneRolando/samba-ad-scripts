import json
import csv
from dataclasses import dataclass

"""
User representation
"""
@dataclass
class User:
    username: str
    last_name: str
    first_name: str
    group: str
    classroom: str
    fiscal_id: str
    password: str

""""
Manages Active Directory configuration file
"""
class Configuration:
    def __init__(self, config_file='/etc/ad/settings.conf'):
        # configuration file path
        self.config_file = config_file
        
        # local settings
        self.samba_path = ""
        self.server_name = ""
        self.home_dirs_path = ""
        self.nt_domain_name = ""
        self.pool_path = ""
        self.pool_owner = ""
        self.winbind_separator = ""
        
    # Load configuration from system JSON file
    def load(self):
        try:
            with open(self.config_file, 'r') as data:
                config_data = json.load(data)
                
                # load file settings
                self.samba_path = config_data.get('samba_path', "")
                self.server_name = config_data.get('server_name', "")
                self.home_dirs_path = config_data.get('home_dirs_path', "")
                self.nt_domain_name = config_data.get('nt_domain_name', "")
                self.pool_path = config_data.get('pool_path', "")
                self.pool_owner = config_data.get('pool_owner', "")
                self.winbind_separator = config_data.get('winbind_separator', "")
                
        except json.JSONDecodeError as e:
            print("Error parsing JSON: ", e)
                
"""
Manages user loading operation
""" 
class UserLoader:
    def __init__(self, users_file, separator=';'):
        self.users_file = users_file
        self.separator = separator
        
    def load(self) -> list:
        results = []
        
        with open(self.users_file, mode='r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=self.separator)
            
            try:
                for row in reader:
                    username = row.get('login', None)
                    last_name = row.get('cognome', None)
                    first_name = row.get('nome', None)
                    group = row.get('gruppo', None)
                    classroom = row.get('classe', None)
                    fiscal_id = row.get('cf', None)
                    password = row.get('password', None)
                    
                    results.append(User(username, last_name, first_name, group, classroom, fiscal_id, password))
            except csv.Error as e:
                print("Error parsing CSV file: ", e)
                
        return results

"""
Checks the validity of a User
"""    
def check_user_validity(user: User) -> bool:
    basic = user.username and user.password
    personal = user.first_name and user.last_name
    
    if not user.group:
        return False
    
    # Check user validity based on type
    if user.group.lower() == "docenti".lower():
        return basic and personal
    
    if user.group and user.group.lower() != "docenti".lower():
        return basic and personal
    
    return False
                