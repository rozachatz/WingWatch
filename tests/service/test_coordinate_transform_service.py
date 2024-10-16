from trackingapp.service.coordinate_transform_service import CoordinateTransformService


def test_execute():
    service = CoordinateTransformService(30.0, 45.0, 120.0)
    azym, el = service.transform_coordinates(30.1, 45.0, 400.0)
    print(f"Transformed Coordinates:")
    print(f"Azimuth: {azym} degrees")
    print(f"Elevation: {el} degrees")
