from rich.table import Table
from textual.widgets import RichLog
from rich.markdown import Markdown



# this function allows to write content to terminal screen
# pass icon , then str, then specify if markdown or not
def write_log(self, icon: str, content: str, is_markdown: bool = False):
    

    terminal_screen = self.query_one("#terminal_screen", RichLog)
    
    # Create the invisible grid for alignment
    grid = Table.grid(padding=(0, 1))
    grid.add_column()  # Column 1: Icon
    grid.add_column()  # Column 2: Content

    # Decide how to render the content
    renderable_content = Markdown(content) if is_markdown else content

    # Add the row
    grid.add_row(icon, renderable_content)

    # Write to log (inside a thread-safe call)
    # self.call_from_thread(lambda: terminal_screen.write(grid))
    terminal_screen.write(grid)
    
    # Optional: Add an empty line for spacing
    # self.call_from_thread(lambda: terminal_screen.write(""))
    terminal_screen.write("")



# this function used to set the content of the text displayed as status 
def set_status(self, status: str):
    status_line = self.query_one("#status-line", RichLog)

    #clear the existing line , we need to keep it one line
    status_line.clear()
    status_line.write(status)
    


# used to enable or disable the laoding indicator
def toggle_loading_bar(self) -> None:
    loading_bar = self.query_one("#loading_bar")

    if loading_bar.styles.display == "none":
        loading_bar.styles.display = "block"
    else:
        loading_bar.styles.display = "none"



# used to toggle the agent operation mode
def toggle_operation_mode(self) -> None:
    mode_switch = self.query_one('#mode_switch')
    
    mode_display = self.query_one('#mode_display')
    # on state
    if mode_switch.value :
        mode_display.update("MANNUAL")
        set_status(self, "Ask user permission before command execution")

    # off state
    else:
        mode_display.update("AUTOMATIC")
        set_status(self, "Command execution without user permission")
