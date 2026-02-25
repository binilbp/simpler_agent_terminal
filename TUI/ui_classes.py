# this file contains custom classes that are imported to the main ui.py file


from textual.events import Key
from textual.app import ComposeResult
from textual.widgets import Label, RichLog, LoadingIndicator, Button, TextArea
from textual.containers import Container, Horizontal, Vertical
from config.settings import SETTINGS



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
        self.query_one("#status-line", RichLog).write("Running as [green]NON-ROOT[/] user")



class ChatInput(TextArea):
    #overide textarea default key handling
    async def _on_key(self, event: Key) -> None:
        if event.key == "enter":
            # Stop the parent TextArea from inserting a newline
            event.stop()
            event.prevent_default()
            
            # Submit the text
            user_text = self.text.strip()
            if user_text:
                self.clear()
                self.app.handle_submission(user_text)
                
        elif event.key == "shift+enter":
            # Stop the parent TextArea from doing whatever it wants
            event.stop()
            event.prevent_default()
            
            # Manually insert the newline
            self.insert("\n")
            
        else:
            # rest given to parent class
            await super()._on_key(event)


class UserInput(Horizontal):
    def compose(self) -> ComposeResult:
        input_box = ChatInput(id="input_box")
        input_box.border_title = SETTINGS.default_dir
        input_box.placeholder = "Type your query here.. \nPress enter to send"
        input_box.highlight_cursor_line = False
        input_box.wrap = True
        yield input_box

