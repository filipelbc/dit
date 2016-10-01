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
  Specifies the directory where the tasks are stored. Defaults to '~/.dit'.

--verbose, -v
  Prints detailed information of what is being done.

--rebuild-index
  Rebuild the INDEX file. For use in case of manual modification of the
  contents of "--directory".

--help, -h
  Prints this message and quits.

<command>:

  new <name> [-: "description"]
    Creates a new task. You will be prompted for the "descroption" if it is
    not provided.

  workon <id> | <name> | --new, -n <name> [-: "description"]
    Clocks in the specified task.
    --new, -n
      Same as 'new' followed by 'workon'.

  halt [<id> | <name>]
    Clocks out of the current task or the specified one.

  switchto <id> | <name> | --new, -n <name> [-: "description"]
    Same as 'halt' followed by 'workon'.

  conclude [<id> | <name>]
    Concludes the current task or the selected one. Note that there is a
    implicit 'halt'.

  status [<gid> | <gname>]
    Prints an overview of the data for the current task or subgroup, or
    for the selected one.

  list
    This is a convenience alias for 'export', with "--output stdout".

  export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"] [<gid> | <gname>]
    Prints most of the data for the current subgroup or the selected one.
    --concluded, -a
      Include concluded tasks.
    --all, -a
      Select all groups and subgroups.
    --verbose, -v
      All information is exported.
    --output, -o
      File to which to write. Defaults to "stdout". Format is deduced from
      file extension if present.

  note [<name> | <id>] [-: "text"]
    Adds a note to the current task or the specified one.

  set [<name> | <id>] [-: "name" ["value"]]
    Sets a property for the current task or the specified one. The format
    of properties are pairs of strings (name, value).

  edit [<name> | <id>]
    Opens the specified task for manual editing. Uses current task if none is
    specified. If $EDITOR environment variable is not set it does nothing.

"-:"
  Arguments preceeded by "-:" are necessary. If omited, then: a) if the
  $EDITOR environment variable is set, a text file will be open for
  editing the argument; b) otherwise, a simple prompt will be used.

<name>: ["group-name"/]["subgroup-name"/]"task-name"
  "a"
      task "a" in current group/subgroup
  "b/a"
      task "a" in subgroup "b" in current group
  "c/b/a"
      task "a" in subgroup "b" in group "c"

  Note that "b" and "c" can be empty strings.

<id>: ["group-id"/]["subgroup-id"/]"task-id"
  "a"
      task "id a" in current subgroup in current group
  "b/a"
      task "id a" in subgroup "id b" in current group
  "c/b/a"
      task "id a" in subgroup "id b" in group "id c"

<gname>: "group-name"[/"subgroup-name"][/"task-name"]
  "a"
      group "a"
  "a/b"
      subgroup "b" in group "a"
  "a/b/c"
      task "c" in subgroup "b" in group "a"

  Note that "a" and "b" can be empty strings, which means the same as ".".

<gid>: "group-id"[/"subgroup-id"][/"task-id"]
  "a"
      group "id a"
  "a/b"
      subgroup "id b" in group "id a"
  "a/b/c"
      task "id c" in subgroup "id b" in group "id a"
```
