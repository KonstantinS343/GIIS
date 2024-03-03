def DDA(start, end):
    x_1 = start.x
    y_1 = start.y

    x_2 = end.x
    y_2 = end.y

    length = max(abs(x_1 - x_2), abs(y_1 - y_2))

    dx = (x_2 - x_1) / length
    dy = (y_2 - y_1) / length

    i = 0
    points = list()
    curr_x, curr_y = x_1, y_1
    while i < length:
        points.append((int(curr_x + dx), int(curr_y + dy)))
        curr_x = curr_x + dx
        curr_y = curr_y + dy
        i += 1

    return points
