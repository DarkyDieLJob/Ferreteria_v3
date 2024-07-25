
import websockets
import json

from core_config.settings import IP_BEW_SOCKET

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
					print(respuesta)
					return respuesta
		except websockets.ConnectionClosedError as e:
			print(e)
			return e
				
