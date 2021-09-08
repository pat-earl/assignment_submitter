#!/usr/bin/env python3

# Authors:
#   Patrick Earl
#   Dylan Schwesinger

# TODO (maybe?)
# * more ignore patterns
# * add semester in path
# * prepend username to archive contents


from datetime import datetime
from shutil import copytree, make_archive, ignore_patterns, copy
from tempfile import TemporaryDirectory
import os
import signal
import sys
import tarfile
import json


def handler(signum, frame):
    raise Exception("ERROR: timeout")


def child(tarfile_basename):

    # set to student's real user ID
    ruid = os.getuid()
    os.setreuid(ruid, ruid)

    tarfile_name = tarfile_basename + ".tar.gz"

    # remove the tarfile if it exists
    if os.path.exists(tarfile_name):
        os.remove(tarfile_name)

    # set an alarm to exit if the archive creation takes too long
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)

    # create the tarfile
    try:
        with TemporaryDirectory() as tempdir:
            copytree(
                os.getcwd(),
                os.path.join(tempdir, sys.argv[2]),
                ignore=ignore_patterns(".git", "*~")
                )
            make_archive(tarfile_basename, "gztar", tempdir)

        # change the permissions on the tar file
        os.chmod(tarfile_name, 0o744)
        #os.chmod(tarfile_name, 0o777)
    except Exception:
        os._exit(2)

    # disable alarm
    signal.alarm(0)

    # exit child
    os._exit(0)


def parent(tarfile_basename):

    # change to uid
    #euid = os.geteuid()
    #os.setreuid(euid, euid)

    # wait for the child to finish
    pid, status = os.wait()

    # check for timeout error
    if os.WEXITSTATUS(status) == 2:
        msg = "ERROR: archive creation timed out; " \
              "you may not be in the correct directory"
        print(msg)
        sys.exit(0)

    tarfile_name = tarfile_basename + ".tar.gz"

    print("The following files will be submitted:")

    # get archive contents
    tar_contents = None
    with tarfile.open(tarfile_name) as tf:
        tar_contents = tf.getnames()

    # print the archive contents
    for name in tar_contents:
        print(name)

    # Confirm the student wants to send the files
    response = input("Continue? [y/N] ")

    if response.lower() == "y":

        submission_dir = os.path.join(
            CONFIG["submission_basedir"], sys.argv[1], sys.argv[2])

        # create the submission directory if it does not exist
        if not os.path.isdir(submission_dir):
            oldmask = os.umask(0o077)
            os.makedirs(submission_dir, 0o700)
            os.umask(oldmask)

        euid = os.geteuid()
        ruid = os.getuid()
        print(euid, ruid)
        # move the tarfile to the submission directory
        #os.rename(tarfile_name, os.path.join(submission_dir, tarfile_name))
        copy(tarfile_name, os.path.join(submission_dir, tarfile_name))

        # log the submission
        with open(os.path.join(submission_dir, "submission.log"), "a") as f:
            f.write(datetime.now().isoformat(timespec="minutes"))
            f.write(" ")
            f.write(os.getlogin())
            f.write("\n")

        # send email confirmation
        mail_command = "/bin/mail -s '[{}] Submission Confirmation'" \
                       " -b {} -r {} {}@kutztown.edu".format(
                               sys.argv[1].upper(),
                               CONFIG["email"],
                               CONFIG["email"],
                               os.getlogin()
                               )
        mail_contents = "\n".join(
                ["Files Submitted for {}:".format(sys.argv[2])]
                + tar_contents
                + ["This is an automated email"]
                )

        os.system("echo \"" + mail_contents + "\" | " + mail_command)

        print("Assignment submitted; you will receive a confirmation email.")
    else:
        print("Assignment submission halted")
        # remove the tarfile from the current directory

    # set to student's real user ID
    ruid = os.getuid()
    os.setreuid(ruid, ruid)
    os.remove(tarfile_name)


if __name__ == "__main__":

    # ignore the interrupt signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # load config file
    with open("/home/kutztown.edu/schwesin/bin/submit_config.json") as f:
        CONFIG = json.load(f)

    # validate command line arguments
    if len(sys.argv) != 3:
        msg = "usage: submit <course> <assignment>\n" \
              "    course      Course in the form cscXXX" \
              " where XXX is the course number\n" \
              "    assignment  Name of the assignment\n" \
              "\nCreates an archive of the current directory for submission.\n"
        print(msg)
        sys.exit(0)

    elif sys.argv[1] not in CONFIG["assignments"]:
        msg = "ERROR: invalid course\n" \
              "Valid course values are:"
        print(msg)
        for c in CONFIG["assignments"]:
            print("    ", c)
        sys.exit(0)

    elif sys.argv[2] not in CONFIG["assignments"][sys.argv[1]]:
        msg = "ERROR: invalid assignment\n" \
              "Valid assignments for course {} are:".format(sys.argv[1])
        print(msg)
        for a in CONFIG["assignments"][sys.argv[1]]:
            print("    ", a)
        sys.exit(0)

    username = os.getlogin()

    if username not in CONFIG["roster"][sys.argv[1]]:
        msg = "ERROR: you are not in the {} class list".format(sys.argv[1])
        print(msg)
        sys.exit(0)

    tarfile_basename = username + "_" + sys.argv[2]

    child_pid = os.fork()
    if child_pid == 0:
        child(tarfile_basename)
    else:
        parent(tarfile_basename)
