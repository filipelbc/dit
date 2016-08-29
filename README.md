# dit

Command line work time tracking and todo list

## Usage

```
  dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. Defaults to '~/.dit'.

  --verbose, -v
    Prints detailed information of what is done.

  --help, -h
    Prints this message and quits.

  <command>:

    new <name> [-d "description"]
      Creates a new task.

    workon <id> | --new, -n <name> [-d "description"]
      Clocks in the specified task.
      --new, -n
        Same as 'new' followed by 'workon'.

    halt [<id> | <name>]
      Clocks out of the specified task or the current one.

    switchto <id> | --new, -n <name> [-d "description"]
      Same as 'halt' followed by 'workon'

    conclude [<id> | <name>]
      Concludes the specified task or the current one. Note that there is an
      implicit 'halt'

    status [<gid> | <gname>]
      Prints an overview of the situation for the specified group, subgroup,
      or task. If none specified, the current task is used.

    list
      This is a convenience alias for 'export'

    export [--concluded, -c] [--all, -a] [--verbose, -v] [--output, -o "file"]
        [<gid> | <gname>]
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

  <id>: --id, -i ["group-id"/]["subgroup-id"/]"task-id"

      Uses current group and current subgroup if they are not specified.

  <gname>: "group-name"[/"subgroup-name"][/"task-name"]

  <gid>: --id, -i "group-id"[/"subgroup-id"][/"task-id"]
```
