from fastapi import FastAPI
from fastapi import Response
from fastapi import WebSocket
from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import typing
import json
import os

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# Bottle model
class Bottle(BaseModel):
	content: str = 'Hello world'
	status_code: int = 200
	headers: typing.Optional[typing.Dict[str, str]]
	media_type: str = 'text/html'


class BottleWebsocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, bottle: Bottle):
        for connection in self.active_connections:
            await connection.send_text(bottle)

# Bottles list, from memory
bottles = {}
# Websocket managers
managers = {}

@app.post("/set/{id}")
async def set_bottle(id: str, bottle: Bottle):
	if id in bottles:
		bottles[id] = bottle
		# await managers[id].broadcast(json.dumps({ 'eventType': 'update' }))
		return bottle
	else:
		return JSONResponse(status_code=400, content={"error": "Bottle does not exist."}) 

@app.post("/new/{id}")
async def new_bottle(id: str):
	bottles[id] = Bottle()
	# Tell all existing managers that a new bottle was created
	for manager in managers.values():
		await manager.broadcast(json.dumps({ 'eventType': 'new', 'bottle_id': id}))
	manager = BottleWebsocketManager()
	managers[id] = manager
	return bottles[id]

@app.get("/get")
def all_bottles():
	return bottles

# Returns info about a specific bottle
@app.get("/get/{id}", response_model=Bottle)
def info_bottle(id: str):
	if id in bottles:
		return bottles[id]
	return None

@app.get("/ui/")
async def bottle_ui_index(request: Request):
	return templates.TemplateResponse("ui.html", {"request": request, "bottle_id": ''})

@app.get("/ui/{id}", response_class=HTMLResponse)
async def bottle_ui(id: str, request: Request):
	print()
	return templates.TemplateResponse("ui.html", {"request": request, "bottle_id": id})

@app.websocket("/ws/{id}")
async def websocket_bottle(websocket: WebSocket, id: str):
	if id in managers:
		manager = managers[id]
		await manager.connect(websocket)
		try:
			while True:
				update = await websocket.receive_text() # Wait for bottle update from client
				await manager.broadcast(json.dumps({ 'eventType': 'update' })) # Ask all clients to update their bottle
		except Exception as e:
			manager.disconnect(websocket)

def get_interesting_data(request: Request):
	data = {}
	request = dict(request)
	print(request)
	data['type'] = request['type']
	data['http_version'] = request['http_version']
	data['server'] = request['server']
	data['client'] = f"{request['client'][0]}:{request['client'][1]}"
	data['method'] = request['method']
	data['path'] = request['path']
	data['query_string'] = request['query_string'].decode()

	# Headers
	data['headers'] = {}
	for header in request['headers']:
		data['headers'][header[0].decode()] = header[1].decode()
	data['path_params'] = request['path_params']

	return data

# Returns a bottle
@app.get("/bottle/{id}")
@app.post("/bottle/{id}")
async def bottle(id: str, request: Request):
	if id in bottles:
		bottle = bottles[id]
		await managers[id].broadcast(json.dumps({ 'eventType': 'bottle', 'bottle': get_interesting_data(request) }))
		response = Response(content=bottle.content, status_code=bottle.status_code, headers=bottle.headers, media_type=bottle.media_type)
		return response
	return