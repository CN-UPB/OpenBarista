#!/bin/bash

function usage {
  echo "usage: $0 [arguments] inputfile"
  echo "Arguments:"
  echo -e "  -r, --raw\tThe raw image file. If not specified a temporary file is used."
  echo -e "  -o, --output\tThe output file. If not specified the name and location of the qcow2 file is derived from the inputfile."
  echo -e "  -h, --help\tShow this usage help and exit."
  echo -e "  -v, --version\tShow version information and exit."
}

function version {
  echo "$0 0.1 (7-Jan-2016)"
}

OPTIONS=$(getopt -o hvi:r:o: -l help,version,input:,raw:,output: -- "$@")

if [ $? -ne 0 ]; then
  echo "getopt error"
  exit 1
fi

eval set -- $OPTIONS

while true; do
  case "$1" in
    -h|--help)    usage ; exit 0 ;;
    -v|--version) version ; exit 0 ;;
    -r|--raw)     rawfile="$2" ; shift ;;
    -o|--output)  outputfile="$2" ; shift ;;
    --)           shift ; break ;;
    *)            echo "unknown option: $1" ; exit 1 ;;
  esac
  shift
done

if [ $# -ne 1 ]; then
  echo "unknown option(s): $@"
  exit 1
fi

command -v vboxmanage >/dev/null 2>&1 || { echo >&2 "Could not find vboxmanage."; exit 1; }
command -v qemu-img >/dev/null 2>&1 || { echo >&2 "Could not find qemu-img."; exit 1; }


inputfile="$@"
if [ ! -e "$inputfile" ]; then
  echo >&2 "Input file not found."
  exit 1
fi

if [ -z $rawfile ]; then
  rawfile=$(tempfile)
  rm -f "$rawfile"
  deleterawfile=1
fi
if [ -z $outputfile ]; then
  outputfile="$(dirname "$inputfile")/$(basename -s .vmdk "$inputfile").qcow2"
fi
vboxmanage clonehd --format RAW "$inputfile" "$rawfile" && qemu-img convert -f raw "$rawfile" -O qcow2 "$outputfile"
if [ ! -z $deleterawfile ] && [ -e $rawfile ]; then
  rm -rf $rawfile
fi
