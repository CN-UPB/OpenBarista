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

iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
if [ ! -z $ip ]; then
  iptables -t nat -A PREROUTING -i eth2 -p tcp --dport 80 -j DNAT --to "$ip:80"
  iptables -A FORWARD -d "$ip" -p tcp --dport 80 -j ACCEPT
  iptables -t nat -A POSTROUTING -j MASQUERADE
fi
iptables -A INPUT -i eth2 -j DROP