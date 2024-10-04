#!/bin/sh

# Start dump1090
cd /dump1090
./dump1090 --interactive --net
#./dump1090 --interactive --net --ifile testfiles/modes1.bin --loop &

# Start rotctld
cd /Hamlib/tests
./rotctld -m 603 -r ${DEVICE} -t 4532 -s 115200 -T 127.0.0.1 -C timeout=2000