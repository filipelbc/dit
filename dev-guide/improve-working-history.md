# Reimplement Working History

## Problem statement

The current implementation has the following problems:

1. **Task states specification**: There is no specification of the possible
   states of Task and the transitions between them.

2. **Working in multiple tasks**: The user is able to work on multiple tasks at
   the same time. This feature is useless and adds unnecessary complexity to the
   system.
    * Example: `dit workon A` + `dit workon B` implies "user is working on both
      A and B".

3. **Limited working history**: Assume that the user started working in Task A.
   Then, while working on Task A, he was interrupted, which caused him to switch
   to Task B. Then he was interrupted again, causing him to switch to Task C. In
   the current implementation, the Task A will be lost in the working history.
   That is, he will be able to resume Task B after completing Task C, but will
   not be able to resume Task A after completing Task B.

    * Example: `dit workon A` + `dit switchto B` + `dit switchto C` +
               `dit conclude C` + `dit resume` + `dit conclude B` implies
               "user is not able to resume the work on A using the `resume`
               command"

4. **List of halted tasks**: The user should be able to see
   the list of halted tasks (through the dit status command). In the current
   implementation, the only way to do that is by iterating over all the task
   files, which can be impractible in a real scenario.

## Proposed solution

1. **Task states specification**: Each task should be in one of the following
   states:

    1. **TODO state**:
        * *Previous state*: None.
        * *When a task assume this state?*: In the instant of creation.
        * *How many tasks in this state*: 0-N.

    2. **CURRENT state**:
        * *Previous state*: Any of the other three states.
        * *When a task assume this state*: In the instant the user start working
          in the task.
        * *How many tasks in this state*: 0-1.

    3. **HALTED state**:
        * *Previous state*: CURRENT state.
        * *When a task assume this state*: In the instant the user stops working
          on the current task or switches to another task.
        * *How many tasks in this state*: 0-N

    4. **COMPLETED state**:
        * *Previous state*: Any of the other three states.
        * *When a task assume this state*: In the instant the user completes the task.
        * *How many tasks in this state*: 0-N

2. **Working in multiple tasks**: If the user starts working in Task B while he
   is already working in Task A, Task A is automatically set to HALTED state.

    * Example: `dit workon A` + `dit workon B` implies "A is halted; user starts
      working on B".

3. **Limited working history**: If the user switches the current working task
   multiple times in sequence, he should be able to resume the previous tasks in
   reverse order easily (using the `git resume` command). This can be done by
   keeping a stack with tasks in halted state.

    * Example: `dit workon A` + `dit switchto B` + `dit switchto C` +
               `dit conclude C` + `dit resume` + `dit conclude B` +
               `dit resume` + `dit conclude A` should work properly.

4. **List of halted tasks**: The same stack that was used to solve the previous
   problem can be used here to make the access to the list of halted tasks
   easier and practible.

## Specification

The `dit` commands should work as follows:

1. **new**: Creates a task and set its state to `TODO`. You will be prompted for
   the "description" if it is not provided.
2. **workon**: Set task state to CURRENT and starts its clocking. If there is
   some task in CURRENT state before running this command, the old task state is
   set to HALTED.
3. **halt**: Set the task state to `HALTED` and stops its clocking. If task is in
   CURRENT state, stops clocking it.
4. **append**: Undoes the previous halt. If there is some task in CURRENT state
   before running this command, no action is done.
5. **cancel**: Undoes the previous workon.
6. **resume**: Set the state of the previous halted task to CURRENT and
   continues its clocking. If there is some task in CURRENT state before running
   this command, no action is done.
7. **switchto**: same as halt followed by workon
7. **conclude**: Set the state to `CONCLUDED` and stops its clocking.

The following commands should be removed:

1. **switchback**: Unnecessary, use `switchto task-name` intead.
