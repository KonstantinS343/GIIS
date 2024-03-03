def Parabola(event_1, event_2):
    x1, y1 = event_1.x, event_1.y
    x2, y2 = event_2.x, event_2.y

    a = (y2 - y1) / ((x2 - x1) ** 2)
    b = -2 * a * x1
    c = y1 - a * x1**2 - b * x1

    x_start = min(x1, x2)
    x_end = max(x1, x2)
    y_values = []

    x = x_start
    while x <= x_end:
        y = a * x**2 + b * x + c
        y_values.append(y)
        x += 1

    x_values = list(range(x_start, x_end + 1))

    pixels = []

    if x1 < x2:
        offset = 0
        for i in range(len(x_values)):
            pixels.append((x_values[i], y_values[i]))
            if i > 0:
                pixels.append(
                    (x_values[i] - abs(x_values[0] - x_values[i]) - offset, y_values[i])
                )
            offset += 1
    else:
        offset = 0
        for i in range(len(x_values)):
            pixels.append((x_values[i], y_values[i]))
            if i > 0:
                pixels.append(
                    (
                        x_values[len(x_values) - i]
                        + 1
                        + abs(max(x_values) - min(x_values)),
                        y_values[i],
                    )
                )
            offset += 1

    return pixels
