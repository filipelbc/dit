[![Build Status](https://travis-ci.org/filipelbc/dit.svg?branch=master)](https://travis-ci.org/filipelbc/dit)

# dit

A CLI work time tracking tool.

## Installation

```
make install
```

To use bash completion, install with:
```
make install-completion
```

## Usage

```
Usage: dit [--verbose, -v] [--directory, -d "path"] <command>

  --directory, -d
    Specifies the directory where the tasks are stored. If not specified, the
    closest ".dit" directory in the tree is used. If not found, "~/.dit" is
    used. The selected directory will be refered to as "dit directory".

  --verbose, -v
    Prints detailed information of what is being done.

  --help, -h
    Prints this message and quits.

  --check-hooks
    Stop with error when hook process fails.

  --no-hooks
    Disable the use of hooks.

  Workflow <command>'s:

    new [--fetch, -f] <name> ["title"]
      Creates a new task. You will be prompted for the "title" if it is
      not provided.
      --fetch, -n
        Use data fetcher plugin.

    workon <id> | <name> | --new, -n [--fetch, -f] <name> ["title"]
      Starts clocking the specified task. If already working on a task, nothing
      is done. Sets the CURRENT and PREVIOUS tasks.
      --at, -a "date"
        Use the datetime given by "date" instead of now.
      --new, -n
        Same as "new" followed by "workon".

    halt
      Stops clocking the CURRENT task.
      --at, -a "date"
        Use the datetime given by "date" instead of now.

    append
      Undoes the previous "halt".

    cancel
      Undoes the previous "workon" (but the CURRENT task is not changed back).

    resume
      Same as "workon CURRENT".

    switchto <id> | <name> | --new, -n [--fetch, -f] <name> ["title"]
      Same as "halt" followed by "workon".

    switchback
      Same as "halt" followed by "workon PREVIOUS". If there is no PREVIOUS
      task, nothing is done.

    conclude [<id> | <name>]
      Concludes the CURRENT task or the selected one. Implies a "halt". It may
      set the CURRENT and/or PREVIOUS tasks.

  Listing <command>'s:

    export [--all, -a] [--concluded, -c] [--compact, -z]
           [--output, -o "file"] [--format, -f "format"] [<gid> | <gname>]
      Prints most information of the CURRENT subgroup or the selected one.
      --all, -a
        Select all groups and subgroups.
      --concluded, -c
        Include concluded tasks.
      --compact, -z
        Make the output more compact.
      --output, -o "file-name"
        File to which to write. Defaults to "stdout".
      --format, -f "format"
        Format to use. If not provided, the format is deduced from the file
        extension if present, else it defaults to dit's own format.

      For a given format, dit will try to use an external exporter plugin
      first. It will fallback to an internal exporter if possible or fail if
      none found.

    list
      This is a convenience alias for "export --output stdout --format dit".

    status
      Prints an overview of the data for the CURRENT and PREVIOUS tasks.

    Note that these commands also accept the following options:
    --verbose, -v
      More information is shown.
    --sum, -s
      Show the overall time spent on the listed tasks.
    --from "date"
      Only consider tasks and log entries from the given date on.
    --to "date"
      Only consider tasks and log entries up to the given date.
    --where, -w "property-name" "property-value"
      Only consider tasks that have the given property with the given value.
      Note that the value can be a regular expression.

  Task editing <command>'s:

    fetch <name>
      Use data fetcher plugin.

    move [--fetch, -f] <name> <name>
      Rename task or change its group and/or subgroup.
      --fetch, -f
        Use data fetcher plugin after moving.

    note [--task, -t <name> | <id>] ["text"]
      Adds a note to the CURRENT task or the specified one. You will be
      prompted for the "text" if it is not provided.

    set [--task, -t <name> | <id>] ["name" ["value"]]
      Sets a property for the CURRENT task or the specified one. You will be
      prompted for the "name" and "value" if they're not provided.

    edit [<name> | <id>]
      Opens the specified task for manual editing. Uses CURRENT task or the
      specified one. It will look in environment variables $VISUAL and $EDITOR
      for a text editor to use and if none is found it will do nothing.

  Other <command>'s:

    rebuild-index
      Rebuild the ".index" file. For use in case of manual modification of the
      contents of the dit directory.

  Plugins:

    Data fetcher:
      This allows placing a script named ".fetcher" in the directory
      of a group or subgroup, which will be used for fetching data for the task
      from an external source. It will be called in the following manner:
        "$ .fetcher dit-directory group subgroup task"
      It should save the fetched data in the file:
        "dit-directory/group/subgroup/task.json"

    Exporter:
      This allows specifying custom formats for the export command.
      The plugin should be installed as a Python module whose name has the
      following format "dit_Xexporter" where "X" will be the format specified
      by "--format X" in the export command call.
      The following methods should be available in the module:
        - setup(file, options)
        - begin()
        - end()
        - group(group, group_id)
        - subgroup(group, group_id, subgroup, subgroup_id)
        - task(group, group_id, subgroup, subgroup_id, task, task_id, data)

    Hooks:
      Hooks are scripts that can be called before and after a command. The
      following hooks are available:
        - "before": called before any command
        - "(before|after)_write": called before/after any command that modifies
                                  some task file (non-listing commands)
        - "(before|after)_read": called before/after any readonly command
                                 (listing commands)
        - "after": called after any command is executed successfully.
      The script should be installed in the ".hooks" directory in your dit
      directory and it will be called in the following manner:
        "$ hook-name dit-directory command-name"

  Clarifications:

  When mandatory arguments are not provided, you will be prompted to provide
  them.  This will either be done by opening a  text editor or with a simple
  CLI prompt. The editor will be used if either the $VISUAL or $EDITOR
  environment variable is set.

  <name>: [["group-name"/]"subgroup-name"/]"task-name" | CURRENT | PREVIOUS

  <gname>: "group-name"[/"subgroup-name"[/"task-name"]] | CURRENT | PREVIOUS

  CURRENT is a reference to the most recent task that received a "workon"
  and has not been "concluded". PREVIOUS is a reference to the second most
  recent.

  Note that a "*-name" must begin with a letter to be valid. Group- and
  subgroup-names can be empty or a ".", which means no group and/or subgroup.

  Also note that CURRENT and PREVIOUS are not valid arguments for the command
  "new".

  <id>: [["group-id"/]"subgroup-id"/]"task-id"

  <gid>: "group-id"[/"subgroup-id"[/"task-id"]]
```
