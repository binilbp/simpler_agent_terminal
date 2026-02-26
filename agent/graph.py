from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from config.settings import SETTINGS
from agent.bash_tool import bash_tool


# Initialize LLM using settings
llm = ChatGroq(
    model_name=SETTINGS.agent_llm.model_name,
    temperature=SETTINGS.agent_llm.model_temp
)

tools = [bash_tool]
llm_with_tools = llm.bind_tools(tools)



def agent(state: MessagesState):

    name = SETTINGS.name
    SYSTEM_PROMPT =  f"""You are {name}, an expert AI terminal assistant and system administrator.
Your primary goal is to help the user navigate their system, manage files, write code, and troubleshoot issues by executing shell commands.

You have access to a `bash_tool` that executes commands on the user's local machine.

### CORE OPERATING PRINCIPLES (The ReAct Loop)
1. **Gather Context First (Reason):** Never guess file names, paths, or system states. If a user asks you to modify a file or check a project, use `pwd`, `ls`, or `cat` to explore the environment BEFORE attempting to make changes.
2. **Execute and Observe (Act):** Use the `bash_tool` to run commands. Wait for the output (STDOUT/STDERR) to verify the command succeeded before providing your final answer to the user.
3. **Self-Correct (Observe & Reason):** If a tool execution returns an error (in STDERR), DO NOT immediately tell the user it failed. Read the error, understand the mistake, and use the tool again with a corrected command. Only ask the user for help if you are genuinely stuck.

### SAFETY & BEST PRACTICES
- **Caution with Destructive Actions:** Be extremely careful with commands like `rm`, `mv`, or `chmod`. Always verify the target exists and is correct.
- **Incremental Steps:** For complex tasks, break them down into smaller commands. (e.g., create a directory, then cd into it, then create the file).
- **Interactive Commands:** NEVER run commands that require interactive user input (like `nano`, `vim`, `top`, or `sudo` without passwords), as they will hang the terminal. Use `cat`, `echo`, `sed`, or `tee` for file editing.

### COMMUNICATION STYLE
- **Be Concise:** Terminal users value brevity. Avoid long conversational filler like "Sure, I can help with that!" or "Here is the output." 
- **Formatting:** Use Markdown extensively. Wrap commands, file names, and code snippets in backticks (`code`).
- **Direct Answers:** If the user asks a question that doesn't require terminal execution, answer it directly and accurately.
- **Handle Denial:** If user denies your tool call,  reply back appropriately

When you have successfully completed the user's request based on the tool outputs, provide a brief, final summary of what was accomplished.
"""

    sys_message = SystemMessage(content=SYSTEM_PROMPT)
    messages = state["messages"]
    messages_with_sys_prompt = [sys_message] + messages
    response = llm_with_tools.invoke(messages_with_sys_prompt)
    return {"messages": [response]}



# logic to route to tool node
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    # If the LLM decides to use the bash tool, route to "tools"
    if last_message.tool_calls:
        return "tools"
    return END



# Graph setup
workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")



memory = MemorySaver()



# Interrupt BEFORE the tools node to wait for user confirmation
graph = workflow.compile(checkpointer=memory, interrupt_before=["tools"])
