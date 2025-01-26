from .widget import Widget

from ..drawer import Drawer, ansi
from ..datatypes import Size, Position
from ..callbacks import OnDrawContext

# TODO: do proper word wrapping in a word wrapper class
class Label(Widget):
    def __init__(
        self,
        text,
        centered: bool = False,
        wordwrap: bool = True,
        padding: int = 0,
        size: Size | tuple[int, int] = (100, 10),
        position: Position | tuple[int, int] = (0, 0),
        **kwargs
    ):
        super().__init__(size, position, **kwargs)

        if not isinstance(text, (str, ansi.AnsiString)):
            raise TypeError(f"Expected `text` to be of type `str` or `ansi.AnsiString` but got `{type(text)}`.")

        if isinstance(text, str):
            text = ansi.AnsiString(text, fore = (220, 220, 220))
        
        self.text = text
        self.pad = padding
        self.centered = centered
        self.wordwrap = wordwrap

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        if isinstance(value, str):
            value = ansi.AnsiString(value, fore = (220, 220, 220))
        
        self._text = value
    
    def _place_text(self, drawer: Drawer, text: ansi.AnsiString, line_index: int = 0):
        def maybe_center_place(t: str, ypos):
            if self.centered:
                pos = (self.position.y + ypos, self.position.x + max(0, self.pad + self.size.width - len(text)) // 2)
            else:
                pos = (self.position.y + ypos, self.position.x + self.pad)
            drawer.place(t, pos = pos, assign = False)

        max_length = (self.size.width - 2*self.pad)

        if len(text) > max_length:
            if self.wordwrap:
                for i in range(len(text)):
                    i_ = len(text) - 1 - i
                    if i_ > max_length:
                        continue
                    if text.vec[i_].char == " ":
                        if len(text) > (i_ + 1):
                            t_0, t_1 = text.split_at(i_ + 1)
                        else:
                            t_0 = text
                            t_1 = ansi.AnsiString("")
                        maybe_center_place(t_0, line_index)
                        return self._place_text(drawer, t_1, line_index + 1)
            else:
                t_0, t_1 = text.split_at(max_length)
                maybe_center_place(t_0, line_index)
        else:
            maybe_center_place(text, line_index)

    def on_draw(self, context: OnDrawContext):
        self._place_text(context.get_drawer(), self.text)