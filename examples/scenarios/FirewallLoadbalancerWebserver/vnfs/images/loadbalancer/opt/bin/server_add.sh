#!/bin/bash
uuid=$(uuidgen)
while getopts ":i:" opt; do
  case $opt in
    i)
      ip="$OPTARG"
      ;;
    \?)
      exit 1
      ;;
    :)
      exit 1
      ;;
  esac
done
if [ ! -z $ip ]; then
  echo -e "\tserver $uuid $ip:80 cookie $uuid check" >> /etc/haproxy/haproxy.cfg
  systemctl restart haproxy.service
fi
