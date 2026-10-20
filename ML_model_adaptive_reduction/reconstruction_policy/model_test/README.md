# Complete application comparison

Each compressed JSON file records one frozen physical request.
The four methods run three times in rotating order on the same worker.
Times include imports, model use, equation generation, exact algebra, recovery, output, and exit.
The external coefficient comparison occurs after that timer.
Records contain completions, failed attempts, chosen actions, and exact results.
The root summary uses summed per-request medians on matched completed requests.
All failures remain in the separate completion counts.
