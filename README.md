# Assignment Submitter

Allows for "secure" copying of student submissions from a Linux directory they own to one owned
by the instructor. This was developed for use on Kutztown University Computer Science's Linux
machines. 

## submit.cpp

A simple wrapper program that calls the Python script file (submit.py). Linux envs do not allow 
interpreted scripts to be ran with with the SUID or SGID bits, which the script needs in order
to run. 

This should be compiled using whatever g++ your Linux disto has to avoid `LD_LIBRARY_PATH`
problems (Since SUID programs ignore that env variable). 

After compiling make sure it's accessible by any user on the system and set the bits.

## submit.py


