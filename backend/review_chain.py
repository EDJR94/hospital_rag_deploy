from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_neo4j import Neo4jVector 
from langchain.prompts import (
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI=os.getenv("NEO4J_URI")
NEO4J_USERNAME=os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD=os.getenv("NEO4J_PASSWORD")
model = ChatOpenAI(model='gpt-4o-mini', api_key=OPENAI_API_KEY)
embedding = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=embedding,
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name='reviews',
    node_label='Review',
    text_node_properties=[
        "physician_name",
        "patient_name",
        "text",
        "hospital_name",
    ],
    embedding_node_property='embedding'
)

neo4j_retriever = neo4j_vector_index.as_retriever(search_kwargs={"k":3})

review_template = """Your job is to use patient
reviews to answer questions about their experience at a hospital. Use
the following context to answer questions. Be as detailed as possible, but
don't make up any information that's not from the context. If you don't know
an answer, say you don't know.
{context}

Question: {question}
"""

review_prompt = ChatPromptTemplate.from_template(review_template)

def review_from_vectorbase(question):
    review_chain = (
        {'context': neo4j_retriever, "question":RunnablePassthrough()}
        | review_prompt
        | model
        | StrOutputParser()
    )

    response = review_chain.invoke(question)

    return response

