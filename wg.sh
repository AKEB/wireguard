#!/bin/bash

ENVFILE=$(dirname $0)/.env
[ -f ${ENVFILE} ] || { echo "${ENVFILE} not found" ; exit 1 ; }
. $(dirname $0)/.env


CONF=$(dirname $0)/wireguard.conf
[ -f $CONF ] || { echo "$CONF not found" ; exit 1 ; }
. $(dirname $0)/wireguard.conf


[ $# -ge 1 ] || { echo "Usage: $0 | add [<users>] | del <users>"; exit 2 ; }

VARS="PEERS TELEGRAM_BOT_TOKEN TELEGRAM_USER_ID"
for VAR in $VARS ; do if [ "${!VAR:-undefined}" = "undefined" ] ; then echo "$VAR is empty or undefined "; exit ; fi ; done

DOCKER_COMPOSE="docker-compose -f ${DOCKER_COMPOSE_FILE} --env-file ${PWD}/wireguard.conf "

CMD=$1
shift

USERLIST=$*

function telegram_file_send() {
    curl -F document=@"${1}" https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument?chat_id=${TELEGRAM_USER_ID}
}

function telegram_text_send() {
    curl -X POST https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage?chat_id=${TELEGRAM_USER_ID} -d text="${1}"
}

function show_users() {
    echo "Show users:" $*
    if [ $# -gt 0 ] ;
    then
        argN=1;
        while [ $argN -le $# ] ;
        do
            if [ -d "${PWD}/config/peer_${!argN}/" ]; then
                ${DOCKER_COMPOSE} exec wireguard /app/show-peer ${!argN}
            else echo "Peer ${!argN} doesn't exist!";
            fi
            argN=$((argN+1)) ;
        done ;
    else echo "USE show <user1> <user2> <user3>" ;
    fi
}

function send_users() {
    echo "Send users:" $*
    if [ $# -gt 0 ] ;
    then
        argN=1;
        while [ $argN -le $# ] ;
        do
            if [ -d "${PWD}/config/peer_${!argN}/" ]; then
                {
                    telegram_text_send "WireGuard config for user ${!argN}"
                    telegram_file_send "${PWD}/config/peer_${!argN}/peer_${!argN}.conf"
                    telegram_file_send "${PWD}/config/peer_${!argN}/peer_${!argN}.png"
                } &> /dev/null
            else echo "Peer ${!argN} doesn't exist!";
            fi
            argN=$((argN+1)) ;
        done ;
    else echo "USE send <user1> <user2> <user3>" ;
    fi
}

function add_users() {
    echo "Add users:" $*
    if [ $# -gt 0 ] ;
    then
        argN=1;
        while [ $argN -le $# ] ;
        do
            PEERS="${PEERS},${!argN}";
            argN=$((argN+1)) ;
        done ;
        PEERS=($(echo "${PEERS}" | tr ',' '\n' | sort -u | tr '\n' ','))
        PEERS=${PEERS::(${#PEERS}-1)}
        echo "PEERS=${PEERS}" > .env

        ${DOCKER_COMPOSE} up -d --force-recreate
        sleep 5;
        show_users $*;
        send_users $*;
    else echo "USE add <user1> <user2> <user3>" ;
    fi
}

function del_users() {
    echo "Delete users:" $*
    if [ $# -gt 0 ] ;
    then
        argN=1;
        while [ $argN -le $# ] ;
        do
            rm -rf "${PWD}/config/peer_${!argN}/"
            argN=$((argN+1)) ;
        done ;
        PEERS_OLD=$(echo "${PEERS}" | tr ',' '\n')
        PEERS=""
        for VAR in ${PEERS_OLD} ; do
            if [[ ! " $* " =~ " ${VAR} " ]]; then
                PEERS="${PEERS},${VAR}";
            fi
        done
        PEERS=${PEERS:1:(${#PEERS})}
        echo "PEERS=${PEERS}" > .env
        ${DOCKER_COMPOSE} up -d --force-recreate
    else echo "USE del <user1> <user2> <user3>" ;
    fi
}


function start() {
    echo "Starting WireGuard"
    ${DOCKER_COMPOSE} up -d --force-recreate
}

function stop() {
    echo "Stoping WireGuard"
    ${DOCKER_COMPOSE} down
}

function restart() {
    echo "Restarting WireGuard"
    ${DOCKER_COMPOSE} down && ${DOCKER_COMPOSE} up -d --force-recreate
}

function logs() {
    ${DOCKER_COMPOSE} logs
}

function stat() {
    ${DOCKER_COMPOSE} exec wireguard wg show
}


case $CMD in
    "add") add_users ${USERLIST} ;;
    "del") del_users ${USERLIST} ;;
    "show") show_users ${USERLIST} ;;
    "send") send_users ${USERLIST} ;;
    "start") start ;;
    "stop") stop ;;
    "restart") restart ;;
    "logs") logs ;;
    "stat") stat ;;
esac
