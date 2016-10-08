[![Build Status](https://travis-ci.org/filipelbc/dit.svg?branch=master)](https://travis-ci.org/filipelbc/dit)

# dit

A command line work time tracker and task list management system.

## Installation

```
make install
```

## Usage

```
dit [--verbose, -v] [--directory, -d "path"] <command>

--directory, -d
  Specifies the directory where the tasks are stored. If not specified, the
  closest ".dit" directory in the tree is used. If not found, '~/.dit' is
  used.

--verbose, -v
  Prints detailed information of what is being done.

--rebuild-index
  Rebuild the INDEX file. For use in case of manual modification of the
  contents of "--directory".

--help, -h
  Prints this message and quits.

Workflow <command>'s:

  new <name> [-: "description"]
    Creates a new task. You will be prompted for the "description" if it is
    not provided.

  workon <id> | <name> | --new, -n <name> [-: "description"]
    Starts clocking the specified task. Sets PREVIOUS if selected task is
    different from CURRENT one. Sets CURRENT task.
    --new, -n
      Same as 'new' followed by 'workon'.

  halt [<id> | <name>]
    Stops clocking the CURRENT task or the specified one. Sets CURRENT to
    halted.

  append [<id> | <name>]
    Undoes the previous 'halt ...'.

  cancel [<id> | <name>]
    Cancels the clocking of the CURRENT task or the selected one.
    (The intention is to undo the previous 'workon', but not all of its
     side-effects are undoable.)

  resume
    Same as 'workon CURRENT'.

  switchto <id> | <name> | --new, -n <name> [-: "description"]
    Same as 'halt' followed by 'workon ...'.

  switchback
    Same as 'halt' followed by 'workon PREVIOUS'.

  conclude [<id> | <name>]
    Concludes the CURRENT task or the selected one. Implies a 'halt'.

Printing <command>'s:

  export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"] [<gid> | <gname>]
    Prints most information of the CURRENT subgroup or the selected one.
    --concluded, -a
      Include concluded tasks.
    --all, -a
      Select all groups and subgroups.
    --verbose, -v
      All information is exported.
    --output, -o
      File to which to write. Defaults to "stdout". Format is deduced from
      file extension if present.

  list
    This is a convenience alias for 'export', with "--output stdout".

  status [<gid> | <gname>]
    Prints an overview of the data for the CURRENT task or subgroup, or
    for the selected one.

Task editing <command>'s:

  note [<name> | <id>] [-: "text"]
    Adds a note to the CURRENT task or the specified one.

  set [<name> | <id>] [-: "name" ["value"]]
    Sets a property for the CURRENT task or the specified one.

  edit [<name> | <id>]
    Opens the specified task for manual editing. Uses CURRENT task if none is
    specified. If $EDITOR environment variable is not set it does nothing.

"-:"
  Arguments preceeded by "-:" are necessary. If omited, then: a) if the
  $EDITOR environment variable is set, a text file will be open for
  editing the argument; b) otherwise, a simple prompt will be used.

<name>: [["group-name"/]"subgroup-name"/]"task-name" | CURRENT | PREVIOUS

<gname>: "group-name"[/"subgroup-name"[/"task-name"]] | CURRENT | PREVIOUS

Note that a "-name" must begin with a letter to be valid. Group- and
subgroup-names can be empty or a dot, which means no group and/or subgroup.

Also note that CURRENT and PREVIOUS are not valid arguments for the command
'new'.

<id>: [["group-id"/]"subgroup-id"/]"task-id"

<gid>: "group-id"[/"subgroup-id"[/"task-id"]]
```
