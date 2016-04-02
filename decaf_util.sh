#!/usr/bin/env bash

VER='1.0'

#######################################################################
# Title      :    DECaF - Component Utils
# Author     :    PG DECaF
# Date       :    2016-02-09
# Requires   :    dialog, bash 4
# Category   :    manages DECaF Orchestrator Plugins
#######################################################################
#
# Description
# Note:
#   - Simplifies developing and operating
#     the DECaF Orchestration Framework.
#
#######################################################################
#
# TODOs:
#  introduce logging
#  rewrite get_component_status to use daemon status
#
#######################################################################



#######################################################################
#
#  INITIALIZATION
#
#######################################################################
# install dialog if not installed
if ! hash dialog 2>/dev/null; then
    clear
    echo "Dialog is not installed."
    read -p "Do you wish to install dialog? (Y/n)" -n 1 -r
    echo # (optional) move to a new line
    if [[ ${REPLY} =~ ^[Yy]$ ]] || [ -z ${REPLY} ]
    then
        echo "Please provide root privileges to install."
        echo "\$ sudo apt-get -y install dialog"
        sudo apt-get -y install dialog
    else
        exit
    fi
fi

# install sqlite3 if not installed
if ! hash sqlite3 2>/dev/null; then
    clear
    echo "sqlite3 is not installed."
    read -p "Do you wish to install sqlite3? (Y/n)" -n 1 -r
    echo # (optional) move to a new line
    if [[ ${REPLY} =~ ^[Yy]$ ]] || [ -z ${REPLY} ]
    then
        echo "Please provide root privileges to install."
        echo "\$ sudo apt-get -y install sqlite3"
        sudo apt-get -y install sqlite3
    else
        exit
    fi
fi

# init some global variables
_temp="/tmp/answer.$$"
SCRIPT=$(readlink -f "${0}")
BASEDIR=$(dirname ${SCRIPT})
BASENAME=$(basename "${SCRIPT}")
dialog > ${_temp} 2> /dev/null
DVER=`cat ${_temp} | head -1`
TITLE="DECaF - Component Utils (v.${VER})"
PW=""
DB_FILE="decaf_util.db"
CALL_ARRAY_LIST_MENU=()
DIALOG=${DIALOG=dialog}


# init default values
PID_DIR='/var/run/decaf'
CONFIG_DIR='/etc/decaf'
LOG_DIR='/var/log/decaf'
PROJECT_DIR="${BASEDIR}"

# init config DEFAULTS
EDITOR="/usr/bin/editor"
TAIL=""
LESS="less -R"


# read in config
#  1. search in BASEDIR
#  2. search in HOMEDIR
#  3. search in /etc/decaf/
#  4. copy sample config into current dir and use it
if [ -f ${BASEDIR}/.${BASENAME::-3}.cfg ]
then
    source ${BASEDIR}/.${BASENAME::-3}.cfg

elif [ -f ~/.${BASENAME::-3}.cfg ]
then
    source ~/.${BASENAME::-3}.cfg

elif [ -f /etc/decaf/.${BASENAME::-3}.cfg ]
then
    source /etc/decaf/.${BASENAME::-3}.cfg
else
    cp ${BASEDIR}/.${BASENAME::-3}.cfg.sample ${BASEDIR}/.${BASENAME::-3}.cfg
    source ${BASEDIR}/.${BASENAME::-3}.cfg
fi


declare -A components_dir
components_dir=(
	["storage"]=${PROJECT_DIR}"/components/decaf-storage"
	["specification"]=${PROJECT_DIR}"/components/decaf-specification"
	["masta"]=${PROJECT_DIR}"/components/decaf-masta/decaf_masta"
	["deployment"]=${PROJECT_DIR}"/components/decaf-deployment"
	["placement"]=${PROJECT_DIR}"/components/decaf-placement"
	["example_scaling"]=${PROJECT_DIR}"/components/example-scaling"
	["vnf_manager_adapter"]=${PROJECT_DIR}"/components/decaf-vnf-manager-adapter"
	["oscar"]=${PROJECT_DIR}"/components/decaf-oscar"
	["componentmanager"]=${PROJECT_DIR}"/components/decaf-componentmanager"
)

