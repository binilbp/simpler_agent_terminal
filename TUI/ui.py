# this file contains python textual TUI code setup 


from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button
from TUI.ui_classes import ASCIname


class App(App):
    CSS_PATH = 'ui.tcss'
    theme = 'dracula'



    def on_mount(self) -> None:
        pass


    def compose(self) -> ComposeResult:
        with Horizontal(id='logo-and-contentswitcher'):
            yield ASCIname()
            yield Button('', id='terminal-button')
            yield Button('', id='info-button')


app = App()
