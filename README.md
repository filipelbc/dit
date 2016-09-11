# dit

Command line work time tracking and todo list

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

  new <name> [-d "description"]
    Creates a new task.

  workon <id> | <name> | --new, -n <name> [-d "description"]
    Clocks in the specified task.
    --new, -n
      Same as 'new' followed by 'workon'.

  halt [<id> | <name>]
    Clocks out of the current task or the specified one.

  switchto <id> | <name> | --new, -n <name> [-d "description"]
    Same as 'halt' followed by 'workon'.

  conclude [<id> | <name>]
    Concludes the current task or the specified one. Note that there is a
    implicit 'halt'.

  status [<gid> | <gname>]
    Prints an overview of the situation for the specified group, subgroup,
    or task. Exports current task or subgroup unless something is specified.

  list
    This is a convenience alias for 'export', with "--output stdout".

  export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"] [<gid> | <gname>]
    Exports data to the specified format. Exports current subgroup unless
    something is specified.
    --concluded, -a
      Include concluded tasks in the listing.
    --all, -a
      Exports all groups and subgroups.
    --verbose, -v
      More information is printed.
    --output, -o
      File to which to export. Defaults to "stdout".
      Format is deduced from file extension if present.

<name>: ["group-name"/]["subgroup-name"/]"task-name"
  "a"
      task "a" in current group/subgroup
  "b/a"
      task "a" in subgroup "b" in current group
  "c/b/a"
      task "a" in subgroup "b" in group "c"

  Note that "b" and "c" can be empty strings.

<id>: --id, -i ["group-id"/]["subgroup-id"/]"task-id"
  "a"
      task "id a" in current subgroup in current group
  "b/a"
      task "id a" in subgroup "id b" in current group
  "c/b/a"
      task "id a" in subgroup "id b" in group "id c"

  Note that "b" and "c" can be empty strings, which map to "id 0".

<gname>: "group-name"[/"subgroup-name"][/"task-name"]
  "a"
      group "a"
  "a/b"
      subgroup "b" in group "a"
  "a/b/c"
      task "c" in subgroup "b" in group "a"

  Note that "a" and "b" can be empty strings, which means the same as ".".

<gid>: --id, -i "group-id"[/"subgroup-id"][/"task-id"]
  "a"
      group "id a"
  "a/b"
      subgroup "id b" in group "id a"
  "a/b/c"
      task "id c" in subgroup "id b" in group "id a"

  Note that "a" and "b" can be empty strings, which are mapped to "id 0".
```
