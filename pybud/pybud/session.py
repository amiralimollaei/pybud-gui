import time
from threading import Thread

from readchar import key as KeyPress
from readchar import readkey

from .drawer import Drawer, color, ansi
from .window import Window

from .datatypes import Size, Color

from .callbacks import OnUpdateContext

# ticks per second
TPS = 20

def get_admination_at(tick, n = 3, animation = "▁▂▃▄▅▆▆▅▄▃▂▁▂ "):
    return animation[tick % (len(animation)-n):tick % (len(animation)-n)+n]

class UpdateHandler:
    def __init__(self, update_fn):
        self.closed = False
        self.tick = 0

        self.tickupdate_thread: Thread = None

        self.update_fn = update_fn
    
    def start(self):
        if self.tickupdate_thread is None:
            self.tickupdate_thread = Thread(target=self.do_tick_updates)
            self.tickupdate_thread.start()
        self.do_key_updates()

    def stop(self):
        self.closed = True
        while self.tickupdate_thread.is_alive():
            time.sleep(0.01)
        self.tickupdate_thread = None

    def is_running(self):
        return (not self.closed) and (self.tickupdate_thread is not None) and self.tickupdate_thread.is_alive()
    
    def do_tick_updates(self):
        frame_time = (1 / TPS)
        
        start_time = time.time()
        self.tick = 0
        while not self.closed:
            self.update_fn(OnUpdateContext(self.tick))

            schedule_ahead = (frame_time * self.tick) - (time.time() - start_time)
            
            # TODO: display a warning if were too far off the schedule

            time.sleep(max(0, schedule_ahead))
            self.tick += 1

    def do_key_updates(self):
        while not self.closed:
            try:
                key = readkey()
            except KeyboardInterrupt:
                key = KeyPress.CTRL_C
            if self.closed:
                break
            self.update_fn(OnUpdateContext(self.tick, key = key))


class Session:
    """
    A `Session` is main handler for all `Window`s, each `Session` contains a list of ordered windows.

    Additonally creates a `Drawer` instance and draws `Window`s in order,
    Also, adds functionality for a `Window` to appear on top of other `Window`s,
    Lastly, handles keyboard updates and tick updates for all windows with an instance of `UpdateHandler`.
    """

    def __init__(
        self,
        size: Size | tuple[int, int],
        background: Color | tuple[int, int, int],
        color_mode: color.ColorMode = None,
        allow_resize: bool = False
    ):
        if not isinstance(size, (Size, tuple)):
            raise TypeError(
                f"Expected size to be of type `datatypes.Size` or `tuple[int, int]` but got {type(size)}."
            )
        if isinstance(size, tuple):
            size = Size(*size)

        self.size = size

        if not isinstance(background, (Color, tuple)):
            raise TypeError(
                f"Expected background to be of type `datatypes.Color` or `tuple[int, int, int]` but got {type(background)}."
            )
        if isinstance(background, tuple):
            background = Color(*background)

        self.background = background

        if allow_resize:
            raise NotImplementedError("`allow_resize` is not yet implemented but will be released in a future update.")

        self.allow_resize = allow_resize
        
        self.color_mode = color.ColorMode.TRUECOLOR if color_mode is None else color_mode
        
        self.update_handler = UpdateHandler(update_fn=self.update)

        self.window_buffer: list[Window] = []

        self.drawer = Drawer(width=size.width, height=size.height, plane_color=background.get_rgb())
        
        self.draw_lock = False
    
    def add_window(self, window: Window):
        if window in self.window_buffer:
            self.window_buffer.remove(window)
        self.window_buffer.append(window)
        self.bring_window_to_front(window)
        self.update_focus()
    
    def bring_window_to_front(self, window: Window):
        # TODO: Don't update unnecessary widgets
        for w in self.window_buffer:
            if w is window:
                w._set_depth(0)
            else:
                w._set_depth(1+w._get_depth())

    def update_focus(self):
        for i, window in enumerate(self.window_buffer):
            if (i + 1) == len(self.window_buffer):
                window.focus()
            else:
                window.unfocus()

    def show(self):
        for window in self.window_buffer:
            window.open()
        self.update_handler.start()
        while self.update_handler.is_running():
            time.sleep(0.01)

    def close(self):
        print(("\r" + (" " * self.size.width) + "\n") * (self.size.height) , end="")
        print(f"\033[{self.size.height}F", end="")
        self.update_handler.stop()

    def update(self, context: OnUpdateContext):
        for window in reversed(self.window_buffer):
            if window.is_in_focus:
                window.update(context)
        self.draw()

    def clear(self):
        self.drawer.clear()
    
    def draw(self):
        if not self.draw_lock:
            self.draw_lock = True
            any_window_is_open = False
            
            depth_order_windows = sorted(self.window_buffer, key = lambda x: x._get_depth())
            for window in depth_order_windows:
                if window.is_open:
                    any_window_is_open = True
                    window.draw(self.drawer)
            if not any_window_is_open:
                self.close()
                self.draw_lock = False
                return
            
            self.drawer.place(ansi.AnsiString(get_admination_at(self.update_handler.tick)), pos=(0, self.size.width-4), assign = False)
            print(self.drawer.render(self.color_mode)[:-1], end="")
            print(f"\033[{self.size.height-1}F", end="")
            self.draw_lock = False