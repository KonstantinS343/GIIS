from matplotlib import pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from russian_names import RussianNames

from typing import NamedTuple


class Dot:
    def __init__(self, x, y, z):
        self.x_coor: float = x
        self.y_coor: float = y
        self.z_coor: float = z


class Figure:
    def __init__(self, dots):
        self.dots = dots
        self.update_midpoint()

    def update_midpoint(self):
        num_dots = len(self.dots)
        sum_x = sum(dot.x_coor for dot in self.dots)
        sum_y = sum(dot.y_coor for dot in self.dots)
        sum_z = sum(dot.z_coor for dot in self.dots)
        mid_x = sum_x / num_dots
        mid_y = sum_y / num_dots
        mid_z = sum_z / num_dots
        self.midpoint = Dot(mid_x, mid_y, mid_z)

    def rotate(self, angle, axis):
        rotation_matrix = self.get_rotation_matrix(angle, axis)
        for dot in self.dots:
            dot.x_coor, dot.y_coor, dot.z_coor = np.dot(
                rotation_matrix, [dot.x_coor, dot.y_coor, dot.z_coor]
            )
        self.update_midpoint()

    def get_rotation_matrix(self, angle, axis):
        c = np.cos(angle)
        s = np.sin(angle)
        if axis == "x":
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == "y":
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == "z":
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    def scale(self, scale_factor):
        for dot in self.dots:
            dot.x_coor = (
                dot.x_coor - self.midpoint.x_coor
            ) * scale_factor + self.midpoint.x_coor
            dot.y_coor = (
                dot.y_coor - self.midpoint.y_coor
            ) * scale_factor + self.midpoint.y_coor
            dot.z_coor = (
                dot.z_coor - self.midpoint.z_coor
            ) * scale_factor + self.midpoint.z_coor
        self.update_midpoint()


class Shapes(NamedTuple):
    name: str
    value: Figure


