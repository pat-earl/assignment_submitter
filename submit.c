// file: submit.c
// run "submit.py" with the SUID bit

#include <stdio.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

int main(int argc, char **argv)
{
    char* cmd = "/home/kutztown.edu/schwesin/bin/submit.py";
    int return_code = execvp(cmd, argv);

    if (return_code == -1) {
        printf("%d: %s\n", errno, strerror(errno));
    }

    return 0;
}
