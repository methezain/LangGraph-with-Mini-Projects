from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel
import random

load_dotenv()


user_prompt = "Tell me what is 2 multiplied by 32, and also give me a random number between 1 to 10 billion."

@tool
def calculator(x: float, y: float, operator: str) -> float:
    """
    performe arithmatic operations on given inputs based on given operator.
    """

    if operator == "+":
        return x + y
    elif operator == "-":
        return x - y
    elif operator == "*":
        return x * y
    elif operator == "/":
        if y == 0:
            Exception("Dominator cannot be 0")
        else:
            return x/y 
        

@tool 
def random_numbers() -> int:
    """It returns any random number between 1 and 10 billion."""
    return str(random.randint(1, 10000000000))

def llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

tools = [calculator, random_numbers]
tool_node = ToolNode(tools)

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0.9).bind_tools(tools)

graph = StateGraph(MessagesState)

graph.add_node("chat_node", llm_node)
graph.add_node("tools", tool_node)


graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
graph.add_edge("chat_node", END)

workflow = graph.compile()

from IPython.display import Image, display
display(Image(workflow.get_graph().draw_mermaid_png()))

result = workflow.invoke({
    "messages": [HumanMessage(content=user_prompt)]
})

print("\nFinal Answer:", result["messages"][-1].content)

