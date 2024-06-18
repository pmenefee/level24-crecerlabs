import asyncio
import websockets

clients = []

async def handle_messages(websocket, path):
    global clients
    
    message = await websocket.recv()
    