# this file contains python textual TUI code setup 
from groq import APIConnectionError

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Container, Vertical
from textual.widgets import Button, Label, ContentSwitcher, TextArea
from textual import work

from TUI.ui_classes import ASCIname, TerminalScreen, StatusBar, UserInput 
from TUI.ui_helper_functions import write_log, toggle_loading_bar

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
        self.query_one("#loading_bar").styles.display = "none"

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

        # get the state to check this resume of previous run or fresh run
        state = graph.get_state(self.config)
        
        # state found means this resumed run
        if state and state.next == ("tools",):
            if user_text.lower() in ['y', 'yes']:
                write_log(self, icon= "  [green] [/] ", content = "[green]Execution Approved.[/]" )
                self.run_agent_graph(None) 
            else:
                write_log(self, icon= "  [red] [/] ", content = "[red]Execution Denied.[/]" )
            return 

        # no state found means fresh run 
        write_log(self, icon="  [green] [/] ", content = user_text)
        self.run_agent_graph(user_text)
    

    @work(exclusive=True,thread=True) # run graph logic in a background worker thread
    async def run_agent_graph(self, user_text: str | None) -> None:
        # set loading indicator safely from the worker thread
        # self.call_from_thread(toggle_loading_bar(self))
        toggle_loading_bar(self)

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
                    lambda d=current_dir: setattr(self.query_one("#input_box"), "border_title", f'> {d}')
                )

                # if it's an AI message, display it in the terminal
                if last_message.type == "ai" and last_message.content:
                    write_log(self,"  [blue] [/] ", last_message.content, is_markdown=True)


            # for loop stops when called interrupt or finished
            # check if the graph paused because it was interrupted to run a tool or finished
            if state.next == ("tools",):
                tool_calls = last_message.tool_calls
                for tc in tool_calls:
                    tool_name = tc['name']
                    tool_args = tc['args']
                    
                    if tool_name == "bash_tool":
                        cmd_to_run = tool_args.get('cmd')
                        warning = f"[bold yellow]Terminal Execution Request[/]\nAgent wants to run: [cyan]'{cmd_to_run}'[/]\nAllow? (y/n)"
                        write_log(self, "  [yellow] [/] ", content = warning )
                
                
        except APIConnectionError as e:
            self.notify(
                    title = 'Error',
                    message = str(e),
                    severity = 'error', 
                    timeout = 3
            )


        finally:
            # hide loading indicator once finished or paused
            toggle_loading_bar(self)





app = App()
