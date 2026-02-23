# this file contains custom classes that are imported to the main ui.py file


from textual.app import ComposeResult
from textual.widgets import Label
from textual.containers import Container



# Logo import
class ASCIname(Container):
    def compose(self) -> ComposeResult:
        try:
            with open("arts/linquix_ascii.txt", "r") as artfile:
                art = artfile.read()
        except FileNotFoundError:
            art = "LINQUIX"
        yield Label(art, id="ascii")

