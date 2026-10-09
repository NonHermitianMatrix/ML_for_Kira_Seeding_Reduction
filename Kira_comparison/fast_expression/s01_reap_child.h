// SPDX-License-Identifier: GPL-3.0-or-later
// Bounded child reaping for Kira's Fermat interface. Exact algebra is unchanged.
#ifndef KIRA_RESPONSIVE_REAP_H
#define KIRA_RESPONSIVE_REAP_H
#include <cerrno>
#include <chrono>
#include <csignal>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
namespace kira_responsive {
enum class Outcome { exited, forced, not_child, invalid, error };
inline Outcome reap(pid_t child, int &status,
                    std::chrono::milliseconds grace=std::chrono::milliseconds(1000)) {
  if(child<=0) return Outcome::invalid;
  const auto deadline=std::chrono::steady_clock::now()+grace;
  for(;;) {
    const pid_t got=waitpid(child,&status,WNOHANG);
    if(got==child) return Outcome::exited;
    if(got<0) {
      if(errno==EINTR) continue;
      return errno==ECHILD?Outcome::not_child:Outcome::error;
    }
    if(std::chrono::steady_clock::now()>=deadline) break;
    std::this_thread::sleep_for(std::chrono::milliseconds(2));
  }
  // An unreaped child retains its PID, so this cannot signal a reused PID.
  if(kill(child,SIGKILL)<0 && errno!=ESRCH) return Outcome::error;
  pid_t got;
  do {got=waitpid(child,&status,0);} while(got<0 && errno==EINTR);
  return got==child?Outcome::forced:(errno==ECHILD?Outcome::not_child:Outcome::error);
}
}
#endif
