import numpy as np


def Hermite(event_start, event_end, tangent_start, tangent_end):
    curve_points = []

    for parameter in np.arange(0, 1, 0.001):
        point_start = (event_start.x, event_start.y)
        point_end = (event_end.x, event_end.y)

        parameter_squared = parameter * parameter
        parameter_cubed = parameter_squared * parameter

        hermite_basis_h00 = 2 * parameter_cubed - 3 * parameter_squared + 1
        hermite_basis_h10 = parameter_cubed - 2 * parameter_squared + parameter
        hermite_basis_h01 = -2 * parameter_cubed + 3 * parameter_squared
        hermite_basis_h11 = parameter_cubed - parameter_squared

        x_coordinate = (
            hermite_basis_h00 * point_start[0]
            + hermite_basis_h10 * tangent_start.x
            + hermite_basis_h01 * point_end[0]
            + hermite_basis_h11 * tangent_end.x
        )
        y_coordinate = (
            hermite_basis_h00 * point_start[1]
            + hermite_basis_h10 * tangent_start.y
            + hermite_basis_h01 * point_end[1]
            + hermite_basis_h11 * tangent_end.y
        )

        curve_points.append((x_coordinate, y_coordinate))

    return curve_points
