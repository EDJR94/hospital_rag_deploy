from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
from qa_chain import query_graph_database
from review_chain import review_from_vectorbase

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up the LLM
model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0
)

# Create tools using the existing functions
graph_qa_tool = StructuredTool.from_function(
    func=query_graph_database,
    name="GraphDatabaseQA",
    description="Use this tool when you need to query structured relationships and connections in the database. Useful for questions about connections between entities, finding paths, or querying structured data. This uses Neo4j Cypher queries behind the scenes."
)

review_vector_tool = StructuredTool.from_function(
    func=review_from_vectorbase,
    name="ReviewSearch",
    description="Use this tool when you need to find information about patient experiences, hospital reviews, physician feedback or any semantic search in reviews. This uses vector embeddings to find relevant reviews."
)

# List of tools
tools = [graph_qa_tool, review_vector_tool]

# Create the prompt template with the required agent_scratchpad
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an assistant that helps users find information about hospitals, physicians, and patient experiences.
    
You have access to two different tools:
1. GraphDatabaseQA: Use this for questions about relationships, connections between entities, or structured data queries.
2. ReviewSearch: Use this for questions about patient experiences, reviews, and feedback.

Choose the appropriate tool based on the nature of the user's question.
- If the query is about finding connections, relationships, or structured data (like "How many patients has Dr. Ryan Brown treated?"), use the GraphDatabaseQA tool.
- If the query is about patient experiences, reviews, or sentiment (like "Have any patients complained about noise?"), use the ReviewSearch tool.

Think carefully about which tool is most appropriate for each query."""),
    ("human", "{input}"),
    # Add the required MessagesPlaceholder for agent_scratchpad
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
agent = create_openai_tools_agent(model, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

# Function to run the agent
def run_agent(query):
    return agent_executor.invoke({"input": query})