#
# creates an empty DB
#
if [ ! -f ${DB_FILE} ]
then
    cat /dev/null > ${DB_FILE}
    sqlite3 ${DB_FILE} "CREATE TABLE call  \
        (id INTEGER PRIMARY KEY,  \
        component TEXT,  \
        method TEXT,  \
        command TEXT,  \
        use_count INTEGER);"
fi

#
# call dispose to exit
# clears screen and clears python env
#
dispose() {
    ${DIALOG} --infobox "Disposing..." 0 0
    rm ${_temp} > /dev/null 2>&1
    unset PW
    #${DIALOG} --clear
    clear
    exit
}

# trap dispose SIGINT


ENV_ENABLED=1
if [ -f "${BASEDIR}/.env/bin/activate" ]; then
    source "${BASEDIR}/.env/bin/activate"
    ENV_ENABLED=0
fi


#######################################################################
#
#  FUNCTIONALITIES
#
#######################################################################

enable_env() {
    if ! ${ENV_ENABLED}; then
        if [ -f "${BASEDIR}/.env/bin/activate" ]; then
            source "${BASEDIR}/.env/bin/activate"
            ENV_ENABLED=0
        else
            ${DIALOG} --msgbox "Could not activate python environment!\n"  \
                "Please setup DECaF Environment first!\n\nCould not find \"${BASEDIR}/.env/bin/activate\"" 0 0
        fi
    fi
    return ${ENV_ENABLED}
}

setup_environment() {
    ${DIALOG} --backtitle "${TITLE}" --title "Setup DECaF Environment" --yesno  \
        "This will drop your database. Do you want to install all nessary packages for the DECaF Environment?\n"  \
        "This will among others install PostgreSQL, RabbitMQ and Python2.7." 0 0
    clear
    if [ ${?} == 0 ]
    then
        run_as_su "${BASEDIR}"/scripts/create_dirs.sh
        run_as_su "${BASEDIR}"/scripts/setup_development_environment.sh
        ${DIALOG} --msgbox "Setup DECaF Environment \ncompleted" 0 0
    fi
}

#
# inserts a call into the DB
#
db_insert() {
    component=$1
    method=$2
    arguments="${@:3}"
    arguments="${arguments/\'/\\\'}"

    sqlite3 ${DB_FILE} "INSERT INTO call (component, method, command, use_count) VALUES ('${component}', '${method}', '${arguments}', 0)";
}

