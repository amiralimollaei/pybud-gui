from readchar import key as KeyPress

from .drawer import Drawer
from .datatypes import Size, Position

from .mixins import CallbackMixin, DepthMixin

from .enums import WindowClosingReason
from .callbacks import OnUpdateContext, OnDrawContext, OnFocusAddedContext, OnFocusLostContext
from .callbacks.window import OnOpenContext, OnCloseContext

from .widgets import Widget, InteractionWidget

def exists(v):
    return v is not None

class Window(CallbackMixin, DepthMixin):
    """
    A `Window` is the main display plane in witch all the widgets will be drawn to, 
    it has a size and position and must be passed to a `Session` to be handled properly.
    """
    
    def __init__(
        self,
        size: Size | tuple[int, int],
        position: Position | tuple[int, int],
        title: str = None,
        has_border: bool = True,
        opacity: float = 1.0
    ):
        
        if not isinstance(size, (Size, tuple)):
            raise TypeError(
                f"Expected size to be of type `datatypes.Size` or `tuple[int, int]` but got {type(size)}."
            )
        if isinstance(size, tuple):
            size = Size(*size)

        self.size = size
        
        if not isinstance(position, (Position, tuple)):
            raise TypeError(
                f"Expected position to be of type `datatypes.Poition` or `tuple[int, int]` but got {type(position)}."
            )
        if isinstance(position, tuple):
            position = Position(*position)

        self.position = position
        
        self.title = title or self.__class__.__name__
        self.has_border = has_border
        self.opacity = opacity
        
        self.is_open = False
        self.is_in_focus = False
        
        self._widgets: list[Widget] = []
        self._focus_widget: Widget = None

        self.tick = 0
        
        self.window_drawer = Drawer(
            width = self.size.width,
            height = self.size.height,
            plane_color = None
        )

        # holds all callbacks based on their ids
        super().__init__([
            "on_draw",
            "on_open",
            "on_close",
            "on_focus_added",
            "on_focus_lost",
            "on_update"
        ])

    def unfocus(self):
        self.is_in_focus = False
        self._run_callbacks(OnFocusLostContext())

    def focus(self):
        self.is_in_focus = True
        self._run_callbacks(OnFocusAddedContext())

    def _trace_closest_widget_in_angle_range(self, origin: InteractionWidget, angle: float, pov: float = 75.0) -> Widget | None:
        # Get origin point and normalize input angles
        o_point = origin._get_center_point()
        angle_min = (angle - pov) % 360
        angle_max = (angle + pov) % 360

        applicable_widgets = []
        for w in reversed(self._widgets):
            if w is origin or not isinstance(w, InteractionWidget):
                continue
                
            w_point = w._get_center_point()
            widget_angle = o_point.angle_to(w_point)
            
            # Check if angle falls within the range (handles wrap-around)
            if angle_min <= angle_max:
                in_range = angle_min <= widget_angle <= angle_max
            else:
                in_range = widget_angle >= angle_min or widget_angle <= angle_max

            if in_range:
                applicable_widgets.append((w, w_point))

        # find the widget were its center point is the closest to the origin point
        min_distance = float("inf")
        chosen_widget = None
        for w, w_point in applicable_widgets:
            w_distance = o_point.distance_to(w_point)
            if w_distance < min_distance:
                min_distance = w_distance
                chosen_widget = w
        return chosen_widget
    
    def update(self, context: OnUpdateContext):
        if exists(context.tick):
            self.tick = context.tick
        self._run_callbacks(context)
        if exists(self._focus_widget):
            self._focus_widget.update(context)
        if context.is_cancelled():
            return
        match context.key:
            case KeyPress.CTRL_C:
                self.close(WindowClosingReason.KeyboardInterrupt)
                context.cancel()
            case KeyPress.TAB:
                chosen_widget = None
                for w in self._widgets:
                    if w is self._focus_widget or not isinstance(w, InteractionWidget):
                        continue
                    chosen_widget = w
                    break
                if chosen_widget:
                    self.set_focus_widget(chosen_widget)
                    context.cancel()
            case KeyPress.UP:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget_in_angle_range(
                        origin = self._focus_widget,
                        angle = 90,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.DOWN:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget_in_angle_range(
                        origin = self._focus_widget,
                        angle = 270,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.RIGHT:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget_in_angle_range(
                        origin = self._focus_widget,
                        angle = 0,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.LEFT:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget_in_angle_range(
                        origin = self._focus_widget,
                        angle = 180,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()

    def set_focus_widget(self, chosen_widget):
        self._widgets.remove(chosen_widget)
        self._widgets.append(chosen_widget)
        self._update_widget_focus()

    def add_widget(self, widget: Widget):
        widget._set_depth(max([0]+[w._get_depth() for w in self._widgets])+1)
        self._widgets.append(widget)
        self._update_widget_focus()
    
    def bring_widget_to_front(self, widget: Widget):
        # TODO: Don't update unnecessary widgets
        for w in self._widgets:
            if w is widget:
                w._set_depth(0)
            else:
                w._set_depth(1+w._get_depth())
    
    # sets the last widget in `self._widgets` to be in focus and others to not be in focus
    def _update_widget_focus(self):
        focus_granted = False
        for w in reversed(self._widgets):
            if isinstance(w, InteractionWidget):
                if w.should_get_focus() and not focus_granted:
                    w.focus()
                    self._focus_widget = w
                    focus_granted = True
                else:
                    w.unfocus()
        if not focus_granted:
            self._focus_widget = None
    
    def draw(self, drawer: Drawer):
        if not self.is_open:
            return
        
        self.window_drawer.plane_color = drawer.plane_color
        self.window_drawer.clear()

        depth_order_widgets = sorted(self._widgets, key=lambda x: x._get_depth())
        for w in depth_order_widgets:
            # TODO: implement focus indication in Widgets themseleves rather than in Window
            if w is self._focus_widget:
                self.window_drawer.place_drawer(
                    Drawer(w.size.get_width(), w.size.get_height(), plane_color=self.window_drawer.plane_color),
                    pos = w.position.get_yx(),
                    opacity = 0.9,
                    border = False,
                    title = ""
                )
            w.draw(self.window_drawer)
        
        self._run_callbacks(OnDrawContext(drawer))

        drawer.place_drawer(
            self.window_drawer,
            pos = self.position.get_yx(),
            opacity = 0.9,
            border = self.has_border,
            title = self.title
        )
                

    def open(self):
        self.is_open = True
        return self._run_callbacks(OnOpenContext())
    
    def close(self, reason: int):
        self.is_open = False
        return self._run_callbacks(OnCloseContext(reason))