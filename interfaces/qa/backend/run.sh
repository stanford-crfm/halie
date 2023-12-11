#!/bin/bash

LOGDIR=${2:-tmp};
DEV=${3:-server};

# Path to benchmarking repo
CRFM_DIR='./crfm_benchmarking';

if [ ! -d ../logs/$LOGDIR ]; then
  mkdir -p ../logs/$LOGDIR;
fi


PORTNUM=5555;

echo -e '\nHi!'
echo - you are running the server on port $PORTNUM;
echo - writing logs will be saved at ../logs/$LOGDIR;
echo -e '- press CTRL+C to quit\n';

python3 api_server.py --port $PORTNUM --log_dir ../logs/$LOGDIR --crfm_dir $CRFM_DIR;
