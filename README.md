WingWatch is an advanced aircraft tracking application that integrates ADS-B and radar data to provide real-time airplane location tracking and antenna rotator configuration.

# Key Features:
##Real-time Tracking: Displays airplane coordinates from both ADS-B and radar sources on an interactive map.
##ADSB Data Reception: Utilizes the dump1090 application to effectively receive and process ADS-B data, ensuring accurate positioning of aircraft.
##Antenna Rotator Configuration: Leverages Hamlib software to configure and control your antenna rotator, allowing for optimized tracking of airborne vehicles.
##Docker Compose Integration: Simplifies deployment and depedency management of the application through Docker Compose.

To build and start the application, run the following command:

bash
Copy code
docker-compose up --build