class GraphicsEditor3D:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Graphic Editor")

        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.axis("on")

        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        self.ax.set_zlim(-100, 100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=4)

        self.dots = []
        self.shapes = []

        self.selected_figure = None

        self.preview_dot = Dot(x=0, y=0, z=0)

        self.dot_frame = tk.Frame(self.root)
        self.dot_frame.grid(row=0, column=1, padx=10, pady=10)

        self.x_label = tk.Label(self.dot_frame, text="X:")
        self.x_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_entry = tk.Entry(self.dot_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)
        self.x_entry.bind("<KeyRelease>", self.x_changed)

        self.y_label = tk.Label(self.dot_frame, text="Y:")
        self.y_label.grid(row=1, column=0, padx=5, pady=5)
        self.y_entry = tk.Entry(self.dot_frame, width=10)
        self.y_entry.grid(row=1, column=1, padx=5, pady=5)
        self.y_entry.bind("<KeyRelease>", self.y_changed)

        self.z_label = tk.Label(self.dot_frame, text="Z:")
        self.z_label.grid(row=2, column=0, padx=5, pady=5)
        self.z_entry = tk.Entry(self.dot_frame, width=10)
        self.z_entry.grid(row=2, column=1, padx=5, pady=5)
        self.z_entry.bind("<KeyRelease>", self.z_changed)

        self.add_button = tk.Button(
            self.dot_frame, text="Add Dot", command=self.add_dot
        )
        self.add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.create_figure_button = tk.Button(
            self.dot_frame, text="Create Figure", command=self.create_figure
        )
        self.create_figure_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        self.clear_button = tk.Button(
            self.dot_frame, text="Clear", command=self.clear_all
        )
        self.clear_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.shapes_combobox = ttk.Combobox(
            self.root, values=self.shapes, state="readonly"
        )
        self.shapes_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.shapes_combobox.bind("<<ComboboxSelected>>", self.select_figure)

        self.root.bind("<KeyPress-x>", self.move_figure_x_plus)
        self.root.bind("<Control-x>", self.move_figure_x_minus)
        self.root.bind("<KeyPress-y>", self.move_figure_y_plus)
        self.root.bind("<Control-y>", self.move_figure_y_minus)
        self.root.bind("<KeyPress-z>", self.move_figure_z_plus)
        self.root.bind("<Control-z>", self.move_figure_z_minus)

        self.root.bind("<Alt-x>", self.rotate_selected_figure_x)
        self.root.bind("<Alt-y>", self.rotate_selected_figure_y)
        self.root.bind("<Alt-z>", self.rotate_selected_figure_z)

        self.root.bind("<KeyPress-i>", self.scale_selected_figure_plus_ten_percent)
        self.root.bind("<KeyPress-r>", self.scale_selected_figure_minus_ten_percent)

        self.file_menu = tk.Menu(root, tearoff=False)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        root.config(menu=self.file_menu)

    def _select_mode(self, mode: str) -> None:
        self.selected_mode = mode

    def save_file(self):
        if self.shapes:
            with open("figures.txt", "w") as file:
                for figure in self.shapes:
                    dots_str = " ".join(
                        f"{dot.x_coor},{dot.y_coor},{dot.z_coor}"
                        for dot in figure.value.dots
                    )
                    file.write(
                        f"{figure.name} " f"{len(figure.value.dots)} {dots_str}\n"
                    )

    def open_file(self):
        self.clear_all()
        try:
            with open("figures.txt", "r") as file:
                for line in file:
                    name, num_dots, *dots_str = line.strip().split(" ")
                    num_dots = int(num_dots)
                    dots = [Dot(*map(float, dot.split(","))) for dot in dots_str]
                    self.shapes.append(Shapes(name=name, value=Figure(dots)))
                    if not self.shapes_combobox["values"]:
                        self.shapes_combobox["values"] = (name,)
                    else:
                        self.shapes_combobox["values"] += (name,)
            self.update_plot()
        except FileNotFoundError:
            print("Error: File not found")

    def scale_selected_figure_plus_ten_percent(self, *args):
        if self.selected_figure:
            self.selected_figure.scale(1.1)
            self.update_plot()

    def scale_selected_figure_minus_ten_percent(self, *args):
        if self.selected_figure:
            self.selected_figure.scale(0.9)
            self.update_plot()

    def rotate_selected_figure_x(self, *args):
        if self.selected_figure:
            self.selected_figure.rotate(np.pi / 4, "x")
            self.update_plot()

    def rotate_selected_figure_y(self, *args):
        if self.selected_figure:
            self.selected_figure.rotate(np.pi / 4, "y")
            self.update_plot()

    def rotate_selected_figure_z(self, *args):
        if self.selected_figure:
            self.selected_figure.rotate(np.pi / 4, "z")
            self.update_plot()

    def move_figure_x_plus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.x_coor += 1
            self.update_plot()

    def move_figure_x_minus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.x_coor -= 1
            self.update_plot()

    def move_figure_y_plus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.y_coor += 1
            self.update_plot()

    def move_figure_y_minus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.y_coor -= 1
            self.update_plot()

    def move_figure_z_plus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.z_coor += 1
            self.update_plot()

    def move_figure_z_minus(self, *args):
        if self.selected_figure:
            for dot in self.selected_figure.dots:
                dot.z_coor -= 1
            self.update_plot()

    def select_figure(self, event):
        selected_value = self.shapes_combobox.get()
        self.selected_figure = next(
            filter(lambda figure: figure.name == selected_value, self.shapes)
        ).value
        self.update_plot()

    def clear_all(self):
        self.dots = []
        self.selection_dots = []
        self.selected_figure = None
        self.shapes = []
        self.update_plot()

    def x_changed(self, *args):
        try:
            self.preview_dot.x_coor = float(self.x_entry.get())
        except ValueError:
            return

        self.update_plot()

    def y_changed(self, *args):
        try:
            self.preview_dot.y_coor = float(self.y_entry.get())
        except ValueError:
            return

        self.update_plot()

    def z_changed(self, *args):
        try:
            self.preview_dot.z_coor = float(self.z_entry.get())
        except ValueError:
            return

        self.update_plot()

    def add_dot(self):
        try:
            x = float(self.x_entry.get())
            y = float(self.y_entry.get())
            z = float(self.z_entry.get())
        except ValueError:
            return

        dot = Dot(x, y, z)
        self.dots.append(dot)
        self.update_plot()

    def draw_figure(self, x_values, y_values, z_values):
        num_steps = 20
        lines = []
        for i in range(len(x_values)):
            for j in range(i + 1, len(x_values)):
                lines.append([i, j])
        interpolated_lines = []
        for line in lines:
            x_interp = np.linspace(x_values[line[0]], x_values[line[1]], num_steps)
            y_interp = np.linspace(y_values[line[0]], y_values[line[1]], num_steps)
            z_interp = np.linspace(z_values[line[0]], z_values[line[1]], num_steps)
            interpolated_lines.append(list(zip(x_interp, y_interp, z_interp)))
        for line in interpolated_lines:
            x, y, z = zip(*line)
            self.ax.plot(x, y, z, color="black", linewidth=1)

    def create_figure(self):
        figure = Figure(self.dots)
        name = RussianNames(count=1, patronymic=False, surname=False).get_batch()
        figure_tuple = Shapes(name=name[0], value=figure)
        self.shapes.append(figure_tuple)
        if not self.shapes_combobox["values"]:
            self.shapes_combobox["values"] = (name,)
        else:
            self.shapes_combobox["values"] += (name,)
        self.dots = []
        self.update_plot()

    def update_plot(self):
        self.ax.clear()

        for figure in self.shapes:
            dots = figure.value.dots
            x_values = [dot.x_coor for dot in dots]
            y_values = [dot.y_coor for dot in dots]
            z_values = [dot.z_coor for dot in dots]
            self.draw_figure(x_values, y_values, z_values)

        if self.dots:
            marked_x = [dot.x_coor for dot in self.dots]
            marked_y = [dot.y_coor for dot in self.dots]
            marked_z = [dot.z_coor for dot in self.dots]
            self.ax.scatter(marked_x, marked_y, marked_z, color="red")

        if self.preview_dot:
            self.ax.scatter(
                self.preview_dot.x_coor,
                self.preview_dot.y_coor,
                self.preview_dot.z_coor,
                color="green",
            )

        if self.selected_figure:
            self.selected_figure.update_midpoint()
            for dot in self.selected_figure.dots:
                self.ax.scatter(dot.x_coor, dot.y_coor, dot.z_coor, color="cyan")
            self.ax.scatter(
                self.selected_figure.midpoint.x_coor,
                self.selected_figure.midpoint.y_coor,
                self.selected_figure.midpoint.z_coor,
                color="purple",
            )

        self.ax.set_xlim(-100, 100)
        self.ax.set_ylim(-100, 100)
        self.ax.set_zlim(-100, 100)
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    editor = GraphicsEditor3D(root)
    root.mainloop()
