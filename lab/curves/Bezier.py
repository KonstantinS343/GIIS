import numpy as np


def Bezier(event_start, event_end, control_point1, control_point2):
    bezier_points = [
        (event_start.x, event_start.y),
        (control_point1.x, control_point1.y),
        (control_point2.x, control_point2.y),
        (event_end.x, event_end.y),
    ]

    curve_coordinates = []

    for parameter in np.arange(0, 1, 0.001):
        parameter_squared = parameter * parameter
        parameter_cubed = parameter_squared * parameter
        one_minus_parameter = 1 - parameter
        one_minus_parameter_squared = one_minus_parameter * one_minus_parameter
        one_minus_parameter_cubed = one_minus_parameter_squared * one_minus_parameter

        x_coordinate = (
            one_minus_parameter_cubed * bezier_points[0][0]
            + 3 * one_minus_parameter_squared * parameter * bezier_points[1][0]
            + 3 * one_minus_parameter * parameter_squared * bezier_points[2][0]
            + parameter_cubed * bezier_points[3][0]
        )
        y_coordinate = (
            one_minus_parameter_cubed * bezier_points[0][1]
            + 3 * one_minus_parameter_squared * parameter * bezier_points[1][1]
            + 3 * one_minus_parameter * parameter_squared * bezier_points[2][1]
            + parameter_cubed * bezier_points[3][1]
        )

        curve_coordinates.append([x_coordinate, y_coordinate])

    return curve_coordinates
