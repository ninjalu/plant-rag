from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from rag import get_rag_resp

# input = "What's the best plant for a north facing garden with clay soil. I like purple flower in autumn as well as summer? Height: about 0.9m to 1.2m. Please list the top cultivars for autumn interest"
app = FastAPI(title="PlantRAG")


# print(get_rag_resp(input))
@app.get("/", response_class=HTMLResponse)
async def read_form():
    return """
    <html>
        <head>
            <title>Plant RAG</title>
        </head>
        <body>
            <h1>Plant RAG</h1>
            <form action="/query" method="post">
                <label for="query">What can I help you with plant recommendations:</label>
                <input type="text" id="query" name="query">
                <input type="submit" value="Submit">
            </form>
        </body>
    </html>
    """


@app.post("/query", response_class=HTMLResponse)
async def handle_query(query: str = Form(...)):
    response = get_rag_resp(query)
    return f"""
    <html>
        <head>
            <title>Plant RAG</title>
        </head>
        <body>
            <h1>Plant RAG</h1>
            <form action="/query" method="post">
                <label for="query">Enter your query:</label>
                <input type="text" id="query" name="query">
                <input type="submit" value="Submit">
            </form>
            <h2>Response:</h2>
            <p>{response}</p>
        </body>
    </html>
    """
