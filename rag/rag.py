from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_ollama import OllamaEmbeddings, OllamaLLM, ChatOllama
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from langchain.agents import create_openai_tools_agent, AgentExecutor
import chromadb
from dotenv import load_dotenv


def get_rag_resp(input):
    llm = OllamaLLM(model="llama3")
    # input = "What's the best plant for a north facing garden with clay soil. I like purple flower in autumn as well as summer? Height: about 0.9m to 1.2m. Please list the top cultivars for autumn interest"

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

    # ## chain
    # doc_chain = create_stuff_documents_chain(llm, prompt)

    # retriever
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    persistent_client = chromadb.PersistentClient("chroma_plants_db")
    # collection = persistent_client.get_collection("rhs_plants")
    vector_store = Chroma(
        client=persistent_client,
        # collection=collection,
        embedding_function=embeddings,
    )
    vec_retriever = vector_store.as_retriever()
    # retriever_chain = create_retrieval_chain(vec_retriever, doc_chain)

    # use langchain tools
    retriever_tool = create_retriever_tool(
        retriever=vec_retriever,
        name="RHS_plants",
        description="All knowledge on draught tolerant planting",
    )
    wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
    wiki = WikipediaQueryRun(api_wrapper=wiki_api)

    tools = [wiki, retriever_tool]

    chat_prompt = hub.pull("hwchase17/openai-functions-agent")

    chat_llm = ChatOllama(model="llama3.2", temperature=0)
    agent = create_openai_tools_agent(tools=tools, llm=chat_llm, prompt=chat_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    response = agent_executor.invoke(input={"input": input})
    return response["output"]
