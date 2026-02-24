# this file contains python textual TUI code setup 


from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Vertical
from textual.widgets import Button, Label, ContentSwitcher
from TUI.ui_classes import ASCIname, TerminalScreen, StatusBar, UserInput


class App(App):
    CSS_PATH = 'ui.tcss'
    theme = 'dracula'



    def compose(self) -> ComposeResult:
        with Horizontal(id='logo_and_contentswitcher'):
            yield ASCIname()
            yield Button('', id='terminal_button')
            yield Button('', id='info_button')

        with ContentSwitcher(initial='terminal'):
            with Vertical(id='terminal'):
                yield TerminalScreen()
                yield StatusBar()
                yield UserInput()

            yield Label('info screen',id='info')



    def on_mount(self) -> None:
        # set the default color and border color for content buttons
        self.query_one('#terminal_button').add_class("active_button")

        # hide the loading bar 
        self.query_one("#loading-bar").styles.display = "none"



    def on_button_pressed(self, event: Button.Pressed) -> None:
        # switch the color and boder color on button pressed
        if event.button.id=='terminal_button':
            self.query_one(ContentSwitcher).current = 'terminal' 
            self.query_one('#terminal_button').add_class("active_button")
            self.query_one('#info_button').remove_class("active_button")

        elif event.button.id=='info_button': 
            self.query_one(ContentSwitcher).current = 'info' 
            self.query_one('#info_button').add_class("active_button")
            self.query_one('#terminal_button').remove_class("active_button")








app = App()
