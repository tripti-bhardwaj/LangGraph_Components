from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

model = ChatOllama(model = "qwen2.5:3b")
thread_id = '1'

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: ChatState):
    messages = state['messages']
    response = model.invoke(messages)
    return {'messages': [response]}

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)

graph.add_node('ChatNode', chatbot)

graph.add_edge(START, 'ChatNode')
graph.add_edge('ChatNode', END)

workflow = graph.compile(checkpointer = checkpointer)

# for message_chunk, metadata in chatbot.stream(
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