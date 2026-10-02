import math
from trackingapp.models.radar_models import Site
from trackingapp.service.geographic_coordinates import pointing_angles


def enu_to_az_el(e, n, u):
    # Convert ENU (East, North, Up) coordinates to azimuth and elevation.

    # Calculate azimuth and normalize to [0, 360) degrees
    azimuth = (math.degrees(math.atan2(e, n)) + 360) % 360

    # Calculate horizontal distance in ENU
    distance_horizontal = math.hypot(e, n)

    # Calculate elevation
    elevation = math.degrees(math.atan2(u, distance_horizontal))

    # Clamp elevation to a valid range (0 to 90 degrees)
    elevation = max(0, min(elevation, 90))  # Adjust max value if needed

    return azimuth, elevation


def plot_figure(enu_coordinates):
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title('3D Plot of Radar and Target Location')
    ax.set_xlabel('East (m)')
    ax.set_ylabel('North (m)')
    ax.set_zlabel('Up (m)')
    ax.scatter(0, 0, 0, color='blue', label='Radar Position')

    # Plot the point of interest in ENU coordinates
    ax.scatter(enu_coordinates[0], enu_coordinates[1], enu_coordinates[2], color='red', label='Target')

    # Draw a line from the radar to the target
    ax.plot([0, enu_coordinates[0]], [0, enu_coordinates[1]], [0, enu_coordinates[2]], color='green', linestyle='--',
            label='Line of Sight')
    ax.legend()
    plt.show()


class CoordinateTransformService:

    def __init__(self, radar_lat, radar_lon, radar_el):
        self.radar_lat = radar_lat
        self.radar_lon = radar_lon
        self.radar_el = radar_el

    def transform_coordinates(self, target_lat, target_lon, target_el):
        receiver = Site(name='receiver', latitude=self.radar_lat, longitude=self.radar_lon,
                        altitude_m=self.radar_el)
        target = Site(name='aircraft', latitude=target_lat, longitude=target_lon,
                      altitude_m=target_el)
        azimuth, elevation = pointing_angles(receiver, target)
        print(f"Azimuth: {azimuth:.2f}°")
        print(f"Elevation: {elevation:.2f}°")
        return azimuth, elevation
