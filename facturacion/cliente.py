import websockets
import json

from core_config.settings import IP_BEW_SOCKET

async def conectar_a_websocket(data):
    uri = IP_BEW_SOCKET

    mensaje_json = json.dumps(data).encode()

    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(mensaje_json)
            respuesta = await websocket.recv()
            print(f"Respuesta del websocket (tipo: {type(respuesta)}): {respuesta}")

            if isinstance(respuesta, str):
                try:
                    respuesta_json = json.loads(respuesta)
                    print(f"Respuesta JSON: tipo: {type(respuesta_json)}: {respuesta_json}")
                    return respuesta_json
                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON: {e}")
                    return {"error": "Respuesta no es JSON válido", "respuesta": respuesta}
            else:
                print("Respuesta no es una cadena.")
                return {"error": "Respuesta no es una cadena", "respuesta": str(respuesta)}

    except websockets.ConnectionClosedError as e:
        print(f"Conexión cerrada: {e}")
        return {"error": "Conexión cerrada", "detalle": str(e)}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"error": "Error inesperado", "detalle": str(e)}