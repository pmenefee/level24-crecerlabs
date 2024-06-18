import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/bytestream")
async def websocket_bytestream(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        print(data)
        await websocket.send_bytes(data)  # Echoing back the bytestream

@app.websocket("/ws/textstream")
async def websocket_textstream(websocket: WebSocket):
    await websocket.accept()
    for i in range(100):
        await websocket.send_text(f"Message {i}")
        await asyncio.sleep(1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
