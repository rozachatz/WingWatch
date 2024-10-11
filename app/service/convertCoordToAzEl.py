import pymap3d as pm
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def enu_to_az_el(e, n, u):
    """Convert ENU (East, North, Up) coordinates to azimuth and elevation."""

    # Calculate azimuth
    azimuth = (np.degrees(np.arctan2(e, n)) % 360)-180  # Normalize to 0-360 degrees

    # Calculate elevation
    distance_horizontal = np.sqrt(e ** 2 + n ** 2)  # Horizontal distance in ENU
    elevation = np.degrees(np.arctan2(u, distance_horizontal))

    return azimuth, elevation

# Radar's position
radar_lat = 37.9865621 # deg
radar_lon = 23.7657559 # deg
radar_el = 120       # meters

# Target
target_lat = 37.9765621  # deg
target_lon = 23.7657559  # deg
target_el = 120      # meters

# Convert geodetic coordinates to ENU coordinates
enu_coordinates = pm.geodetic2enu(target_lat, target_lon, target_el, radar_lat, radar_lon, radar_el)

print(f"ENU coordinates: East = {enu_coordinates[0]:.2f} m, North = {enu_coordinates[1]:.2f} m, Up = {enu_coordinates[2]:.2f} m")

azimuth, elevation = enu_to_az_el(enu_coordinates[0], enu_coordinates[1], enu_coordinates[2])

print(f"Azimuth: {azimuth:.2f}°")
print(f"Elevation: {elevation:.2f}°")

# Plot in 3D
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Set the labels for the plot
ax.set_title('3D Plot of Radar and Target Location')
ax.set_xlabel('East (m)')
ax.set_ylabel('North (m)')
ax.set_zlabel('Up (m)')

# Plot the radar's location as the origin (0, 0, 0)
ax.scatter(0, 0, 0, color='blue', label='Radar Position')

# Plot the point of interest in ENU coordinates
ax.scatter(enu_coordinates[0], enu_coordinates[1], enu_coordinates[2], color='red', label='Target')

# Draw a line from the radar to the target
ax.plot([0, enu_coordinates[0]], [0, enu_coordinates[1]], [0, enu_coordinates[2]], color='green', linestyle='--', label='Line of Sight')

# Add a legend
ax.legend()

# Show the plot
plt.show()