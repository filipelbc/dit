# Time Tracking Tools

## toogl

Platform: Web, Desktop, iOS, Android, Windows Phone, Linux.

* Automatic (start/button) and manual (start/stop time) mode.
* Daily/Weekly views.
* Tasks grouped by projects.
* Dashboard:
    * total of work hours in each day of the week
    * total of work hours in each project durring the week
* Report (dashboard with filters).
* Tags.
* Import/Export.

## everhour

Platform: Web.

* Needs integration with Asana, Basecamp, Pivotal Tracker, Trello, or Github.

## paydirt

Platform: Web.

* Tasks grouped by clients.
* Chrome extension.
* Dashboard with hours logged/billable hours/unbillable hours/billable value per
  day.

## timely

Platform: Web, iOS, Apple Watch.

* Daily/Week views.
* Tasks grouped by projects.
* Google Calendar integration (tasks in the app are automatically imported).
* Planned time.
* Reports.

## orgmode

TODO.

## timetrap

Platform: cli.

* Open source.
* Coded in ruby.
* Each task is a timesheet.
* The `switchto` (sheet) does not imply `workon` (in).
* Each work session in a given timesheet has an individual note.
* Natural language times:
    * `t out --at "in 30 minutes"`
    * `t edit --start "last monday at 10:30am"`
    * `t edit --end "tomorrow at noon"`
    * `t display --start "10am" --end "2pm"`
    * `t i -a "2010-11-29 12:30:00"`
* Export (text, csv, ical, json, ids).
* Custom output formatters.
* Autosheets feature (default sets current task from a `.timetrap-sheet` file in
  the current directory).
* Bash/Zsh completion.
* Use sqlite as database.

## taskwarrior

Platform: cli.

* Open source.
* Coded in cpp.
* Task priorities.
* Task age, instead of creation date.
* Hooks.
* Task server (daemon) to sync tasks between different machines.
* Tags.

## ti

Platform: cli.

* Open source.
* Natural language times:
    * 30minutes ago
    * 30mins ago
    * 10seconds ago
    * 10s ago
* Commands: on, fin, status, log, note, tag.
* Tags.

## timed

Platform: cli.

* Open source.
* Coded in python.
* Commands: start, stop, status, summary, parse.
* Bash completion.

## t

Platform: cli.

* Open source.
* Coded in python.
* Manage text files. Each file is a list of tasks.

## utt

Platform: cli.

* Open source.
* Coded in python.

## timetracker

Platform: cli.

* Open source.
* Coded in perl.
* Git, IRC, and RT support.

## ttrack

Platform: cli.

* Open source.
* Coded in python.
* Use sqlite as database.
* Stores command history through the `.timetrackhistory` file.
* Interactive mode (all commands run in a single instance).
* Tags.
* Retrospective times (stop last Friday at 17:35).
