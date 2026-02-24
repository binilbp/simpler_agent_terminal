# this file contains custom classes that are imported to the main ui.py file


from textual.app import ComposeResult
from textual.widgets import Label, RichLog, LoadingIndicator, TextArea, Button
from textual.containers import Container, Horizontal, Vertical



# Logo import
class ASCIname(Container):
    def compose(self) -> ComposeResult:
        try:
            with open("arts/linquix_ascii.txt", "r") as artfile:
                art = artfile.read()
        except FileNotFoundError:
            art = "LINQUIX"
        yield Label(art, id="ascii")



# Display the chathistory and command output  
class TerminalScreen(Container):
    def compose(self) -> ComposeResult:
        terminal_screen = RichLog(
            id="terminal_screen",
            auto_scroll = True, 
            highlight=True, 
            markup = True
        )
        # terminal_screen.border_title = "Terminal"
        terminal_screen.can_focus = False
        yield terminal_screen 

    def on_mount(self) -> None:
        self.query_one("#terminal_screen", RichLog).write("  [blue] [/]  How can I help you today?\n", animate = True)



class StatusBar(Horizontal):
    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="loading-bar")
        status_line = RichLog(
                id="status-line",
                markup = True
        )
        yield status_line

    def on_mount(self) -> None:
        self.query_one("#status-line", RichLog).write("Running as [red]NON-ROOT[/] user")



class UserInput(Horizontal):
    def compose(self) -> ComposeResult:
        input_box = TextArea(id="input-box")
        input_box.border_title = "/home/binil/~"
        input_box.placeholder = "Type your query here..\nPress Enter to sent query"
        input_box.highlight_cursor_line = False
        yield input_box
        # with Vertical(id="input-buttons"):
        #     yield Button("", id="send-button")
        #     yield Button("", id="stop-button")

