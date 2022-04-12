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
    echo "Usage: $(basename "$0")"
    echo
    echo "${WHITE} SUPPORT"   
    echo "${WHITE} daf.init ${NO_COLOR} - Initialize DAF, creating the required files"
    echo "${WHITE} daf.reset ${NO_COLOR} - Reset configurations to default"
    echo "${WHITE} daf.prompt ${NO_COLOR} - Set DAF prompt, must be used with source"
    echo "${WHITE} daf.setup ${NO_COLOR} - Manage DAF setups"
    echo
    echo "${PURPLE} GUIs"
    echo "${PURPLE} daf.gui ${NO_COLOR} - Launch DAF's main GUI"
    echo "${PURPLE} daf.live ${NO_COLOR} - Launch DAF's live plot"
    echo "${PURPLE} daf.rmap ${NO_COLOR} - Lanch a graphical resciprocal space map"
    echo
    echo "${GREEN} CONFIGURE THE EXPERIMENT"
    echo "${GREEN} daf.expt ${NO_COLOR} - Set sample, energy and reference vectors"
    echo "${GREEN} daf.mode ${NO_COLOR} - Set the mode of operation"
    echo "${GREEN} daf.bounds ${NO_COLOR} - Set diffractometer angles bounds"
    echo "${GREEN} daf.cons ${NO_COLOR} - Function to constrain angles and pseudo-angles during the experiment"
    echo "${GREEN} daf.ub ${NO_COLOR} - Set or calculate UB matrix from 2 or 3 reflections"
    echo "${GREEN} daf.mc ${NO_COLOR} - Manage counters to be used in scans"
    echo
    echo "${YELLOW} QUERY INFORMATION"
    echo "${YELLOW} daf.status ${NO_COLOR} - Show the experiment status"
    echo "${YELLOW} daf.wh ${NO_COLOR} - Show the current position in the reciprocal space, angles and pseudo-angles"
    echo "${YELLOW} daf.ca ${NO_COLOR} - Calculate the diffractometer angles needed to reach a given HKL position"
    echo
    echo "${BLUE} MOVE MOTORS"
    echo "${BLUE} daf.amv ${NO_COLOR} - Move the diffractometer motors by direct change in the angles"
    echo "${BLUE} daf.ramv ${NO_COLOR} - Move the diffractometer motors by a relative change in the angles"
    echo "${BLUE} daf.mv ${NO_COLOR} - Move in the reciprocal space by giving a HKL position"
    echo
    echo "${CYAN} SCANS"
    echo "${CYAN} daf.scan ${NO_COLOR} - Perform a scan in HKL coordinates"
    echo "${CYAN} daf.rfscan ${NO_COLOR} - Perform a scan in HKL coordinates by providing a csv file generated by daf.scan"
    echo "${CYAN} daf.ascan ${NO_COLOR} - Perform an absolute scan in one of the diffractometer motors"
    echo "${CYAN} daf.a2scan ${NO_COLOR} - Perform an absolute scan using two of the diffractometer motors"
    echo "${CYAN} daf.a3scan ${NO_COLOR} - Perform an absolute scan using three of the diffractometer motors"
    echo "${CYAN} daf.a4scan ${NO_COLOR} - Perform an absolute scan using four of the diffractometer motors"
    echo "${CYAN} daf.a5scan ${NO_COLOR} - Perform an absolute scan using five of the diffractometer motors"
    echo "${CYAN} daf.a6scan ${NO_COLOR} - Perform an absolute scan using six of the diffractometer motors"
    echo "${CYAN} daf.lup ${NO_COLOR} - Perform an relative scan in one of the diffractometer motors"
    echo "${CYAN} daf.dscan ${NO_COLOR} - Perform an relative scan in one of the diffractometer motors"
    echo "${CYAN} daf.d2scan ${NO_COLOR} - Perform an relative scan in two of the diffractometer motors"
    echo "${CYAN} daf.d3scan ${NO_COLOR} - Perform an relative scan in three of the diffractometer motors"
    echo "${CYAN} daf.d4scan ${NO_COLOR} - Perform an relative scan in four of the diffractometer motors"
    echo "${CYAN} daf.d5scan ${NO_COLOR} - Perform an relative scan in five of the diffractometer motors"
    echo "${CYAN} daf.d6scan ${NO_COLOR} - Perform an relative scan in six of the diffractometer motors"
    echo "${CYAN} daf.mesh ${NO_COLOR} - Perform a mesh scan using two of the diffractometer motors"
    echo
}

main()
# See usage
{
    pretty-print
    usage
}

main