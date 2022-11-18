import fastapi
import uvicorn
from fastapi.responses import HTMLResponse, PlainTextResponse

app = fastapi.FastAPI()

@app.get("/")
async def get_index():
    with open("./web/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

@app.get("/script.js")
async def get_index():
    with open("./web/script.js", "r") as f:
        content = f.read()
    return PlainTextResponse(content)

@app.get("/styles.css")
async def get_index():
    with open("./web/styles.css", "r") as f:
        content = f.read()
    return PlainTextResponse(content)


uvicorn.run(app, host = "0.0.0.0")