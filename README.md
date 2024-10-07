WingWatch is a Python-based aircraft tracking application that integrates ADS-B and radar data to provide real-time airplane location tracking and antenna rotator configuration.

# Key Features:
## Real-time Tracking 
Displays airplane coordinates from both ADS-B and (passive) radar sources on an interactive map.
## ADSB Data Reception 
Utilizes the dump1090 application to receive and process ADS-B data.
## Antenna Rotator Configuration
Uses Hamlib software to configure and control your antenna rotator.
## Docker Compose Integration
Simplifies deployment and depedency management of the application through Docker Compose. To build and start the application, run the command `docker-compose up --build`.

