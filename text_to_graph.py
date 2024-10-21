import asyncio
from neo4j import GraphDatabase
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
import neo4j_graphrag.llm
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

entities = [
    "Name",
    "Genus",
    "Species",
    "Cultivar",
    "Stem_colour",
    "flower_colour",
    "Sun_exposure",
    "Soil_types",
    "Moisture_levels",
    "Family",
    "Description",
    "Ph",
]
relations = ["BELONG TO", "HAVE", "DESCRIBE", "NEED"]

potential_schema = [
    ("Genus", "BELONG_TO", "Family"),
    ("Species", "BELONG_TO", "Genus"),
    ("NAME", "BELONG_TO", "Genus"),
    ("Name", "HAVE", "Description"),
    ("Name", "NEED", "Soil_types"),
    ("Name", "NEED", "Moisture_levels"),
    ("Name", "NEED", "Ph"),
    ("Name", "NEED", "Sun_exposure"),
    ("Name", "NEED", "Ph"),
]

embedder = OllamaEmbeddings(model="nomic-embed-text")

llm = Ollama(model="llama3")


# Instantiate the SimpleKGPipeline
kg_builder = SimpleKGPipeline(
    llm=llm,
    driver=driver,
    embedder=embedder,
    entities=entities,
    relations=relations,
    on_error="IGNORE",
    from_pdf=False,
)

corpus_folder = "corpus"
for file_name in os.listdir(corpus_folder):
    file_path = os.path.join(corpus_folder, file_name)
    if os.path.isfile(file_path) and file_name.endswith(".txt"):
        with open(file_path) as f:
            text = f.read()
            asyncio.run(kg_builder.run_async(text=text))


driver.close()
