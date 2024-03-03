def Wu(start, end):
    x = start.x
    y = start.y

    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    points = []

    s1 = 1 if end.x > start.x else -1
    s2 = 1 if end.y > start.y else -1

    if dy > dx:
        dx, dy = dy, dx
        change_flag = True
    else:
        change_flag = False

    e = 2 * dy - dx

    additional = []

    for i in range(dx + 1):
        if change_flag:
            points.append((x, y))
            additional.append((x, y + s2))
        else:
            points.append((x, y))
            additional.append((x + s1, y))
        while e >= 0:
            if change_flag:
                x += s1
            else:
                y += s2
            e -= 2 * dx
        if change_flag:
            y += s2
        else:
            x += s1
        e += 2 * dy

    k = (end.y - start.y) / (end.x - start.x)
    b = start.y - start.x * k
    for i in range(len(points)):
        if change_flag:
            additional[i] = (
                additional[i][0] + 10 * s1,
                additional[i][1],
                abs(points[i][0] * k + b - points[i][1]),
            )
        else:
            additional[i] = (
                additional[i][0],
                additional[i][1] + 10 * s2,
                abs(points[i][0] * k + b - points[i][1]),
            )

    return points, additional, change_flag
