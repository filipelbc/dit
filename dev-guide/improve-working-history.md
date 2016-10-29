# Reimplement Working History

## Problem statement

The current implementation has the following problems:

1. **Task states specification**: There is no specification of the possible
   states of Task and the transitions between them.

2. **Working in multiple tasks**: The user is able to work on multiple tasks at
   the same time. This feature is useless and adds unnecessary complexity to the
   system.
    * Example: (simplified syntax)
    ```
    $ dit workon A
    $ dit workon B
    --> user is working on both A and B
    ```

3. **Limited working history**: Assume that the user started working in Task A.
   Then, while working on Task A, he was interrupted, which caused him to switch
   to Task B. Then he was interrupted again, causing him to switch to Task C. In
   the current implementation, the Task A will be lost in the working history.
   That is, he will be able to switch back Task B after completing Task C, but will
   not be able to switch back Task A after completing Task B.

    * Example: (simplified syntax)
    ```
    $ dit workon A
    $ dit switchto B
    $ dit switchto C
    $ dit conclude
    --> CURRENT is C and PREVIOUS is B
    $ dit switchback
    --> CURRENT is B and PREVIOUS is C
    $ dit conclude
    $ dit switchback
    --> CURRENT is C and PREVIOUS is B
    --> Fail the intended purpose, will try to workon C.
    ```

4. **List of halted tasks**: The user should be able to see the list of halted
   tasks (through the `dit status` command). In the current implementation, the
   only way to do that is by iterating over all the task files, which is not
   conveninent.

## Proposed solution

1. **Task states specification**: Each task should be in one of the following
   states:

    1. **TODO**:
        * *Previous state*: None.
        * *When does a task assume this state?*: At the moment of creation.
        * *How many tasks in this state*: N >= 0.
        * A task in this state has an empty logbook.

    2. **DOING**:
        * *Previous state*: Any of the other three states.
        * *When does a task assume this state*: When the user starts working
          in the task.
        * *How many tasks in this state*: 0 or 1.
        * A task in this state has the most recent logbook entry `in` field set,
        but not the `out` field.

    3. **HALTED**:
        * *Previous state*: DOING state.
        * *When does a task assume this state*: When the user halts his work
          on the task.
        * *How many tasks in this state*: N >= 0.
        * A task in this state has the most recent `logbook` entry `in` and
          `out` fields set.

    4. **CONCLUDED state**:
        * *Previous state*: Any of the other three states.
        * *When a task assume this state*: When the user `$ dit conclude` the task.
        * *How many tasks in this state*: N >= 0.
        * A task in this state has the `concluded_at` field set.

    Note that the states can always be computed from the task data.

2. **Working in multiple tasks**: The system should enforce the correct use of
the commands

    * Example 1:
    ```
    $ dit workon A
    $ dit workon B
    --> Error: cannot workon on two tasks at the same time
    ```
    * Example 2:
    ```
    $ dit workon A
    $ dit switchto B
    --> Ok: A is halted.
    ```

3. **Limited working history**: If the user switches the current working task
   multiple times in sequence, he should be able to resume the previous tasks in
   reverse order easily (using the `git resume` command). This can be done by
   keeping a stack with tasks in halted state.

    * Example: (simplified syntax)
    ```
    $ dit workon A
    $ dit switchto B
    $ dit switchto C
    --> PREVIOUS: AB, CURRENT: C
    $ dit conclude
    --> PREVIOUS: AB, CURRENT: None
    $ dit resume (OR switchback)
    --> PREVIOUS: A, CURRENT: B
    $ dit conclude
    --> PREVIOUS: A, CURRENT: None
    $ dit resume (OR switchback)
    --> PREVIOUS: None, CURRENT: A
    --> Working on task A!
    ```

4. **List of halted tasks**: The same stack that was used to solve the previous
   problem can be used here to make the access to the list of halted tasks
   easier.

## Specification

The mechanism for solving the problem is the use of a stack-controlled workflow.

### Stack structure:

1. **CURRENT**: this is the most recent task on which the user worked.
    * If there is a task in the DOING state, it will be this one.
    * This task will either be on the DOING or the HALTED stated.

2. **PREVIOUS**: This is a stack (first in last out) which will contain all
   task in the HALTED state, with the possible exception of the task in
   CURRENT.

### Commands

This describes mainly the aspects that relates to the functioning of the
stack-controlled workflow.

The `dit` commands should work as follows:

1. **workon T**: starts clocking task T and sets CURRENT to T.
    * If there was a CURRENT task in HALTED state, it is moved to the top of the
      PREVIOUS stack.
    * If there was a CURRENT task in DOING state, nothing is done.

2. **halt**: stops clocking CURRENT.

3. **append**: if the CURRENT task is halted, this command undoes the `halt`.

4. **conclude [T]**: removes the task T or CURRENT from the PREVIOUS stack (not
   necessarily from the top) or from CURRENT, `halt`ing it first.

5. **cancel**: undoes the previous `workon`.
    * The task on which the user was working will remain as the CURRENT.

6. **resume**: same as `workon CURRENT`.
    * If there is not CURRENT, it is the same as `switchback`.

7. **switchto T**: same as `halt` followed by `workon T`.

8. **switchback**: same as `halt` followed by `workon PREVIOUS.TOP`.

# Future: Timecard feature

If a task is set to be a timecard, it will not be part of the stack-controlled
workflow.

Two commands will be able to affect this kind of task: `enter` and `leave`.

* Note that it would still be possible to compute its state.
