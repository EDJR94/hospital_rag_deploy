from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from dotenv import load_dotenv
import os

load_dotenv()

# Load credentials from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Set up the model
model = ChatOpenAI(model='gpt-4o-mini', api_key=OPENAI_API_KEY)

# Set up Neo4j Graph
graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD
)

# Create the GraphCypherQAChain
chain = GraphCypherQAChain.from_llm(
    llm=model,
    graph=graph,
    verbose=True,
    allow_dangerous_requests=True
)

def query_graph_database(query):
    response = chain.invoke({"query": query})

    return response['result']