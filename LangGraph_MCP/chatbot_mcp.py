from langgraph.graph import StateGraph, START
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOllama(model="qwen2.5:3b")

client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": "python3",          
            "args": ["file_path/main.py"],
        }
    }
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph():
    tools = await client.get_tools()
    print(tools)
    llm_with_tools = llm.bind_tools(tools)
    async def chat_node(state: ChatState):
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {'messages': [response]}
    tool_node = ToolNode(tools)
    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
    chatbot = graph.compile()
    return chatbot

async def main():
    chatbot = await build_graph()
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="Find the modulus of 132354 and 23 and give answer like a cricket commentator.")]})
    print(result['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())