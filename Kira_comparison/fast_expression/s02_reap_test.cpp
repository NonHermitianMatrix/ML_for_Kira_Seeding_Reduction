// SPDX-License-Identifier: GPL-3.0-or-later
#include "s01_reap_child.h"
#include <cassert>
#include <iostream>
using kira_responsive::Outcome;
int main() {
 int status=0;auto start=std::chrono::steady_clock::now();
 pid_t child=fork();assert(child>=0);if(child==0)_exit(7);
 assert(kira_responsive::reap(child,status)==Outcome::exited);
 assert(WIFEXITED(status)&&WEXITSTATUS(status)==7);
 double quick=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 assert(quick<0.8);
 child=fork();assert(child>=0);if(child==0){usleep(80000);_exit(9);}
 assert(kira_responsive::reap(child,status)==Outcome::exited);
 assert(WIFEXITED(status)&&WEXITSTATUS(status)==9);
 child=fork();assert(child>=0);if(child==0){for(;;)pause();}
 start=std::chrono::steady_clock::now();
 assert(kira_responsive::reap(child,status,std::chrono::milliseconds(30))==Outcome::forced);
 assert(WIFSIGNALED(status)&&WTERMSIG(status)==SIGKILL);
 double forced=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 assert(forced<0.8);
 assert(kira_responsive::reap(child,status)==Outcome::not_child);
 assert(kira_responsive::reap(getpid(),status)==Outcome::not_child);
 assert(kira_responsive::reap(0,status)==Outcome::invalid);
 assert(kira_responsive::reap(-1,status)==Outcome::invalid);
 assert(waitpid(-1,&status,WNOHANG)==-1 && errno==ECHILD);
 std::cout<<"{\"passed\":true,\"quick_exit_seconds\":"<<quick<<",\"forced_exit_seconds\":"<<forced<<",\"checks\":8}\n";
}
