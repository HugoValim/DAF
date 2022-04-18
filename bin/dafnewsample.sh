#!/bin/bash


pretty-print()
# No arguments.
# Enable colors (see man tput and man terminfo).
{
    # These are global
    NO_COLOR=$'\E[39;49m'
    BLACK=$'\E[30m'
    RED=$'\E[31m'
    GREEN=$'\E[32m'
    YELLOW=$'\E[33m'
    BLUE=$'\E[34m'
    PURPLE=$'\E[35m'
    CYAN=$'\E[36m'
    WHITE=$'\E[37m'
}

new_setup()
{
    
    mkdir $1
    chmod -R 777 $1
    cd $1
    daf.init -a
}

kill_others()
{
    # Kill all daf.gui and daf.live instances
    ps axu | grep daf_gui.py | awk {'print $2'} | head -n -1 | xargs kill -9
    ps axu | grep live_view.py | awk {'print $2'} | head -n -1 | xargs kill -9
}

usage()
{
    echo "Usage: $(basename "$0") <dir name> [subcommands]"
    echo "-k, --kill - Kill other running GUIs interface"
    echo
}

main()
# See usage
{
    #pretty-print

    case "${2:-}" in
        '-k'|'--kill') kill_others;;
    esac

    case "${1:-}" in
        '-h'|'--help') usage "$@";;
        *) new_setup "$@";;
    esac
}

main "$@"