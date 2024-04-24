import numpy as np
import tkinter as tk
from scipy.spatial import Delaunay, Voronoi


def clip_line(x1, y1, x2, y2, canvas_width, canvas_height):
    INSIDE = 0  # Both points are inside the canvas
    LEFT = 1  # Bitmask for left boundary
    RIGHT = 2  # Bitmask for right boundary
    BOTTOM = 4  # Bitmask for bottom boundary
    TOP = 8  # Bitmask for top boundary

    def compute_outcode(x, y):
        code = INSIDE
        if x < 0:
            code |= LEFT
        elif x > canvas_width:
            code |= RIGHT
        if y < 0:
            code |= BOTTOM
        elif y > canvas_height:
            code |= TOP
        return code

    outcode1 = compute_outcode(x1, y1)
    outcode2 = compute_outcode(x2, y2)

    while True:
        if not (outcode1 | outcode2):  # Trivially accept
            break
        if outcode1 & outcode2:  # Trivially reject
            return None, None, None, None

        x = 0
        y = 0
        outcode = outcode1 if outcode1 else outcode2

        if outcode & TOP:
            x = x1 + (x2 - x1) * (canvas_height - y1) / (y2 - y1)
            y = canvas_height
        elif outcode & BOTTOM:
            x = x1 + (x2 - x1) * (0 - y1) / (y2 - y1)
            y = 0
        elif outcode & RIGHT:
            y = y1 + (y2 - y1) * (canvas_width - x1) / (x2 - x1)
            x = canvas_width
        elif outcode & LEFT:
            y = y1 + (y2 - y1) * (0 - x1) / (x2 - x1)
            x = 0

        if outcode == outcode1:
            x1 = x
            y1 = y
            outcode1 = compute_outcode(x1, y1)
        else:
            x2 = x
            y2 = y
            outcode2 = compute_outcode(x2, y2)

    return x1, y1, x2, y2


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

    def on_drag_end(self, event):
        if self.dragged_point is not None:
            self.current_line[self.dragged_point[0]] = event.x
            self.current_line[self.dragged_point[1]] = event.y
            self.canvas.delete("ghost")
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
        elif (
            self.mode_var.get() == "Delone triangulation"
            and self.current_line != None
            and len(self.current_line) >= 3
        ):
            self.draw_delone_triangulation(self.current_line)
            self.current_line = []
            self.redraw_markers()
            return
        elif (
            self.mode_var.get() == "Voronoi diagram"
            and self.current_line != None
            and len(self.current_line) >= 3
        ):
            self.draw_voronoi_diagram(self.current_line)
            self.current_line = []
            self.redraw_markers()
            return
        self.redraw_markers()
        self.correction_mode = True

    def create_delete_button(self):
        delete_button = tk.Button(
            self.window, text="Delete All Lines", command=self.delete_all_lines
        )
        delete_button.pack(side="left")

    def delete_all_lines(self):
        self.canvas.delete("all")
        self.lines = []
        self.polygons = []
        self.intersection_points = []
        self.dragged_point = None
        self.correction_mode = False
        self.current_line = None

    def create_mode_menu(self):
        self.mode_var = tk.StringVar(self.window)
        self.mode_var.set("---")

        mode_menu = tk.OptionMenu(
            self.window, self.mode_var, "Delone triangulation", "Voronoi diagram"
        )
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
            (self.mode_var.get() == "Curve")
            or (self.mode_var.get() == "Polygon")
            or (self.mode_var.get() == "Delone triangulation")
            or (self.mode_var.get() == "Voronoi diagram")
        ):
            self.current_line.extend([x_center, y_center])
        else:
            self.current_line.extend([x_center, y_center])
            self.lines.append(self.current_line)
            self.current_line = None
            self.canvas.delete("marker")

    def show_error_message(self, message):
        error_label = tk.Label(self.canvas, text=message, fg="red")
        error_label.place(x=10, y=10)
        self.canvas.after(5000, lambda: error_label.destroy())

    def draw_delone_triangulation(self, line):
        def inside_circle(A, B, C, P):
            ax = A[0] - P[0]
            ay = A[1] - P[1]
            bx = B[0] - P[0]
            by = B[1] - P[1]
            cx = C[0] - P[0]
            cy = C[1] - P[1]

            return (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) >= 1e-12

        def cross_product(u, v):
            return u[0] * v[1] - u[1] * v[0]

        def triangulate(points):
            n = len(points)
            edges = []

            sorted_points = sorted(points, key=lambda p: p[0])

            for i in range(n):
                while len(edges) >= 2:
                    j = len(edges) - 2
                    k = len(edges) - 1
                    A = sorted_points[edges[j][0]]
                    B = sorted_points[edges[j][1]]
                    C = sorted_points[edges[k][1]]

                    if (
                        cross_product(
                            (B[0] - A[0], B[1] - A[1]), (C[0] - B[0], C[1] - B[1])
                        )
                        > 0
                    ):
                        break

                    edges.pop()

                edges.append((len(edges), i))

            lower = len(edges)
            t = lower + 1

            for i in range(n - 2, -1, -1):
                while len(edges) >= t:
                    j = len(edges) - 2
                    k = len(edges) - 1
                    A = sorted_points[edges[j][0]]
                    B = sorted_points[edges[j][1]]
                    C = sorted_points[edges[k][1]]

                    if (
                        cross_product(
                            (B[0] - A[0], B[1] - A[1]), (C[0] - B[0], C[1] - B[1])
                        )
                        > 0
                    ):
                        break

                    edges.pop()

                edges.append((i, len(edges)))

            edges.pop()

            result = []
            for i in range(len(edges)):
                a = edges[i][0]
                b = edges[i][1]
                A = sorted_points[a]
                B = sorted_points[b]
                flag = True

                for j in range(n):
                    if j == a or j == b:
                        continue

                    P = sorted_points[j]
                    if inside_circle(A, B, P, sorted_points[(a + b) >> 1]):
                        flag = False
                        break

                if flag:
                    result.append((a, b))
                    self.canvas.create_line(
                        sorted_points[a][0],
                        sorted_points[a][1],
                        sorted_points[b][0],
                        sorted_points[b][1],
                    )

            return result

        points = []
        for i in range(0, len(line), 2):
            points.append((line[i], line[i + 1]))
        triangulation = Delaunay(np.array(points))
        triangulate(points)
        for triangle in triangulation.simplices.copy():
            x1, y1 = points[triangle[0]]
            x2, y2 = points[triangle[1]]
            x3, y3 = points[triangle[2]]
            self.draw_line_bresenham(x1, y1, x2, y2)
            self.draw_line_bresenham(x2, y2, x3, y3)
            self.draw_line_bresenham(x3, y3, x1, y1)

    def draw_voronoi_diagram(self, line):
        points = []
        for i in range(0, len(line), 2):
            points.append((line[i], line[i + 1]))

        vor = Voronoi(np.array(points))
        for ridge in vor.ridge_vertices:
            if -1 not in ridge:
                x1, y1, x2, y2 = clip_line(
                    vor.vertices[ridge[0]][0],
                    vor.vertices[ridge[0]][1],
                    vor.vertices[ridge[1]][0],
                    vor.vertices[ridge[1]][1],
                    self.width,
                    self.height,
                )
                x1 = ((x1 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                y1 = ((y1 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                x2 = ((x2 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                y2 = ((y2 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
                self.draw_line_bresenham(x1, y1, x2, y2)

    def draw_line_bresenham(self, x1, y1, x2, y2):
        dx = int(abs(x2 - x1) / self.grid_size)
        dy = int(abs(y2 - y1) / self.grid_size)
        sx = -1 * self.grid_size if x1 > x2 else self.grid_size
        sy = -1 * self.grid_size if y1 > y2 else self.grid_size
        err = dx - dy

        while x1 != x2 or y1 != y2:
            x1 = ((x1 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            x2 = ((x2 // self.grid_size) * self.grid_size) + (self.grid_size // 2)
            self.canvas.create_rectangle(
                x1 - self.grid_size / 2,
                y1 - self.grid_size / 2,
                x1 + self.grid_size / 2,
                y1 + self.grid_size / 2,
                fill="black",
            )
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x1 += sx

            if err2 < dx:
                err += dx
                y1 += sy

    def run(self):
        self.window.mainloop()


editor = GraphicsEditor2D(800, 600, 10)
editor.run()
