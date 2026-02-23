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
    self.call_from_thread(lambda: terminal_screen.write(grid))
    
    # Optional: Add an empty line for spacing
    self.call_from_thread(lambda: terminal_screen.write(""))




# this function used to set the content of the text displayed as status 
def set_status(self, status: str):
    status_line = self.query_one("#status-line", RichLog)

    #clear the existing line , we need to keep it one line
    status_line.clear()
    status_line.write(status)
    
