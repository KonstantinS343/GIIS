def Bresenham(start, end):
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

    for _ in range(dx + 1):
        points.append((x, y))
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

    return points
