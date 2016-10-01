
This is the development guide to **Dit**, a command line work time tracker and task list management system.

What follows is a description of the states of the system and desired behavior of the commands.

# States

#### INDEX

This associates a code to a task and is set by `new`.

#### CURRENT

This is the task on which the user is working (which means that the user has started clocking)

#### PREVIOUS

This is the last task on which the user worked (which means that the user has stopped clocking)

# Time tracking commands

These are the commands for tracking time and managing the flow between the various tasks.

#### new

* **Function:** registers a new task.

* **Side-effect:** modifies `INDEX`

#### workon

* **Function:** starts clocking a task.

* **Side-effect:** adds a `logbook-in` entry to a task.

* **Side-effect:** sets `CURRENT`

#### **TODO** cancel

* **Function:** cancels the previous `workon`

* **Side-effect:** removes the last `logbook-in` entry from the task.

* **Side-effect:** clears `CURRENT`

#### halt

* **Function:** stops clocking a task.

* **Side-effect:** adds a `logbook-out` entry to the task.

* **Side-effect:** clears `CURRENT`

* **Side-effect:** sets `PREVIOUS`

#### **TODO** cancel

* **Function:** cancels the previous `halt`

* **Side-effect:** removes the last `logbook-out` entry from the task.

* **Side-effect:** sets `CURRENT`

#### conclude

* **Function:** sets a task as concluded

* **Implies:** a `halt`

#### **TODO** resume

* **Function:** same as a `workon` on the `PREVIOUS` task

#### switchto

* **Function:** same as a `halt` on the `CURRENT` task followed by a `workon`

#### **TODO** switchback

* **Function:** stops clocking the `CURRENT` task, starts clocking the `PREVIOUS` task

* **Side-effect:** swaps `CURRENT` and `PREVIOUS`

# Future

`CURRENT` and `PREVIOUS` should be "stack-like".
