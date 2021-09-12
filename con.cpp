#include <bits/stdc++.h>
#include <sched.h>
#include <unistd.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <sys/mount.h>


using namespace std;

#define STACK_SIZE 1024*1024
#define HOSTNAME "conman"
#define CHROOT_PATH "/home/akash/conman_again/ubuntu_fs/"
#define errExit(msg) {perror(msg); return errno;}

#include "mount.h"
MountHelper MOUNT_HELPER;

struct ChildArgs{
	char ** argv;
};

int fork_and_execute(ChildArgs* child_args)
{
    pid_t fork_pid = fork();

    if(fork_pid < 0)
        errExit("Fork failed.\n");

    if(fork_pid == 0)
    {
        cout << "Starting forked process...\n";
        execvp(child_args->argv[0], child_args->argv);
    }
    else
    {
        if(waitpid(fork_pid, NULL, 0) < 0)
            errExit("Forked process failed.\n");
        cout << "Fork process terminated. Exiting.\n";
    }
    return 0;
}

int setup_container()
{
    sethostname((char *)HOSTNAME, ((string)HOSTNAME).size());
    // MOUNT_HELPER.add_mount("", "/", "", MS_REC | MS_PRIVATE );
    // mount("", CHROOT_PATH, "", MS_PRIVATE, NULL);
	if(chdir((char*)CHROOT_PATH) || chroot((char *)CHROOT_PATH)!= 0)
		errExit("Error in chroot");
    MOUNT_HELPER.add_mount("proc", "/proc", "proc", 0);
    return 0;
}

int child(void* args)
{
    ChildArgs* child_args = static_cast<ChildArgs*>(args);

    if(setup_container() < 0)
        errExit("Container setup failed.\n");

    return fork_and_execute(child_args);
}
int main(int argc, char* argv[])
{
    static char child_stack[STACK_SIZE];

	int flags = CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNS | SIGCHLD;
    ChildArgs child_args = {&argv[1]};
    pid_t child_pid = clone(child, child_stack + STACK_SIZE, flags, &child_args);
    if(child_pid < 0)
    {
        cout << "Error creating child process\n";
        cout << errno << "\n";
    }
    if(waitpid(child_pid, NULL, 0) < 0)
    {
        cout << "Error executing child process.\n";
        cout << errno << "\n";
    }
    return 0;
}