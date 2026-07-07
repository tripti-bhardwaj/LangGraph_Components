from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

model = ChatOllama(model = "qwen2.5:3b")
thread_id = '1'

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

conn = sqlite3.connect(database = 'chatbot.bd', check_same_thread = False)
checkpointer = SqliteSaver(conn)
graph = StateGraph(ChatState)

graph.add_node('ChatNode', chatbot)

graph.add_edge(START, 'ChatNode')
graph.add_edge('ChatNode', END)

workflow = graph.compile(checkpointer = checkpointer)

# print(list(checkpointer.list(None)))
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

# response = workflow.invoke(
#     {'messages': [HumanMessage (content = 'What is my name? And, what recipe did I ask for previously?')]},
#     config = {'configurable': {'thread_id': 'thread-1'}}
# )

# print(response)

# for message_chunk, metadata in workflow.stream(
#     {'messages': [HumanMessage (content = 'What is the recipe of alfredo pasta?')]},
#     config = {'configurable': {'thread_id': thread_id}},
#     stream_mode = 'messages'
# ):
#     if message_chunk.content:
#         print(message_chunk.content, end = " ", flush = True)

# while True:
#     user_query = input('Enter your prompt: ')
#     if user_query.strip().lower() in ['exit', 'bye', 'quit']:
#         break
#     config = {'configurable': {'thread_id': thread_id}}
#     response = workflow.invoke({'messages': [HumanMessage (content = user_query)]}, config = config)
#     print('AI: ', response['messages'][-1].content)