import os
import operator
from typing import Annotated, TypedDict

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

os.remove("./checkpoints.sqlite")

class State(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

llm = ChatOllama(
    model="ministral-3:14b",
    temperature=0.0,
    streaming=False,
    verbose=True
)

with open("./systemprompt.md", "r", encoding="utf-8") as f:
    systemprompt = f.read()

def llm_call(state: dict):
    """LLM decides whether to call a tool or not"""

    return {
        "messages": [llm.invoke([SystemMessage(content=systemprompt)]+ state["messages"])]
    }
    
workflow = StateGraph(State)

workflow.add_node(llm_call)
workflow.add_edge(START, "llm_call")
workflow.add_edge( "llm_call", END)

# checkpointer = InMemorySaver()
# checkpointer = SqliteSaver.from_conn_string("checkpoints.sqlite")
with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
    graph = workflow.compile(checkpointer)

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}

    result = graph.invoke({"messages":[]}, config)
    print(result["messages"][0].content)

    user = ""
    while not user == "/break":
        print("Prompt: ", end="")
        user = input()
        message = HumanMessage(user)
        result = graph.invoke( {"messages": [message]}, config)
        print(result["messages"][-1].content)