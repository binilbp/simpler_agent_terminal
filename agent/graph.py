from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from config.settings import SETTINGS
from agent.bash_tool import bash_tool
from agent.llm import get_llm
from agent.get_prompt import get_prompt 


# Initialize LLM using settings
llm = get_llm()
tools = [bash_tool]
llm_with_tools = llm.bind_tools(tools)


# get the appropriate prompt based on config
SYSTEM_PROMPT = get_prompt()

def agent(state: MessagesState):

    
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
