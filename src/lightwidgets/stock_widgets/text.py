from typing import List

import cairo

from lightwidgets.geometry import Point
from lightwidgets.stock_widgets.geometrical import DrawableRectangle
from lightwidgets.stock_widgets.root import MainWindow, Root
from lightwidgets.stock_widgets.widget import Widget
from itertools import islice


class _TextLine:

    def __init__(self, text:str, start: Point):
        self.text = text
        self.start = start

class TextArea(Widget):

    def __init__(self, text: List[str], font_size: int=20, padding: int=10,
                 bold:bool=False, italic:bool=False):
        super().__init__()
        self.font_size = font_size
        self.text = text
        self.padding = padding
        self.italic = italic
        self.bold = bold
        self.__text_lines = []

    def on_draw(self, widget: "Widget", context: cairo.Context):
        self._set_font(context)
        for tl in self.__text_lines:
            context.move_to(tl.start.x, tl.start.y)
            context.show_text(tl.text)

        # context.move_to(0, 0)
        # self.shape.draw_on_context(context)
        # context.stroke()

    def _set_font(self, context: cairo.Context):
        context.set_font_size(self.font_size)
        slant = cairo.FONT_SLANT_NORMAL if not self.italic else cairo.FONT_SLANT_ITALIC
        weight = cairo.FONT_WEIGHT_NORMAL if not self.bold else cairo.FONT_WEIGHT_BOLD
        context.select_font_face("", slant, weight)

    def layout(self, context: cairo.Context):
        if self.father is None:
            return
        width = self.father.container_size[0] - 2 * self.padding

        self._set_font(context)



        def fit_check(l: List[str]) -> bool:
            l = " ".join(l)
            xb, yb, w, h, xa, ya = context.text_extents(l)
            if xa > width:
                return False
            else:
                return True

        self.__text_lines = []
        start_y = self.padding/2

        def append_line(line: str):
            nonlocal start_y
            if not line:
                start_y += self.padding
            else:
                _, yb, _, h, _, _ = context.text_extents(line)
                start_y += h - (yb *.75)
                self.__text_lines.append(_TextLine(line, Point(self.padding, start_y)))
                # context.move_to(self.padding, start_y + h + yb)
                # context.show_text(line)

        for paragraph in self.text:
            words = paragraph.split(" ")
            start = 0
            while start < len(words):
                pivot = start
                end = len(words)
                if fit_check(islice(words, start, end)):
                    append_line(" ".join(islice(words, start, end)))
                    start = len(words)
                elif not fit_check([words[start]]):
                    append_line(words[start])
                    start += 1
                else:
                    while end > pivot + 1:
                        t = (end + pivot) // 2
                        if not fit_check(islice(words, start, t)):
                            end = t
                        else:
                            pivot = t
                    append_line(" ".join(islice(words, start, pivot)))
                    start = pivot
            append_line("")

            self.shape = DrawableRectangle(Point(0, 0), width + 2 * self.padding, start_y + self.padding/2)



def main():

    win = MainWindow("TextTest")
    root = Root(200, 200)
    root.set_main_window(win)

    root.set_child(TextArea(["questa è una prova", "funzioni anche quando ci sono due righe forzate?"]))

    win.start_main()

if __name__ == '__main__':
    main()
