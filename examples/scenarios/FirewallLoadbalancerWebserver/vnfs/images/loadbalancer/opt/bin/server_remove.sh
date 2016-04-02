#!/bin/bash
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
ip=${ip//./'\.'}
if [ ! -z $ip ]; then
  sed -i "/$ip/d" /etc/haproxy/haproxy.cfg
  systemctl restart haproxy.service
fi
