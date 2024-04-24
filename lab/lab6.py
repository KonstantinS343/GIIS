import math
import keyboard
import tkinter as tk


def is_point_inside_polygon(x, y, polygon):
    num_vertices = len(polygon.points)
    intersections = 0

    for i in range(num_vertices):
        x1, y1 = polygon.points[i]
        x2, y2 = polygon.points[(i + 1) % num_vertices]

        if ((y1 <= y < y2) or (y2 <= y < y1)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1) + x1
        ):
            intersections += 1

    return intersections % 2 != 0


def is_point_inside_any_polygon(x, y, polygons):
    for poly in polygons:
        if is_point_inside_polygon(x, y, poly):
            return True
    return False


class Polygon:
    def __init__(self, points):
        i = 0
        self.points = []
        while i < len(points):
            self.points.append([points[i], points[i + 1]])
            i += 2


class GraphicsEditor2D:
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()
        self.canvas.configure(bg="white")
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.window.bind("<Return>", self.on_enter_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.lines = []
        self.intersection_points = []
        self.polygons = []
        self.current_line = None
        self.debug_mode = False
        self.grid_toggled = False
        self.correction_mode = False
        self.dragged_point = None

        self.create_delete_button()
        self.create_mode_menu()
        self.create_polygon_algorithm_menu()
        self.create_polygon_fill_algorithm_menu()

    def on_drag_end(self, event):
        if self.dragged_point is not None:
            self.current_line[self.dragged_point[0]] = event.x
            self.current_line[self.dragged_point[1]] = event.y
            self.canvas.delete("ghost")
            if self.mode_var.get() == "Polygon":
                if self.polygon_algorithm_var.get() == "Graham":
                    self.draw_graham_polygon(self.current_line, "ghost")
                elif self.polygon_algorithm_var.get() == "Jarvis":
                    self.draw_jarvis_polygon(self.current_line, "ghost")
            self.redraw_markers()
            self.dragged_point = None

    def on_drag_start(self, event):
        i = 0
        while i < len(self.current_line):
            x_center = ((self.current_line[i] // self.grid_size) * self.grid_size) + (
                self.grid_size // 2
            )
            y_center = (
                (self.current_line[i + 1] // self.grid_size) * self.grid_size
            ) + (self.grid_size // 2)
            x_event_center = ((event.x // self.grid_size) * self.grid_size) + (
                self.grid_size // 2
            )
            y_event_center = ((event.y // self.grid_size) * self.grid_size) + (
                self.grid_size // 2
            )
            if x_event_center == x_center and y_event_center == y_center:
                self.dragged_point = i, i + 1
            i += 2

    def on_enter_press(self, event):
        if self.correction_mode:
            self.canvas.delete("marker")
            self.canvas.delete("ghost")
            if self.mode_var.get() == "Polygon":
                if self.polygon_algorithm_var.get() == "Graham":
                    self.draw_graham_polygon(self.current_line)
                    self.polygons.append(Polygon(self.current_line))
                elif self.polygon_algorithm_var.get() == "Jarvis":
                    self.draw_jarvis_polygon(self.current_line)
                    self.polygons.append(Polygon(self.current_line))
            self.current_line = None
            self.correction_mode = False
            return
        elif len(self.current_line) == 2 and is_point_inside_any_polygon(
            self.current_line[0], self.current_line[1], self.polygons
        ):
            if self.polygon_fill_algorithm_var.get() == "Edge table":
                self.draw_edge_table(self.current_line)
                self.current_line = []
                self.redraw_markers()
                return
            elif self.polygon_fill_algorithm_var.get() == "Active edge table":
                self.draw_active_edge_table(self.current_line)
                self.current_line = []
                self.redraw_markers()
                return
            elif self.polygon_fill_algorithm_var.get() == "Flood fill":
                self.draw_flood_fill(self.current_line)
                self.current_line = []
                self.redraw_markers()
                return
            elif self.polygon_fill_algorithm_var.get() == "Scanline flood fill":
                self.draw_scanline_flood_fill(self.current_line)
                self.current_line = []
                self.redraw_markers()
                return
            else:
                return
        elif (
            self.mode_var.get() == "Polygon"
            and self.current_line != None
            and len(self.current_line) >= 6
        ):
            if self.polygon_algorithm_var.get() == "Graham":
                self.draw_graham_polygon(self.current_line, "ghost")
            elif self.polygon_algorithm_var.get() == "Jarvis":
                self.draw_jarvis_polygon(self.current_line, "ghost")
            else:
                return
        self.redraw_markers()
        self.correction_mode = True

    def draw_edge_table(self, point):
        polygon = None
        for poly in self.polygons:
            if is_point_inside_polygon(point[0], point[1], poly):
                polygon = poly
                break

        if polygon is None:
            return

        intersections = []

        for i in range(len(polygon.points)):
            x1, y1 = polygon.points[i]
            x2, y2 = polygon.points[(i + 1) % len(polygon.points)]

            if y1 != y2:
                slope = (x2 - x1) / (y2 - y1)
                y_start = min(y1, y2)
                y_end = max(y1, y2)

                for y in range(y_start, y_end):
                    x = x1 + slope * (y - y1)
                    intersections.append((x, y))

        for i in range(len(polygon.points)):
            x_prev, y_prev = polygon.points[(i - 1) % len(polygon.points)]
            x_curr, y_curr = polygon.points[i]
            x_next, y_next = polygon.points[(i + 1) % len(polygon.points)]

            if y_curr < y_prev and y_curr < y_next:
                intersections.append((x_curr, y_curr))
                intersections.append((x_curr, y_curr))
            elif y_curr > y_prev and y_curr > y_next:
                intersections.append((x_curr, y_curr))
                intersections.append((x_curr, y_curr))

        intersections.sort(key=lambda point: (point[1], point[0]))
        previous_y = -1
        for i in range(0, len(intersections), 2):
            x_start, y = intersections[i]
            x_end, _ = (
                intersections[i + 1] if i + 1 < len(intersections) else (self.width, y)
            )

            x = int(x_start)
            while x <= int(x_end):
                x_center = ((x // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                y_center = ((y // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                if previous_y != y_center:
                    self.canvas.create_rectangle(
                        x_center - self.grid_size / 2,
                        y_center - self.grid_size / 2,
                        x_center + self.grid_size / 2,
                        y_center + self.grid_size / 2,
                        fill="black",
                    )
                    self.canvas.create_rectangle(
                        x_center - self.grid_size / 2,
                        y_center - self.grid_size / 2,
                        x_center + self.grid_size / 2,
                        y_center + self.grid_size / 2,
                        fill="green",
                        tags="debug",
                    )
                    if self.debug_mode:
                        self.canvas.update()
                        keyboard.wait("space")
                    self.canvas.delete("debug")
                x += self.grid_size
            previous_y = ((y // self.grid_size) * self.grid_size) + (
                self.grid_size // 2
            )

        self.canvas.update()

    def draw_active_edge_table(self, point):
        polygon = None
        for poly in self.polygons:
            if is_point_inside_polygon(point[0], point[1], poly):
                polygon = poly
                break

        if polygon is None:
            return

        Y_groups = [[] for _ in range(self.height)]

        num_vertices = len(polygon.points)
        for i in range(num_vertices):
            x1, y1 = polygon.points[i]
            x2, y2 = polygon.points[(i + 1) % num_vertices]

            if y1 != y2:
                if y1 < y2:
                    ymin = y1
                    ymax = y2
                    xmin = x1
                    slope_inverse = (x2 - x1) / (y2 - y1)
                else:
                    ymin = y2
                    ymax = y1
                    xmin = x2
                    slope_inverse = (x1 - x2) / (y1 - y2)

                Y_groups[ymin].append((xmin, slope_inverse, ymax - ymin + 1))

        current_scanline = 0
        active_edges = []
        previous_y = -1

        while current_scanline < self.height:
            active_edges.extend(Y_groups[current_scanline])
            active_edges.sort(key=lambda edge: edge[0])
            intersection_points = [edge[0] for edge in active_edges]
            intersection_points.sort()

            for i in range(0, len(intersection_points) - 1, 2):
                x_start = intersection_points[i]
                x_end = intersection_points[i + 1]

                x = int(x_start)
                while x <= int(x_end):
                    x_center = ((x // self.grid_size) * self.grid_size) + (
                        self.grid_size // 2
                    )
                    y_center = (
                        (current_scanline // self.grid_size) * self.grid_size
                    ) + (self.grid_size // 2)
                    if previous_y != y_center:
                        self.canvas.create_rectangle(
                            x_center - self.grid_size / 2,
                            y_center - self.grid_size / 2,
                            x_center + self.grid_size / 2,
                            y_center + self.grid_size / 2,
                            fill="black",
                        )
                        self.canvas.create_rectangle(
                            x_center - self.grid_size / 2,
                            y_center - self.grid_size / 2,
                            x_center + self.grid_size / 2,
                            y_center + self.grid_size / 2,
                            fill="green",
                            tags="debug",
                        )
                        if self.debug_mode:
                            self.canvas.update()
                            keyboard.wait("space")
                        self.canvas.delete("debug")
                    x += self.grid_size
                previous_y = ((current_scanline // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )

            active_edges = [
                (xmin, slope_inverse, Du - 1)
                for (xmin, slope_inverse, Du) in active_edges
                if Du > 1
            ]

            active_edges = [
                (xmin + slope_inverse, slope_inverse, Du)
                for (xmin, slope_inverse, Du) in active_edges
            ]

            current_scanline += 1

        self.canvas.update()

    def create_delete_button(self):
        delete_button = tk.Button(
            self.window, text="Delete All Lines", command=self.delete_all_lines
        )
        delete_button.pack(side="left")

    def create_polygon_algorithm_menu(self):
        self.polygon_algorithm_var = tk.StringVar(self.window)
        self.polygon_algorithm_var.set("Graham")

        polygon_algorithm_menu = tk.OptionMenu(
            self.window, self.polygon_algorithm_var, "Graham", "Jarvis"
        )
        polygon_algorithm_menu.pack(side="left")

    def create_polygon_fill_algorithm_menu(self):
        self.polygon_fill_algorithm_var = tk.StringVar(self.window)
        self.polygon_fill_algorithm_var.set("Edge table")

        polygon_fill_algorithm_menu = tk.OptionMenu(
            self.window,
            self.polygon_fill_algorithm_var,
            "Edge table",
            "Active edge table",
            "Flood fill",
            "Scanline flood fill",
        )
        polygon_fill_algorithm_menu.pack(side="left")

    def create_mode_menu(self):
        self.mode_var = tk.StringVar(self.window)
        self.mode_var.set("Polygon")

        mode_menu = tk.OptionMenu(self.window, self.mode_var, "Polygon")
        mode_menu.pack(side="left")

    def redraw_markers(self):
        self.canvas.delete("marker")
        i = 0
        while i < len(self.current_line):
            x_center = ((self.current_line[i] // self.grid_size) * self.grid_size) + (
                self.grid_size // 2
            )
            y_center = (
                (self.current_line[i + 1] // self.grid_size) * self.grid_size
            ) + (self.grid_size // 2)
            self.canvas.create_rectangle(
                x_center - self.grid_size / 2,
                y_center - self.grid_size / 2,
                x_center + self.grid_size / 2,
                y_center + self.grid_size / 2,
                fill="green",
                tags="marker",
            )
            i += 2

    def delete_all_lines(self):
        self.canvas.delete("all")
        self.lines = []
        self.polygons = []
        self.intersection_points = []
        self.dragged_point = None
        self.correction_mode = False
        self.current_line = None

    def on_canvas_click(self, event):
        if self.correction_mode:
            return self.on_drag_start(event)
        x = event.x
        y = event.y

        x_center = ((x // self.grid_size) * self.grid_size) + (self.grid_size // 2)
        y_center = ((y // self.grid_size) * self.grid_size) + (self.grid_size // 2)

        is_inside_polygon = False
        for polygon in self.polygons:
            if is_point_inside_polygon(x_center, y_center, polygon):
                is_inside_polygon = True
                break

        if is_inside_polygon:
            self.canvas.create_rectangle(
                x_center - self.grid_size / 2,
                y_center - self.grid_size / 2,
                x_center + self.grid_size / 2,
                y_center + self.grid_size / 2,
                fill="purple",
                tags="marker",
            )
        else:
            self.canvas.create_rectangle(
                x_center - self.grid_size / 2,
                y_center - self.grid_size / 2,
                x_center + self.grid_size / 2,
                y_center + self.grid_size / 2,
                fill="green",
                tags="marker",
            )

        if self.current_line is None:
            self.current_line = [x_center, y_center]
        elif (
            (
                len(self.current_line) < 4
                and self.mode_var.get() == "Second-order line"
                and self.second_order_line_algorithm_var.get() == "Parabola"
            )
            or (self.mode_var.get() == "Curve")
            or (self.mode_var.get() == "Polygon")
            or (self.mode_var.get() == "Delone triangulation")
            or (self.mode_var.get() == "Voronoi diagram")
        ):
            self.current_line.extend([x_center, y_center])
        else:
            self.current_line.extend([x_center, y_center])
            self.lines.append(self.current_line)
            line = self.current_line
            self.current_line = None
            self.canvas.delete("marker")

    def draw_graham_polygon(self, line, tag=""):
        def calculate_normal(p1, p2):
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude != 0:
                nx = -dy / magnitude
                ny = dx / magnitude
                return nx, ny
            return 0, 0

        def graham_scan(points):
            def orientation(p0, p1, p2):
                val = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p2[0] - p1[0]) * (
                    p1[1] - p0[1]
                )
                if val == 0:
                    return 0
                return 1 if val > 0 else -1

            lowest = min(points, key=lambda p: p[1])

            def compare(p1, p2):
                if p1 == lowest:
                    return -1
                if p2 == lowest:
                    return 1

                angle1 = math.atan2(p1[1] - lowest[1], p1[0] - lowest[0])
                angle2 = math.atan2(p2[1] - lowest[1], p2[0] - lowest[0])

                if abs(angle1 - angle2) < 1e-6:
                    return (p1[0] - lowest[0]) * (p2[1] - lowest[1]) - (
                        p2[0] - lowest[0]
                    ) * (p1[1] - lowest[1])
                return angle1 - angle2

            points.sort(key=lambda p: compare(lowest, p))

            stack = []
            for p in points:
                while len(stack) >= 2 and orientation(stack[-2], stack[-1], p) <= 0:
                    stack.pop()
                stack.append(p)

            return stack

        points = []
        for i in range(0, len(line), 2):
            points.append((line[i], line[i + 1]))

        hull = graham_scan(points)

        is_convex = True
        for i in range(len(hull)):
            try:
                p0 = hull[i - 2]
            except:
                p0 = hull[i - 2]
            p1 = hull[i - 1]
            p2 = hull[i]
            orientation_val = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p2[0] - p1[0]) * (
                p1[1] - p0[1]
            )
            if orientation_val < 0:
                is_convex = False
                break

        for i in range(len(hull)):
            start = hull[i]
            end = hull[(i + 1) % len(hull)]
            x1, y1 = start
            x2, y2 = end
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            while x1 != x2 or y1 != y2:
                x_center = ((x1 // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                y_center = ((y1 // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                if tag != "":
                    normal = calculate_normal(start, end)
                    normal_length = self.grid_size * 5
                    nx = normal[0] * normal_length
                    ny = normal[1] * normal_length
                    self.canvas.create_line(
                        x_center,
                        y_center,
                        x_center + nx,
                        y_center + ny,
                        fill="blue",
                        tags=tag,
                    )
                if tag != "" and not is_convex:
                    self.canvas.create_rectangle(
                        x_center - self.grid_size / 2,
                        y_center - self.grid_size / 2,
                        x_center + self.grid_size / 2,
                        y_center + self.grid_size / 2,
                        fill="red",
                        tags=tag,
                    )
                else:
                    self.canvas.create_rectangle(
                        x_center - self.grid_size / 2,
                        y_center - self.grid_size / 2,
                        x_center + self.grid_size / 2,
                        y_center + self.grid_size / 2,
                        fill="black",
                        tags=tag,
                    )
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

    def draw_jarvis_polygon(self, line, tag=""):
        def calculate_normal(p1, p2):
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude != 0:
                nx = -dy / magnitude
                ny = dx / magnitude
                return nx, ny
            return 0, 0

        def jarvis_scan(points):
            def orientation(p, q, r):
                val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
                if val == 0:
                    return 0  # collinear
                return 1 if val > 0 else -1  # clockwise or counterclockwise

            def distance(p, q):
                return (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2

            leftmost = min(points, key=lambda p: p[0])

            hull = []
            current = leftmost
            next_point = None

            while True:
                hull.append(current)
                next_point = points[0]

                for point in points:
                    if point == current:
                        continue
                    turn = orientation(current, next_point, point)
                    if turn == -1 or (
                        turn == 0
                        and distance(current, point) > distance(current, next_point)
                    ):
                        next_point = point

                current = next_point
                if current == leftmost:
                    break

            return hull

        points = [(line[i], line[i + 1]) for i in range(0, len(line), 2)]

        hull = jarvis_scan(points)

        for i in range(len(hull)):
            start = hull[i]
            end = hull[(i + 1) % len(hull)]
            x1, y1 = start
            x2, y2 = end
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy
            while x1 != x2 or y1 != y2:
                x_center = ((x1 // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                y_center = ((y1 // self.grid_size) * self.grid_size) + (
                    self.grid_size // 2
                )
                if tag != "":
                    normal = calculate_normal(end, start)
                    normal_length = self.grid_size * 5
                    nx = normal[0] * normal_length
                    ny = normal[1] * normal_length
                    self.canvas.create_line(
                        x_center,
                        y_center,
                        x_center + nx,
                        y_center + ny,
                        fill="blue",
                        tags=tag,
                    )
                self.canvas.create_rectangle(
                    x_center - self.grid_size / 2,
                    y_center - self.grid_size / 2,
                    x_center + self.grid_size / 2,
                    y_center + self.grid_size / 2,
                    fill="black",
                    tags=tag,
                )
                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

    def draw_flood_fill(self, point):
        x_center = ((point[0] // self.grid_size) * self.grid_size) + (
            self.grid_size // 2
        )
        y_center = ((point[1] // self.grid_size) * self.grid_size) + (
            self.grid_size // 2
        )
        stack = [(x_center, y_center)]
        painted_pixels = []
        while stack:
            x, y = stack.pop()
            if (
                x >= 0
                and x < self.width
                and y >= 0
                and y < self.height
                and (x, y) not in painted_pixels
                and is_point_inside_any_polygon(x, y, self.polygons)
            ):
                painted_pixels.append((x, y))
                self.canvas.create_rectangle(
                    x - self.grid_size / 2,
                    y - self.grid_size / 2,
                    x + self.grid_size / 2,
                    y + self.grid_size / 2,
                    fill="black",
                )
                self.canvas.create_rectangle(
                    x - self.grid_size / 2,
                    y - self.grid_size / 2,
                    x + self.grid_size / 2,
                    y + self.grid_size / 2,
                    fill="green",
                    tags="debug",
                )
                if self.debug_mode:
                    self.canvas.update()
                    keyboard.wait("space")
                self.canvas.delete("debug")
                stack.append((x + self.grid_size, y))
                stack.append((x - self.grid_size, y))
                stack.append((x, y + self.grid_size))
                stack.append((x, y - self.grid_size))

    def draw_scanline_flood_fill(self, point):
        x_center = ((point[0] // self.grid_size) * self.grid_size) + (
            self.grid_size // 2
        )
        y_center = ((point[1] // self.grid_size) * self.grid_size) + (
            self.grid_size // 2
        )
        stack = [(x_center, y_center)]
        painted_pixels = []

        while stack:
            x, y = stack.pop()

            if (
                x >= 0
                and x < self.width
                and y >= 0
                and y < self.height
                and (x, y) not in painted_pixels
                and is_point_inside_any_polygon(x, y, self.polygons)
            ):
                left = x
                right = x

                while (
                    left > 0
                    and (left - self.grid_size, y) not in painted_pixels
                    and is_point_inside_any_polygon(
                        left - self.grid_size, y, self.polygons
                    )
                ):
                    left -= self.grid_size

                while (
                    right < self.width - 1
                    and (right + self.grid_size, y) not in painted_pixels
                    and is_point_inside_any_polygon(
                        right + self.grid_size, y, self.polygons
                    )
                ):
                    right += self.grid_size

                i = left
                while i <= right:
                    self.canvas.create_rectangle(
                        i - self.grid_size / 2,
                        y - self.grid_size / 2,
                        x + self.grid_size / 2,
                        y + self.grid_size / 2,
                        fill="black",
                    )
                    self.canvas.create_rectangle(
                        i - self.grid_size / 2,
                        y - self.grid_size / 2,
                        x + self.grid_size / 2,
                        y + self.grid_size / 2,
                        fill="green",
                        tags="debug",
                    )
                    if self.debug_mode:
                        self.canvas.update()
                        keyboard.wait("space")
                    self.canvas.delete("debug")

                    painted_pixels.append((i, y))

                    if (
                        y > 0
                        and (i, y - self.grid_size) not in painted_pixels
                        and is_point_inside_any_polygon(
                            i, y - self.grid_size, self.polygons
                        )
                    ):
                        stack.append((i, y - self.grid_size))

                    if (
                        y < self.height - 1
                        and (i, y + self.grid_size) not in painted_pixels
                        and is_point_inside_any_polygon(
                            i, y + self.grid_size, self.polygons
                        )
                    ):
                        stack.append((i, y + self.grid_size))
                    i += self.grid_size

    def run(self):
        self.window.mainloop()


editor = GraphicsEditor2D(1000, 1000, 10)
editor.run()
