# Application test

These files compare fresh processes on sequences of three momentum scales.
The factors are 1, 3/2, and 2.
Each sequence includes its initial Kira reduction and all exact checks.
The four methods separate learned choices and exact reuse.
Each base request has three repetitions, with all methods on the same worker.
JOINT_APP_PARTS and JOINT_APP_PART split disjoint base requests between workers.
Completion requires every part.
Native references are generated independently at all three scales.

Read [the parent guide](../README.md) for producers, readers, dependencies, and limits.
