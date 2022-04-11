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


usage()
{
    echo "Usage: "
    echo
    echo "${NO_COLOR}-k ${BLACK} - set prompt color to black"
    echo "${NO_COLOR}-r ${RED} - set prompt color to red"
    echo "${NO_COLOR}-g ${GREEN} - set prompt color to green"
    echo "${NO_COLOR}-y ${YELLOW} - set prompt color to yellow"
    echo "${NO_COLOR}-b ${BLUE} - set prompt color to blue"
    echo "${NO_COLOR}-p ${PURPLE} - set prompt color to purple"
    echo "${NO_COLOR}-c ${CYAN} - set prompt color to cyan"
    echo "${NO_COLOR}-w ${WHITE} - set prompt color to white"
}


set_color()
{
    COLOR=$1
    case $COLOR in
        '-k')
            PS1="\[\033[1;30m\]DAF> \[\033[0m\]"
            ;;
        '-r')
            PS1="\[\033[1;31m\]DAF> \[\033[0m\]"
            ;;
        '-g')
            PS1="\[\033[1;32m\]DAF> \[\033[0m\]"
            ;;
        '-y')
            PS1="\[\033[1;33m\]DAF> \[\033[0m\]"
            ;;
        '-b')
            PS1="\[\033[1;34m\]DAF> \[\033[0m\]"
            ;;
        '-p')
            PS1="\[\033[1;35m\]DAF> \[\033[0m\]"
            ;;
        '-c')
            PS1="\[\033[1;36m\]DAF> \[\033[0m\]"
            ;;
        '-w')
            PS1="\[\033[1;37m\]DAF> \[\033[0m\]"
            ;;
        *)
            PS1="\[\033[1;36m\]DAF> \[\033[0m\]"
            ;;
    esac
}

main()
# See usage
{
    pretty-print
    # Do not raise an error if $1 is not set.
    case "${1:-}" in
        '-k'|'-r'|'-g'|'-y'|'-b'|'-p'|'-c'|'-w') set_color "$@";;
        *) usage "$@";;
    esac
}

main "$@"