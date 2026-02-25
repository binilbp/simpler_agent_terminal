# this file contains python textual TUI code setup 


from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Vertical
from textual.widgets import Button, Label, ContentSwitcher, TextArea
from textual import work

from TUI.ui_classes import ASCIname, TerminalScreen, StatusBar, UserInput 
from TUI.ui_helper_functions import write_log

from langchain_core.messages import HumanMessage
from agent.graph import graph
from agent.bash_tool import bash_core



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

        #focus on input box
        self.query_one("#input_box").focus()

        #config settings
        self.config = {"configurable": {"thread_id": "session_1"}}



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


    # this functino is called by the cutom class 'ChatInput' created 
    def handle_submission(self, user_text: str) -> None:
        write_log(self, icon="  [green] [/] ", content = user_text)

        # get the state to check this resume of previous run or fresh run
        state = graph.get_state(self.config)
        
        # state found means this resumed run
        if state and state.next == ("tools",):
            if user_text.lower() in ['y', 'yes']:
                write_log(self, "", "[bold green]Execution Approved.[/]", is_markdown=True)
                self.run_agent_graph(None) 
            else:
                write_log(self, "", "[bold red]Execution Denied.[/]", is_markdown=True)
            return 

        # no state found means fresh run
        self.run_agent_graph(user_text)
    

    @work(exclusive=True,thread=True) # run graph logic in a background worker thread
    async def run_agent_graph(self, user_text: str | None) -> None:
        # set loading indicator safely from the worker thread
        self.call_from_thread(lambda: setattr(self.query_one("#loading-bar"), "styles.display", "block"))
        
        try:
            # if user_text is provided, it's a new request. If None, we are resuming after an approval.
            inputs = {"messages": [HumanMessage(content=user_text)]} if user_text else None
            
            # stream the execution events from LangGraph
            for event in graph.stream(inputs, self.config, stream_mode="values"):
                last_message = event["messages"][-1]
                state = graph.get_state(self.config)

                # read current cwd from bash_core and update the UI securely on the main thread
                current_dir = bash_core.cwd
                self.call_from_thread(
                    lambda d=current_dir: setattr(self.query_one("#input_box"), "border_title", d)
                )

                # check if the graph paused because it wants to run a tool
                if state.next == ("tools",):
                    tool_calls = last_message.tool_calls
                    for tc in tool_calls:
                        tool_name = tc['name']
                        tool_args = tc['args']
                        
                        if tool_name == "bash_tool":
                            cmd_to_run = tool_args.get('cmd')
                            warning = f"[bold yellow]Terminal Execution Request[/]\nAgent wants to run: [cyan]'{cmd_to_run}'[/]\nAllow? [y/N]"
                            write_log(self, "⚠️", warning, is_markdown=True)
                        else:
                            warning = f"[bold yellow]Tool Execution Request[/]\nAgent wants to use: [cyan]{tool_name}[/]\nWith args: {tool_args}\nAllow? [y/N]"
                            write_log(self, "⚙️", warning, is_markdown=True)
                    
                    break # Stop streaming, wait for user input from the UI
                
                # otherwise, if it's an AI message, display it in the terminal
                elif last_message.type == "ai" and last_message.content:
                    write_log(self,"  [blue] [/] ", last_message.content, is_markdown=True)

        finally:
            # hide loading indicator once finished or paused
            self.call_from_thread(lambda: setattr(self.query_one("#loading-bar"), "styles.display", "none"))





app = App()
