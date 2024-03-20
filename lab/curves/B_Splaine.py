def B_Splaine(point1, point2, point3, point4):
    spline_points = []
    total_points = 1000
    for index in range(total_points):
        param = index / (total_points - 1)
        param_squared = param * param
        param_cubed = param_squared * param
        one_minus_param = 1 - param
        omp_squared = one_minus_param * one_minus_param
        omp_cubed = omp_squared * one_minus_param

        x_coord = (
            omp_cubed * point1.x
            + 3 * omp_squared * param * point4.x
            + 3 * one_minus_param * param_squared * point3.x
            + param_cubed * point2.x
        )
        y_coord = (
            omp_cubed * point1.y
            + 3 * omp_squared * param * point4.y
            + 3 * one_minus_param * param_squared * point3.y
            + param_cubed * point2.y
        )

        spline_points.append((x_coord, y_coord))
    return spline_points
