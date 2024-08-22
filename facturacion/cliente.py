
import websockets
import json


import os

IP_BEW_SOCKET = os.environ.get('IP_BEW_SOCKET', 'default_value')

async def conectar_a_websocket(data):
	uri = IP_BEW_SOCKET  # Cambia la IP y el puerto según tu servidor

	# Convertir a formato de bytes
	mensaje_json = json.dumps(data).encode()

	
	async with websockets.connect(uri) as websocket:
		await websocket.send(mensaje_json)
		try:
			respuesta = await websocket.recv()
			while True:
				if respuesta:
					print("Respuesta recibida desde websocket: ")
					print(respuesta)
					return respuesta
		except websockets.ConnectionClosedError as e:
			print(e)
			print(respuesta)
			return e
				
