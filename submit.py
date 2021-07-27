#!/usr/bin/python3

# Author:   Patrick Earl
# Submit script that will copy student submissions to a specified directory that is only
# accessibly by the instructor
#
# Script needs to be ran by the cpp executable with SUID bit and SGID. (submit.cpp) 
# Should be owned by instructor and the csit_faculty group

import os
import pwd
import sys
import signal
import stat
import tarfile

from shutil import copy, copytree, copyfile, Error as shutilError

# CONFIGURATION
# --- STORAGE_DIR ---
# Base directory where assignments will be stored. The script will create new directories for
# each course and the tar files will be placed there. 
# STORAGE_DIR + /csc135/assignment0/csstu000
STORAGE_DIR = "/home/kutztown.edu/earl/submissions"

# --- VALID_COURSES ---
VALID_COURSES = [
    'csc135'
]

# --- CSIT_FACULTY_GID ---
# The UNIX group id for the csit_faculty group
# Can be found with this command: getent group csit_faculty
CSIT_FACULTY_GID = 220853343

# --- PROF_NAME ---
# Put your name here
PROF_NAME = "Prof. Patrick Earl"



# ---- DEBUGGING PRINT STATEMENTS (IGNORE) ----
# print("Effective ID:", os.geteuid())
# print("Real ID:", os.getuid())

# print(sys.argv)
# os.system('whoami')
# ---------------------------------------------

# Add a signal handler to prevent the script from being terminated by CTRL-C
# (This is so the directory permissions don't get out of wack)
def no_exit(sig, stack):
    pass

signal.signal(signal.SIGINT, no_exit)

# Arguments Check
if len(sys.argv) < 3:
    print("Usage: {} <course> <assignment name>".format(sys.argv[0]))
    print("Course should be in cscXXX format. Where XXX is the course number (i.e. csc135)")
    print("Assignment name should be the name specified in the assignment handout")
    print("Run this IN the directory your submittables are in")
    sys.exit()

elif sys.argv[1] not in VALID_COURSES:
    print("You need to specify a valid course")
    print("Where XXX is the course number (i.e. csc135")
    sys.exit()

# Begin the copy process

stu_username = os.getlogin()
course = sys.argv[1]
assignment_name = sys.argv[2]
instructor_uid = os.getegid()
tar_name = '{}_{}.tar'.format(stu_username, assignment_name)
assignment_dir = os.path.join(STORAGE_DIR, course, assignment_name)

# Make the assignment directory (if it doesn't exist)
if not os.path.isdir(assignment_dir):
    os.makedirs(assignment_dir)
    # Make sure instructor is the owner & group
    os.chown(assignment_dir, os.geteuid(), CSIT_FACULTY_GID)


# Change the assignment dir's permissions (777)
os.chmod(assignment_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

# Directory is set up and student account can copy into it.
child_pid = os.fork()
# CHILD PROCESS
# Child process is responsible for copying the student's files to said directory
if child_pid == 0:
    # Set the EUID back to the student's REAL ID
    ruid, euid = os.getuid(), os.geteuid()
    os.setreuid(ruid, ruid)

    print("Do you, {}, wish to submit the following files to {} for {}?".format(stu_username, 
                                                                                PROF_NAME, 
                                                                                assignment_name))
    # Directory listing of the files 
    for root, dirs, files in os.walk('.', topdown=True):
        for name in files:
            print(os.path.join(root, name))
        for name in dirs:
            print(os.path.join(root, name))
    
    # Confirm the student wants to send the files
    print("Make sure the assignment name is the same as the one specified in the assignment/project handout!")
    response = input("Type q or Q + ENTER to cancel or hit ENTER to send the files")
    if response.lower() == 'q':
        sys.exit(1)
   
    # Tar the directory
    tar = tarfile.open(tar_name, mode='w:')
    tar.add(".")
    tar.close()

    sys.exit(0)

else:
    # Wait for the child process (Probably don't need the status code or PID)
    pid, status = os.wait()

    # Copy the created tar
    copy(tar_name, os.path.join(assignment_dir, tar_name))
    # Change the permissions on the tar
    os.chmod(os.path.join(assignment_dir, tar_name), stat.S_IRUSR | stat.S_IWUSR)

    # Reset the assignment submission permissions
    os.chmod(assignment_dir, stat.S_IRWXU)
    # TODO: Send E-Mail receipt

    # Set the euid to the student's and remove the tar file from their directory
    ruid = os.getuid()
    os.setreuid(ruid, ruid)
    os.remove(tar_name)

# EOF
