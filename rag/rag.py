from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_ollama import OllamaEmbeddings
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_openai_tools_agent
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = Ollama(model="llama3")

## Prompt template
prompt = ChatPromptTemplate.from_template(
    """
    Answer the following question based only on the provided context.
    Think step by step before providing a detailed answer.
    <context>
    {context}
    </context>
    Question: {input}
    """
)

## chain
doc_chain = create_stuff_documents_chain(llm, prompt)

# retriever
embeddings = OllamaEmbeddings(model="nomic-embed-text")
persistent_client = chromadb.PersistentClient("chroma_plants_db")
collection = persistent_client.get_collection("rhs_plants")
vector_store = Chroma(
    client=persistent_client,
    # collection=collection,
    embedding_function=embeddings,
)
retriever = vector_store.as_retriever()
retriever_chain = create_retrieval_chain(retriever, doc_chain)

response = retriever_chain.invoke(
    {
        "input": "What's the best plant for a north facing garden with clay soil. I like purple flower in autumn as well as summer? Height: about 0.9m to 1.2m. Please list the top cultivars for autumn interest"
    }
)
try:
    print(response["answer"])
    print(response["context"])
except KeyError as e:
    print(e)


# # use langchain tools

# wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
# wiki = WikipediaQueryRun(api_wrapper=wiki_api)

# tools = [wiki]

# openai = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
# prompt = hub.pull("hwchase17/openai-functions-agent")

# agent = create_openai_tools_agent(tools=tools, openai=openai, prompt=prompt)
