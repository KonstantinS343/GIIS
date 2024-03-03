def Hyperbola(event_1, event_2):
    semimajor_axis = abs(event_2.x - event_1.x) // 2
    semiminor_axis = abs(event_2.y - event_1.y) // 2
    center_x = (event_1.x + event_2.x) // 2
    center_y = (event_1.y + event_2.y) // 2
    x = 0
    y = semiminor_axis
    decision_param = (
        semiminor_axis * semiminor_axis
        - semimajor_axis * semimajor_axis * semiminor_axis
        + semimajor_axis * semimajor_axis / 4
    )

    pixels = []

    while semimajor_axis * semimajor_axis * (
        2 * y - 1
    ) > 2 * semiminor_axis * semiminor_axis * (x + 1):
        if decision_param < 0:
            decision_param = decision_param + semiminor_axis * semiminor_axis * (
                2 * x + 3
            )
            x = x + 1
        else:
            decision_param = (
                decision_param
                + semiminor_axis * semiminor_axis * (2 * x + 3)
                + semimajor_axis * semimajor_axis * (-2 * y + 2)
            )
            x = x + 1
            y = y - 1
        pixels.append((x + center_x, -y + center_y))
        pixels.append(
            (
                -x + abs(event_1.x - event_2.x) + center_x,
                y - abs(event_1.y - event_2.y) + center_y,
            )
        )

    decision_param = (
        semiminor_axis * semiminor_axis * (x + 1) * (x + 1)
        + semimajor_axis * semimajor_axis * (y - 1) * (y - 1)
        - semimajor_axis * semimajor_axis * semiminor_axis * semiminor_axis
    )

    while y > 0:
        if decision_param < 0:
            decision_param = (
                decision_param
                + semiminor_axis * semiminor_axis * (2 * x + 2)
                + semimajor_axis * semimajor_axis * (-2 * y + 3)
            )
            x = x + 1
            y = y - 1
        else:
            decision_param = decision_param + semimajor_axis * semimajor_axis * (
                -2 * y + 3
            )
            y = y - 1
        pixels.append((x + center_x, -y + center_y))
        pixels.append(
            (
                -x + abs(event_1.x - event_2.x) + center_x,
                y - abs(event_1.y - event_2.y) + center_y,
            )
        )

    return pixels
