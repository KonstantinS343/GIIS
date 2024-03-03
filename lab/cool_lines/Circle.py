def Circle(event_1, event_2, is_circle=True):
    pixels = []

    radius_x = abs(event_1.x - event_2.x) // 2
    radius_y = abs(event_1.y - event_2.y) // 2
    center_x = min(event_1.x, event_2.x) + radius_x
    center_y = min(event_1.y, event_2.y) + radius_y

    if is_circle:
        radius_y = radius_x

    x = 0
    y = radius_y

    decision_param_1 = (
        (radius_y * radius_y)
        - (radius_x * radius_x * radius_y)
        + (0.25 * radius_x * radius_x)
    )
    dx = 2 * radius_y * radius_y * x
    dy = 2 * radius_x * radius_x * y

    while dx < dy:
        pixels.append((x + center_x, y + center_y))
        pixels.append((-x + center_x, y + center_y))
        pixels.append((x + center_x, -y + center_y))
        pixels.append((-x + center_x, -y + center_y))

        if decision_param_1 < 0:
            x += 1
            dx = dx + (2 * radius_y * radius_y)
            decision_param_1 = decision_param_1 + dx + (radius_y * radius_y)
        else:
            x += 1
            y -= 1
            dx = dx + (2 * radius_y * radius_y)
            dy = dy - (2 * radius_x * radius_x)
            decision_param_1 = decision_param_1 + dx - dy + (radius_y * radius_y)

    decision_param_2 = (
        ((radius_y * radius_y) * ((x + 0.5) * (x + 0.5)))
        + ((radius_x * radius_x) * ((y - 1) * (y - 1)))
        - (radius_x * radius_x * radius_y * radius_y)
    )

    while y >= 0:
        pixels.append((x + center_x, y + center_y))
        pixels.append((-x + center_x, y + center_y))
        pixels.append((x + center_x, -y + center_y))
        pixels.append((-x + center_x, -y + center_y))

        if decision_param_2 > 0:
            y -= 1
            dy = dy - (2 * radius_x * radius_x)
            decision_param_2 = decision_param_2 + (radius_x * radius_x) - dy
        else:
            y -= 1
            x += 1
            dx = dx + (2 * radius_y * radius_y)
            dy = dy - (2 * radius_x * radius_x)
            decision_param_2 = decision_param_2 + dx - dy + (radius_x * radius_x)

    return pixels
