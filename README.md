This app uses dump1090 linux app to receive ADSB data and show the location of the plane in a map.

**TO DO**
1) Integrate the passive radar algorithm and show respective marker on map.
2) Dockerize rotator interface app and communicate with antenna rotator. (done, TODO: tcp connection script)

1)Power up software 
docker build -t linux_app .
docker run -it -p 8080:8080 --privileged -v /dev/swradio0:/dev/swradio0 -v /dev/ttyACM0:/dev/ttyACM0 linux_app

2)Connect to tcp and send commands to rotator
telnet localhost 4532
P 130 10


