import asyncio
import json
import datetime

from websockets import server as websockets
from websockets import exceptions as wsexceptions


def get_time():
    dt = datetime.datetime.now()
    return dt.strftime("%H:%M:%S")


json_storage = {}
rooms: dict = {}
users: dict = {}

def load():
    global json_storage
    global rooms
    global users

    with open("storage.json", "r") as f:
        json_storage = json.load(f)


    rooms = json_storage["rooms"]
    for id, data in rooms.copy().items():
        rooms[int(id)] = data
        del rooms[id]
    users = json_storage["users"]

load()

class WSserver:
    def __init__(self):
        self.socket = None
        self.endpoints = {}
    
    def endpoint(self, name: str = None):
        def wrap(function):
            self.endpoints[name] = function
            return function
        return wrap
    

    def dump(self):
        copied_rooms = rooms.copy()
        copied_users = users.copy()

        for key, value in rooms.copy().items():
            val = value.copy()
            copied_rooms[str(key)] = val
            del copied_rooms[key]
            val["clients"] = []
        
        to_write = {"rooms": copied_rooms, "users": copied_users}
        with open("storage.json", "w") as f:
            json.dump(to_write, f, indent = 4)

    async def on_client_receive(
            self, 
            client: websockets.WebSocketServerProtocol, 
            data: dict,
            client_data: dict
        ):
        op = data.pop("op")
        if op == "send_message":
            text: str = data["text"]
            color: str = data["color"]
            if color != users[client.remote_address[0]]["last_color"]:
                if color.startswith("#") and len(color) == 7 and color[1:].isalnum():
                    users[client.remote_address[0]]["last_color"] = color
                    self.dump()
            if not (text.replace(" ", "").replace("\n", "")):
                return
            message = {
                "timestamp": get_time(),
                "author": users[client.remote_address[0]]["name"],
                "author_color": color,
                "message": text
            }
            message = json.dumps(message)
            message = "eval|insert_message(" + message + ")"
            room = client_data["last_channel"]
            room = rooms[int(client_data["last_channel"])]
            for i in room["clients"].copy():
                try:
                    await i.send(message)
                except:
                    # Already disconnected client.
                    await i.close()
                    room["clients"].remove(i)

        
        elif op == "authorize":
            load()
            ip_address = client.remote_address[0]
            if not ip_address in users:
                await client.send("eval|alert('Your IP address is not verified.')")
                return
            username = client_data["username"] = users[ip_address]["name"]
            sending_rooms = []
            
            for room in rooms.values():
                copied_room = room.copy()
                del copied_room["clients"]
                copied_room.pop("members", None)
                if (not room["private"]) or (username in room["members"]):
                    sending_rooms.append(json.dumps(copied_room))
            to_send = []
            
            for i in sending_rooms:
                to_send.append("insert_room(" + i + ")")
            
            to_send.append("switch_to_channel('0')")
            to_send.append(f"text_color = '{users[ip_address]['last_color']}'")
            to_send.append("insert_message({timestamp:" + "'" + get_time() + "'" + ", author: '[SERVER]', author_color: '#FFFFFF', message: 'Welcome.'})")
            to_send = "eval|" + ";".join(to_send)
            await client.send(to_send)
        
        elif op == "switch_channel":
            if int(data["id"]) in rooms:
                try:
                    rooms[int(client_data["last_channel"])]["clients"].remove(client)
                except ValueError:
                    pass
                client_data["last_channel"] = data["id"]
                rooms[int(data["id"])]["clients"].append(client)


    async def handle_client(self, client: websockets.WebSocketServerProtocol):
        client_data = {"last_channel": "0"}
        try:
            async for message in client:
                try:
                    data: dict = json.loads(message)
                except json.JSONDecodeError:
                    data = None
                if not isinstance(data, dict):
                    await client.close()
                    return
                if not ("op" in data):
                    await client.close()
                    return
                await self.on_client_receive(client, data, client_data)
        except wsexceptions.ConnectionClosedOK:
            await client.close()
            try:
                rooms[int(client_data["last_channel"])]["clients"].remove(client)
            except ValueError:
                pass

    
    async def start(self):
        self.socket = await websockets.serve(
            self.handle_client, 
            "0.0.0.0", 5050
        )
        self.future = future = asyncio.Future()
        await future
    
    def run(self):
        asyncio.run(self.start())
    
server = WSserver()
server.run()