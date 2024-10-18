## Data ingestion
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["NOMIC_API_KEY"] = os.getenv("NOMIC_API_KEY")
os.environ["OLLAMA_HOST"] = os.getenv("OLLAMA_HOST")
corpus_folder = "corpus"
# List to hold all documents
all_documents = []

# Iterate over all files in the corpus folder
for file_name in os.listdir(corpus_folder):
    file_path = os.path.join(corpus_folder, file_name)
    if os.path.isfile(file_path) and file_name.endswith(".txt"):
        # Initialize the TextLoader with the path to the text file
        loader = TextLoader(file_path)
        # Load the text file
        documents = loader.load()
        # Add the loaded documents to the list
        all_documents.extend(documents)


# batch documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_documents = text_splitter.split_documents(all_documents)

# Vector embeddings and Vector store
print("Starting to save to embedding store")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
batch_size = 5460
for i in range(0, len(all_documents), batch_size):
    batch = all_documents[i : i + batch_size]
    vector_store = Chroma.from_documents(
        collection_name="rhs_plants",
        documents=batch,
        embedding=embeddings,
        persist_directory="./chroma_plants_db",
    )
