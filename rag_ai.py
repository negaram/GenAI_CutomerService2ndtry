from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_hub.tools.tavily_research import TavilyToolSpec
from prompts import assistant_prompt  
from helper_functions import (fetch_user_flight_information, 
                              search_flights, 
                              cancel_ticket, 
                              update_ticket_to_new_flight,
                              book_hotel,
                              cancel_hotel,
                              update_hotel,
                              search_hotels,
                              book_car_rental,
                              cancel_car_rental,
                              update_car_rental,
                              search_car_rentals,
                              book_excursion,
                              search_trip_recommendations,
                              update_excursion,
                              cancel_excursion
                            )
from dotenv import load_dotenv
import os
from create_database import db

load_dotenv()

llm = Ollama (base_url='http://localhost:11434', model="llama", request_timeout=360)

parser = LlamaParse(result_type="markdown")
file_extractor = {".docx": parser}

# embed_model = resolve_embed_model("local:BAAI/bge-m3")
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

if os.path.exists('./storage'):
    storage_context = StorageContext.from_defaults(persist_dir='./storage')
    vector_index = load_index_from_storage(storage_context=storage_context)
else:    
    documents = SimpleDirectoryReader("./data").load_data()
    vector_index = VectorStoreIndex.from_documents(documents)    
    vector_index.storage_context.persist()

query_engine = vector_index.as_query_engine(llm=llm)

lookup_policy = QueryEngineTool(
                        query_engine=query_engine,
                        metadata=ToolMetadata(
                            description="""Consult the company policies to check whether certain options are permitted.
                                            Use this before making any flight changes performing other 'write' events.""",
                            name='policy_documentation'
                        )
                    )

tavily_tool = TavilyToolSpec(
    api_key='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',
)

tools = [
    tavily_tool.to_tool_list()[0],
    lookup_policy,
    fetch_user_flight_information,
    search_flights,
    update_ticket_to_new_flight,
    cancel_ticket,
    book_hotel,
    cancel_hotel,
    update_hotel,
    search_hotels,
    book_car_rental,
    cancel_car_rental,
    update_car_rental,
    search_car_rentals,
    book_excursion,
    search_trip_recommendations,
    update_excursion,
    cancel_excursion
]

agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=assistant_prompt)

conversation_history = []

def store_interaction(user_question, agent_response):
    conversation_history.append({"question": user_question, "response": agent_response})

def get_conversation_context():
    # Concatenate previous Q&A pairs into a single string
    context = ""
    for interaction in conversation_history:
        context += f"Q: {interaction['question']} A: {interaction['response']} "
    return context
    


while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    retries = 0
    while retries < 3:
        try:
            # result = agent.query(prompt)
            context = get_conversation_context()
            full_prompt = context + f"Q: {prompt} A: "
    
            result = agent.query(full_prompt)
            break
        except Exception as e:
            retries += 1
    
    if retries >= 3:
        print("Unable to process request, try again...")
        continue
    
    print(result)