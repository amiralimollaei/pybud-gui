from pybud.drawer import ansi
from pybud.session import Session
from pybud.window import Window
from pybud.widgets import TextBox, Label, ComboBox, VerticalMultipleChoice

class Main(Window):
    def __init__(self):
        super().__init__(
            size = (76, 14),
            position = (0, 0),
            has_border = False,
            opacity = 1.0,
            title = "PyBUD: GUI Beauty"
        )
        
        title = ansi.AnsiString("PyBUD: GUI Beauty", fore = (20, 250, 120))
        title.add_graphics(ansi.AnsiGraphicMode.BOLD | ansi.AnsiGraphicMode.UNDERLINE)
        
        title = ansi.AnsiString("[ ") + title + ansi.AnsiString(" ]")

        self.add_widget(Label(
            title,
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 1),
        ))
        
        caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, ansi color optimizations written in Rust, and more!"
        
        self.add_widget(Label(
            caption,
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 2),
        ))
        self.add_widget(TextBox(
            "TextBox: ",
            size = (self.size.width//2 - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 6),
        ))
        self.add_widget(ComboBox(
            "ComboBox: ",
            options = {
                "Nice!": self.nice_option,
                "Very Good!": self.verygood_option,
                "Awesome!": self.awesome_option,
                "Briliant!": self.briliant_option,
            },
            size = (self.size.width//2 - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (self.size.width//2 + 2, 6),
        ))
        self.add_widget(VerticalMultipleChoice(
            "VerticalMultipleChoice:",
            # the text and callback function for each option
            options = {
                "Nice!": self.nice_option,
                "Very Good!": self.verygood_option,
                "Awesome!": self.awesome_option,
                "Briliant!": self.briliant_option,
            },
            size = (self.size.width-4, 1),  # height will be owerwritten in WidgetOptions
            position = (2, 8),
        ))
        self.add_widget(Label(
            ansi.AnsiString("Tip: ", fore = (255, 128, 0)) +
            ansi.AnsiString("Use TAB or arrow keys to switch between Widgets, Use ") +
            ansi.AnsiString("Ctrl + C", fore = (255, 128, 0)) + ansi.AnsiString(" to exit the demo."),
            centered = True,
            size = (self.size.width - 26, 1),  # height will be owerwritten in WidgetLabel
            position = (22, 9),
            name = "tip-label"
        ))
        self.lbl_result = Label(
            "",
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 12),
            name = "result-label"
        )
        self.add_widget(self.lbl_result)

    def briliant_option(self):
        self.lbl_result.text = "Briliant!"

    def verygood_option(self):
        self.lbl_result.text = "Very Good!"

    def nice_option(self):
        self.lbl_result.text = "Nice!"

    def awesome_option(self):
        self.lbl_result.text = "Awesome!"


if __name__ == "__main__":
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    main_window = Main()
    s = Session((76, 14), background=(90, 110, 220))
    s.add_window(main_window)
    s.show()

    print(f"Session Closed! Widget Data:\n")
    for i, w in enumerate(main_window._widgets):
        print(w.name + ":")
        if isinstance(w, TextBox):
            print(f"- text=\"{w.text}\", input=\"{w.input}\"")
        elif isinstance(w, (VerticalMultipleChoice, ComboBox)):
            print(f"- selected_option_id={w.selected_option_id}")
            print(f"- selected option text=\"{list(w.options)[w.selected_option_id]}\"")
        if isinstance(w, Label):
            print(f"- text=\"{w.text}\"")
        else:
            print("- no data")
        print("")