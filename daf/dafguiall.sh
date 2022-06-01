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

open_guis()
{
    daf.gui
    daf.live
}

usage()
{
    echo "Usage: $(basename "$0")"
    echo "Opens all DAF's GUIs"
    echo
}

main()
# See usage
{
    #pretty-print
    case "${1:-}" in
        '-h'|'--help') usage "$@";;
        *) open_guis "$@";;
    esac
}

main "$@"