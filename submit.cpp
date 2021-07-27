/*
 * Wrapper to run the submit.py script with sticky bit set!
*/
#include <iostream>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sstream>

using namespace std;

int main(int argc, char **argv)
{
    string cmd = "/home/kutztown.edu/earl/bin/submit.py";
    int return_code = execvp(cmd.c_str(), argv);

    if (return_code == -1)
        cout << errno << ": " << strerror(errno) << endl;

    return 0;
}