#
# writes all calls from the DB into an array
# CALL_ARRAY_LIST_MENU
#
db_list() {

    ${DIALOG} --infobox "loading..." 0 0
    # empty return arrays
    CALL_ARRAY_LIST_MENU=()

    while IFS=$'\n' read -ra ROW
    do
        # match columns to variables
        id=$(echo "$ROW" | cut -d '|' -f1)
        component=$(echo "$ROW" | cut -d '|' -f2)
        method=$(echo "$ROW" | cut -d '|' -f3)
        arguments=$(echo "$ROW" | cut -d '|' -f4)

        # check if arguments is longer than 30
        if [[ ${#arguments} -gt 43 ]]
        then
            CALL_ARRAY_LIST_MENU+=(${id} "$(printf '%-20s %-20s %-40s...' "${component:0:20}" "${method:0:20}" "${arguments:0:40}")")
        else
            CALL_ARRAY_LIST_MENU+=(${id} "$(printf '%-20s %-20s %-43s' "${component:0:20}" "${method:0:20}" "${arguments}")")
        fi

    done< <(sqlite3 ${DB_FILE} "SELECT * FROM call ORDER BY use_count DESC")

    if [ ${#CALL_ARRAY_LIST_MENU[@]} == 0 ]
    then
        CALL_ARRAY_LIST_MENU+=(0 "No recent calls found (don't use me)")
    fi
}

#
# increment usage of a given call by id
#
db_increment() {
    id=$1

    sqlite3 ${DB_FILE} "UPDATE call SET use_count = use_count + 1 WHERE id = ${id}"
}

#
# gathers all rabbbitMQ endpoint for a given component
# returns endpoint separated with LF (\n)
#
list_endpoints() {
    component=$1

    sudo rabbitmqctl list_bindings | grep "^guest.*guest.decaf_${component}" | cut -d'.' -f3 | cut -d$'\t' -f1
}

#
# wrapps decaf-cli command
#
cli_call() {
    clear
    echo "decaf-cli call --json decaf_${1} ${2} ${3}"
    echo ""
    decaf-cli call --json decaf_${1} ${2} ${3}
    read -p "Press [Enter] key to resume..."
}

#
# wrapps decaf-cli command and DB call by id
#
cli_call_by_id() {
    id=$1

    ROW=$(sqlite3 ${DB_FILE} "SELECT * FROM call WHERE id = ${id}")

    id=$(echo "$ROW" | cut -d '|' -f1)
    component=$(echo "$ROW" | cut -d '|' -f2)
    method=$(echo "$ROW" | cut -d '|' -f3)
    arguments=$(echo "$ROW" | cut -d '|' -f4)

    db_increment ${id}

    clear
    echo "decaf-cli call --json ${component} ${method} ${arguments}"
    decaf-cli call --json decaf_${component} ${method} ${arguments}

    read -p "Press [Enter] key to resume..."
}

#
# asks the user to creates a new decaf-cli call
# afterwads it will be saved to db
# and executed
#
new_call() {

    while true
    do
        unset component

        # build component list with status
        i=0
        component_menu_list=()
        for component in "${!components_dir[@]}"
        do
            i=$((i + 1))
            component_menu_list+=(${component} "$(get_component_status_colored ${component})")
        done

        ${DIALOG} --backtitle "${TITLE}" --title " Custom Call"  \
            --colors  \
            --no-collapse    \
            --cancel-label "Back"  \
            --menu "select a component" 17 60 10  \
            "${component_menu_list[@]}" 2>${_temp}
        if [ ${?} != 0 ]; then return 1; fi

        component=$(cat ${_temp})

        # call next dialog and return if the call was successfull
        new_call_select_endpoint "${component}"

        if [ ${?} != 0 ]; then continue; fi
        return 0
    done
}

new_call_select_endpoint() {
    component=$1

        while true
        do
            unset endpoint

            # gather endpoint_list
            endpoint_menu_list=()
            endpoint_menu_list+=(custom "if the endpoint is not in the list")

            i=0
            while IFS=$'\n' read -ra ROW
            do
                i=$((i + 1))
                endpoint_menu_list+=("${ROW}" "")
            done< <(list_endpoints ${component})

            ${DIALOG} --backtitle "${TITLE}" --title " Custom Call - ${component}"  \
                --cancel-label "Back"  \
                --colors  \
                --no-collapse    \
                --menu "select an Endpoint" 0 0 15  \
                "${endpoint_menu_list[@]}" 2>${_temp}
            if [ ${?} != 0 ]; then return 1; fi
            endpoint=$(cat ${_temp})

            if [ ${endpoint} == "custom" ]
            then
                dialog --backtitle "${TITLE}" --title " Custom Call - ${component}"  \
                    --cancel-label "Back"  \
                    --inputbox "input endpoint description" 20 100 2>${_temp}
                if [ ${?} != 0 ]; then continue; fi
                if [ `cat ${_temp}` == "" ]
                then
                    dialog --backtitle "${TITLE}" --title " Custom Call - ${component}"  \
                        --msgbox "empty endpoints are not allowed :P" 0 0
                    continue
                fi
                endpoint=`cat ${_temp}`
            fi

            # call next dialog and return if the call was successfull
            new_call_select_arguments "${component}" "${endpoint}"
            if [ ${?} != 0 ]; then return 1; fi
            return 0
        done
}

new_call_select_arguments() {
    component=$1
    endpoint=$2

    ${DIALOG} --backtitle "${TITLE}" --title " Custom Call - ${component} - ${endpoint}"  \
        --cancel-label "Back"  \
        --ok-label "Call"  \
        --inputbox "input JSON formated argument data\nCAUTION: Do not use single quotes!" 20 100 2>${_temp}
    if [ ${?} != 0 ]; then return 1; fi
    arguments=$(cat ${_temp})

    db_insert ${component} ${endpoint} ${arguments}

    cli_call ${component} ${endpoint} "${arguments}"
    return 0
}

#
# recreate PostgreSQL Database
#
recreate_database() {
    ${DIALOG} --backtitle "${TITLE}" --title "Recreate Database" --yesno  \
 "This will drop your database. Please close all database connnections." 0 0
    clear
    if [ ${?} = 0 ]
    then
        run_as_su "${BASEDIR}"/scripts/recreate_database.sh
        ${DIALOG} --msgbox "Recreate Database \ncompleted" 0 0
    fi
}

#
# copy component configs from basedir into config dir
#
create_configs() {
    ${BASEDIR}/scripts/create_dirs.sh
    for component in "${!components_dir[@]}"; do
        create_config ${component}
    done
    ${DIALOG} --msgbox "Create Default Configs \ncompleted" 0 0
}

#
# copy component configs from basedir into config dir
#
create_dirs() {
    ${BASEDIR}/scripts/create_dirs.sh
    ${DIALOG} --msgbox "Create needed directories \ncompleted" 0 0
}

#
# copy component config from basedir into config dir
# for a single given component
#
create_config() {
    component=${1}

    component_dir=${components_dir["${component}"]}
    if [ ! -f "${CONFIG_DIR}/${component}"d.cfg ]
    then
        run_as_su "cp ${component_dir}/config/${component}d.cfg ${CONFIG_DIR}"
    fi
}

#
# lists rabbit bindings in less
#
list_rabbit_bindings() {
    run_as_su "rabbitmqctl list_bindings | less"
}

#
# builds the given component
#
build_comp() {
    component=${1}

    component_dir=${components_dir["${component}"]}
    if enable_env; then

        ${DIALOG} --infobox "Build ${component} Component \n..." 0 0
        (cd ${component_dir} && make install)

        ${DIALOG} --msgbox "Build ${component} Component \ncompleted" 0 0
    fi
}

#
# restarts the given component
#
restart_comp() {
    component=${1}

    ${DIALOG} --infobox "Restarting ${component} Component \n..." 0 0
    "${component}"d restart >${_temp}
    sleep 1
    ${DIALOG} --cr-wrap --colors --msgbox "Restarting \Zb${component}\Zn Component Output:\n\n$(cat ${_temp})" 20 120
}

#
# stops the given component
#
stop_comp() {
    component=${1}

    if [ $(get_component_status ${component}) = 0 ]
    then
        ${DIALOG} --infobox "Stopping ${component} Component \n..." 0 0
        "${component}"d stop >${_temp} 2>&1
        sleep 1
        ${DIALOG} --cr-wrap --colors --msgbox "Stopping \Zb${component}\Zn Component Output:\n\n$(cat ${_temp})" 20 120
    fi
}

#
# starts the given component
#
start_comp() {
    component=${1}

    if [ $(get_component_status ${component}) != 0 ]
    then
        ${DIALOG} --infobox "Starting ${component} Component \n..." 0 0
        "${component}"d start > ${_temp} 2>&1
        sleep 1
        ${DIALOG} --cr-wrap --colors --msgbox "Starting \Zb${component}\Zn Component Output:\n\n$(cat ${_temp})" 20 120
    fi
}

#
# sends SIGKILL to component daemon and removes pid file
#
kill_comp() {
    component=${1}

        ${DIALOG} --infobox "Killing ${component} Component \n..." 0 0

        ps aux | grep "${component}d"  | awk '{print $2}' | xargs kill -9
        sleep 3
        rm -f ${PID_DIR}/"${component}"d.pid

        ${DIALOG} --cr-wrap --colors --msgbox "Killed \Zb${component} \ZnComponent." 20 120
}

#
# edit config file of a component
#
edit_config() {
    component=${1}

    clear
    sudo ${EDITOR} ${CONFIG_DIR}/"${component}"d.cfg
}

#
# show whole logfile of component
#
tail_log() {
    component=${1}

    logfile=${LOG_DIR}/"${component}"d.log
    if [ -z "${TAIL}" ]
    then
        ${DIALOG} --backtitle "${TITLE}" --title "${component} - Watch the logfile tail"  \
            --tailbox ${logfile} 0 0
    else
        trap generic_component_menu ${component} SIGINT
        ${TAIL} ${logfile}
    fi
}

#
# show logfile tail of component
#
less_log() {
    component=${1}

    logfile=${LOG_DIR}/"${component}"d.log
    if [ -z "${LESS}" ]
    then
        ${DIALOG} --colors --backtitle "${TITLE}" --title "${component} - Show the whole logfile"  \
            --textbox ${logfile} 0 0
    else
        ${LESS} ${logfile}
    fi
}

#
# runs make script with ${DIALOG} windows
#
my_make() {

    target=${1}
    clear
    make ${target}

    ${DIALOG} --msgbox "Build finished" 0 0
}

#
# returns status of component as a colored string
#  running ${PID} / stopped
#
get_component_status_colored() {
    component=${1}

    pid=`cat ${PID_DIR}/"${component}"d.pid 2> /dev/null`
    component_status="\Zb\Z1stopped\Z0\Zn         "
    if [ $(get_component_status ${component}) = 0 ]
    then
        component_status=$(printf "\Zb\Z2running\Z0\Zn   %6s" ${pid})
    fi
    echo "${component_status}"
}

#
# returns status of component as int
#  0: running
#  1: stopped
#
get_component_status() {
    component=${1}

    component_status="1"
    pid=`cat ${PID_DIR}/"${component}"d.pid 2> /dev/null`
    if ps -p ${pid} > /dev/null 2>&1
    then
        component_status="0"
    fi
    echo ${component_status}
}

run_as_su() {
    #${DIALOG} --clear
    clear
    sudo bash -c "${1}"
}

#######################################################################
#
#  MENUS
#
#######################################################################

call_menu() {
    while true
    do

        db_list
        ${DIALOG} --backtitle "${TITLE}" --title " Call Component Function "  \
             --cancel-label "Back"  \
             --extra-button \
             --extra-label "Add new call" \
             --menu "Recent calls are sorted by usage" 0 0 20  \
             "${CALL_ARRAY_LIST_MENU[@]}" 2>${_temp}

        case ${?} in
            0)
                menuitem=$(cat ${_temp})
                cli_call_by_id $(cat ${_temp})
                ;;
            3)
                new_call;;
            *)
                return;;
        esac
    done
}

components_menu() {

    # build component list with status
    component_menu_list=( )
    for component in "${!components_dir[@]}"; do
        component_menu_list+=(${component} "$(get_component_status_colored ${component})")
    done

    # no-collapse allows mutliple whitespaces in a row
    ${DIALOG} --backtitle "${TITLE}" --title " Manage Components"  \
        --cancel-label "Back"  \
        --colors  \
        --no-collapse    \
        --menu "     component            status      pid" 17 60 10  \
        "${component_menu_list[@]}" 2>${_temp}


    opt=${?}
    if [ ${opt} != 0 ]; then
        return;
    fi
    menuitem=`cat ${_temp}`
    generic_component_menu ${menuitem}
    components_menu
}

generic_component_menu() {
    component=${1}

    component_status=$(get_component_status ${component})
    if [ ${component_status} != 0 ]
    then
        start_stop_entry="Start"
    else
        start_stop_entry="Stop"
    fi

    ${DIALOG} --backtitle "${TITLE}" --title "${component^^}"  \
         --colors  \
         --no-collapse  \
         --cancel-label "Back"  \
         --menu "${component} Component - $(get_component_status_colored ${component})" 17 60 10  \
         Restart "Restart ${component}"  \
         Watch_Log "Watch the logfile tail"  \
         Show_Log "Show the whole logfile"  \
         Build "Build ${component}"  \
         ${start_stop_entry} "${start_stop_entry} ${component}"  \
         Config "Open Configuration in Editor"  \
         Kill "Kill ${component}d" 2>${_temp}

    opt=${?}
    if [ ${opt} != 0 ]; then
        return;
    fi
    menuitem=`cat ${_temp}`
    case ${menuitem} in
        Restart) restart_comp ${component} ;;
        Build) build_comp ${component} ;;
        Start) start_comp ${component} ;;
        Stop) stop_comp ${component} ;;
        Config) edit_config ${component} ;;
        Watch_Log) tail_log ${component} ;;
        Show_Log) less_log ${component} ;;
        Kill) kill_comp ${component} ;;
    esac
    generic_component_menu ${component}
}

