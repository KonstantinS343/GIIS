from tkinter import Tk, Canvas, Button
from tkinter import ttk
import tkinter as tk

from copy import deepcopy

from importlib import import_module
import logging

logging.basicConfig(
    format="[%(asctime)s | %(levelname)s]: %(message)s",
    datefmt="%m.%d.%Y %H:%M:%S",
    level=logging.INFO,
)


class Paint:
    def __init__(self, name: str = "Graphical Editor") -> None:
        self.window = Tk()
        self.canvas_width = 800
        self.canvas_height = 600
        self.window.title(name)
        self.configure_window()

    def configure_window(self) -> None:
        self._init_canvas()
        self._setup_tools()

    def _init_canvas(self) -> None:
        self.canvas = Canvas(
            self.window,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white",
            bd=3,
            relief=tk.SUNKEN,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.click_handler)

    def _setup_tools(self):
        self.colors = ["black", "red", "green", "blue", "yellow", "orange", "purple"]
        self.selected_color = self.colors[0]
        self.mode = [
            "DDA",
            "Wu",
            "Bresenham",
            "Ellipse",
            "Circle",
            "Hyperbola",
            "Parabola",
        ]
        self.selected_mode = self.mode[0]

        self.tool_frame = ttk.LabelFrame(self.window, text="Tools")
        self.tool_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.Y)

        self.mode_label = ttk.Label(self.tool_frame, text="Mode:")
        self.mode_label.pack(side=tk.TOP, padx=5, pady=5)

        self.mode_combobox = ttk.Combobox(
            self.tool_frame, values=self.mode, state="readonly"
        )
        self.mode_combobox.current(0)
        self.mode_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.mode_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self._select_mode(self.mode_combobox.get()),
        )

        self.color_label = ttk.Label(self.tool_frame, text="Color:")
        self.color_label.pack(side=tk.TOP, padx=5, pady=5)

        self.color_combobox = ttk.Combobox(
            self.tool_frame, values=self.colors, state="readonly"
        )
        self.color_combobox.current(0)
        self.color_combobox.pack(side=tk.TOP, padx=5, pady=5)
        self.color_combobox.bind(
            "<<ComboboxSelected>>",
            lambda event: self._select_color(self.color_combobox.get()),
        )

        self.clear_button = ttk.Button(
            self.tool_frame, text="Clear Canvas", command=self.clear_canvas
        )
        self.clear_button.pack(side=tk.TOP, padx=5, pady=5)

        self.debug_button = ttk.Button(
            self.tool_frame, text="Debug", command=self.debug_line
        )
        self.debug_button.pack(side=tk.TOP, padx=5, pady=5)

        self.debug_button_cool_line = ttk.Button(
            self.tool_frame, text="Debug Cool Lines", command=self.debug_cool_lines
        )
        self.debug_button_cool_line.pack(side=tk.TOP, padx=5, pady=5)

    def clear_canvas(self) -> None:
        logging.info("Clear all")
        self.canvas.delete("all")

    def _select_color(self, color: str) -> None:
        logging.info("Select " + color + " Color")
        self.selected_color = color

    def _select_mode(self, mode: str) -> None:
        logging.info("Select " + mode + " Mode")
        self.selected_mode = mode

    def click_handler(self, event) -> None:
        try:
            self.draw.append(event)
        except AttributeError:
            self.draw = [event]
            return
        try:
            module = import_module("lines." + self.selected_mode)
        except ModuleNotFoundError:
            module = import_module("cool_lines." + self.selected_mode)
        function = getattr(module, self.selected_mode)
        try:
            self.points, self.additional, change_flag = function(
                self.draw[0], self.draw[1]
            )
            self.old_additional = deepcopy(self.additional)
        except Exception:
            self.points = function(self.draw[0], self.draw[1])
        logging.info("Draw in " + self.selected_mode + " Mode")
        if self.selected_mode != "Wu":
            for i in self.points:
                self.canvas.create_line(
                    i[0], i[1], i[0] + 1, i[1] + 1, fill=self.selected_color, width=2
                )
        else:
            s1 = 1 if self.points[-1][0] > self.points[0][0] else -1
            s2 = 1 if self.points[-1][1] > self.points[0][1] else -1

            k = (self.points[-1][1] - self.points[0][1]) / (
                self.points[-1][0] - self.points[0][0]
            )
            b = self.points[-1][1] - self.points[-1][0] * k
            for i in range(len(self.points)):
                if change_flag:
                    self.additional[i] = (
                        self.additional[i][0] - 10 * s1,
                        self.additional[i][1],
                        abs(self.points[i][0] * k + b - self.points[i][1]),
                    )
                else:
                    self.additional[i] = (
                        self.additional[i][0],
                        self.additional[i][1] - 10 * s2,
                        abs(self.points[i][0] * k + b - self.points[i][1]),
                    )
            for i in range(len(self.points)):
                color_1 = "#%02x%02x%02x" % (
                    abs(int(255 * self.additional[i][2])),
                    abs(int(255 * self.additional[i][2])),
                    abs(int(255 * self.additional[i][2])),
                )

                color_2 = "#%02x%02x%02x" % (
                    abs(int(255 * (1 - self.additional[i][2]))),
                    abs(int(255 * (1 - self.additional[i][2]))),
                    abs(int(255 * (1 - self.additional[i][2]))),
                )

                self.canvas.create_rectangle(
                    self.points[i][0],
                    self.points[i][1],
                    self.points[i][0] + 1,
                    self.points[i][1] + 1,
                    fill=color_1,
                )
                self.canvas.create_rectangle(
                    self.additional[i][0],
                    self.additional[i][1],
                    self.additional[i][0] + 1,
                    self.additional[i][1] + 1,
                    fill=color_2,
                )
        delattr(self, "draw")

    def run(self):
        self.window.mainloop()

    def debug_line(self):
        self.debug_window = Tk()
        self.debug_window.title("Debug")
        self.debug_window.geometry("1000x1000")

        self.next_button = Button(self.debug_window, text="Next")
        self.next_button.grid()

        self.debug_canvas = Canvas(
            self.debug_window, width=1000, height=1000, background="white"
        )
        self.debug_canvas.grid()
        if self.selected_mode == "Wu":
            self.additional = self.old_additional
            sign_x = 1
            sign_y = 1
            if self.additional[-1][0] - self.additional[0][0] < 0:
                sign_x = -1
            if self.additional[-1][1] - self.additional[0][1] < 0:
                sign_y = -1

            prev_x = self.additional[0][0]
            prev_y = self.additional[0][1]

            prev_add_x = self.additional[0][0]
            prev_add_y = self.additional[0][1]

            pixels = list(self.additional)
            x = 0
            y = 0
            for i in range(len(self.additional)):
                if pixels[i][0] == prev_x:
                    self.additional[i] = (prev_add_x, prev_add_y, self.additional[i][2])
                else:
                    self.additional[i] = (
                        pixels[i][0] + 10 * x * sign_x,
                        prev_add_y,
                        self.additional[i][2],
                    )
                    prev_add_x = pixels[i][0] + 10 * x * sign_x
                    prev_x = pixels[i][0]
                    x += 1

                if pixels[i][1] == prev_y:
                    self.additional[i] = (prev_add_x, prev_add_y, self.additional[i][2])
                else:
                    self.additional[i] = (
                        prev_add_x,
                        pixels[i][1] + 10 * y * sign_y,
                        self.additional[i][2],
                    )
                    prev_add_y = pixels[i][1] + 10 * y * sign_y
                    prev_y = pixels[i][1]
                    y += 1
        sign_x = 1
        sign_y = 1
        if self.points[-1][0] - self.points[0][0] < 0:
            sign_x = -1
        if self.points[-1][1] - self.points[0][1] < 0:
            sign_y = -1

        prev_x = self.points[0][0]
        prev_y = self.points[0][1]

        prev_add_x = self.points[0][0]
        prev_add_y = self.points[0][1]

        pixels = list(self.points)
        x = 0
        y = 0
        for i in range(len(self.points)):
            if pixels[i][0] == prev_x:
                self.points[i] = (prev_add_x, prev_add_y)
            else:
                self.points[i] = (pixels[i][0] + 10 * x * sign_x, prev_add_y)
                prev_add_x = pixels[i][0] + 10 * x * sign_x
                prev_x = pixels[i][0]
                x += 1

            if pixels[i][1] == prev_y:
                self.points[i] = (prev_add_x, prev_add_y)
            else:
                self.points[i] = (prev_add_x, pixels[i][1] + 10 * y * sign_y)
                prev_add_y = pixels[i][1] + 10 * y * sign_y
                prev_y = pixels[i][1]
                y += 1

        def debug_draw(*args):
            if self.selected_mode != "Wu":
                self.debug_canvas.create_rectangle(
                    self.points[0][0],
                    self.points[0][1],
                    self.points[0][0] + 10,
                    self.points[0][1] + 10,
                    fill="black",
                )
                del self.points[0]
            else:
                color_1 = "#%02x%02x%02x" % (
                    abs(int(255 * self.additional[0][2])),
                    abs(int(255 * self.additional[0][2])),
                    abs(int(255 * self.additional[0][2])),
                )

                color_2 = "#%02x%02x%02x" % (
                    abs(int(255 * (1 - self.additional[0][2]))),
                    abs(int(255 * (1 - self.additional[0][2]))),
                    abs(int(255 * (1 - self.additional[0][2]))),
                )

                self.debug_canvas.create_rectangle(
                    self.points[0][0],
                    self.points[0][1],
                    self.points[0][0] + 10,
                    self.points[0][1] + 10,
                    fill=color_1,
                )
                self.debug_canvas.create_rectangle(
                    self.additional[0][0],
                    self.additional[0][1],
                    self.additional[0][0] + 10,
                    self.additional[0][1] + 10,
                    fill=color_2,
                )
                self.points.pop(0)
                self.additional.pop(0)

        self.next_button.bind("<Button-1>", debug_draw)

    def debug_cool_lines(self):
        self.debug_window = Tk()
        self.debug_window.title("Debug")
        self.debug_window.geometry("1000x1000")

        # self.next_button = Button(self.debug_window, text="Next")
        # self.next_button.grid()

        self.debug_canvas = Canvas(
            self.debug_window, width=1000, height=1000, background="white"
        )
        self.debug_canvas.grid()

        def draw_point(*args):
            if not self.points:
                self.debug_window.mainloop()
            self.debug_canvas.create_rectangle(
                self.points[0][0],
                self.points[0][1],
                self.points[0][0],
                self.points[0][1],
                fill="black",
            )
            self.points.pop(0)
            self.debug_window.after(10, draw_point)

        try:
            draw_point()
        except Exception:
            pass


p = Paint()
p.run()
