#Imported Libraries
import subprocess, sys

#This function checks to see if a library is up to date
def check_up_to_date(name):
    
    #Access the name of the latest version of the package using the terminal
    latest_version = str(subprocess.run([sys.executable, '-m', 'pip', 'install', '{}==random'.format(name)], capture_output=True, text=True))
    latest_version = latest_version[latest_version.find('(from versions:')+15:]
    latest_version = latest_version[:latest_version.find(')')]
    latest_version = latest_version.replace(' ','').split(',')[-1]

    #Access the name of the current version of the package using the terminal
    current_version = str(subprocess.run([sys.executable, '-m', 'pip', 'show', '{}'.format(name)], capture_output=True, text=True))
    current_version = current_version[current_version.find('Version:')+8:]
    current_version = current_version[:current_version.find('\\n')].replace(' ','') 

    #Return whether or not the two version names are the same
    return latest_version == current_version