build_menu() {
    ${DIALOG} --backtitle "${TITLE}" --title " Build Menu "  \
         --cancel-label "Back"  \
         --menu "Move using [UP] [DOWN], [Enter] to select" 17 60 10  \
         All "Build all"  \
         Core "Build utility packages"  \
         Clean "Delete all builds" 2>${_temp}

    opt=${?}
    if [ ${opt} != 0 ]; then
        return;
    fi
    menuitem=`cat ${_temp}`
    case ${menuitem} in
        All) my_make install ;;
        Core) my_make core-install ;;
        Clean) my_make clean ;;
    esac
    build_menu
}

environment_menu() {
    ${DIALOG} --backtitle "${TITLE}" --title " Environment Management"  \
         --cancel-label "Back"  \
         --menu "Move using [UP] [DOWN], [Enter] to select" 17 60 10  \
         All "Run all"  \
         Setup "Setup DECaF Environment"  \
         Dirs "Create needed direcetories"  \
         Configs "Create Default Configs" 2>${_temp}

    opt=${?}
    if [ ${opt} != 0 ]; then
        return;
    fi
    menuitem=`cat ${_temp}`
    case ${menuitem} in
        All) setup_environment;
        recreate_database;
        create_configs ;;
        Setup) setup_environment ;;
        Database) recreate_database ;;
        Dirs) create_dirs ;;
        Configs) create_configs ;;
    esac
    environment_menu
}

main_menu() {
    ${DIALOG} --backtitle "${TITLE}" --title " Main Menu"\
        --cancel-label "Quit" \
        --menu "Move using [UP] [DOWN], [Enter] to select" 17 60 10 \
        Environment "Environment Management" \
        Build "Build Menu" \
        Components "Manage Components" \
        Call "Call Component Function" \
        Rabbit "List Bindings in RabbitMQ" \
        Quit "Exit program" 2>${_temp}

    opt=${?}
    if [ ${opt} != 0 ]; then
        dispose;
    fi
    menuitem=`cat ${_temp}`
    case ${menuitem} in
        Environment) environment_menu ;;
        Build) build_menu ;;
        Components) components_menu ;;
        Call) call_menu ;;
        Rabbit) list_rabbit_bindings ;;
        Quit) dispose ;;
    esac
}

#######################################################################
#
#  MAIN LOOP
#
#######################################################################
while true; do
    main_menu
done
