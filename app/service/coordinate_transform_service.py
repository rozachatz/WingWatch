import matplotlib.pyplot as plt
import numpy as np
import pymap3d as pm


def enu_to_az_el(e, n, u):
    #  Convert ENU (East, North, Up) coordinates to azimuth and elevation.
    azimuth = (np.degrees(np.arctan2(e, n)) % 360) - 180  # Normalize to 0-360 degrees
    distance_horizontal = np.sqrt(e ** 2 + n ** 2)  # Horizontal distance in ENU
    elevation = np.degrees(np.arctan2(u, distance_horizontal))
    return azimuth, elevation


def plot_figure(enu_coordinates):
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
        # Convert geodetic coordinates to ENU coordinates
        enu_coordinates = pm.geodetic2enu(target_lat, target_lon, target_el, self.radar_lat, self.radar_lon,
                                          self.radar_el)
        azimuth, elevation = enu_to_az_el(enu_coordinates[0], enu_coordinates[1], enu_coordinates[2])
        print(f"Azimuth: {azimuth:.2f}°")
        print(f"Elevation: {elevation:.2f}°")
        return azimuth, elevation
