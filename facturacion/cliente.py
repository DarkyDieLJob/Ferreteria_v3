# -*- coding: utf-8 -*-
import asyncio
import websockets
import json

import logging

logger = logging.getLogger(__name__)
from core_config.settings import IP_BEW_SOCKET # Ensure this setting is correctly configured

async def conectar_a_websocket(data):
    """
    Connects to a WebSocket server, sends JSON data, and receives a response.
    Logs interaction details and handles potential errors.

    Args:
        data (dict): The dictionary to be sent as JSON to the WebSocket server.

    Returns:
        dict: The parsed JSON response from the server, or an error dictionary
              if connection, communication, or parsing fails.
    """
    uri = IP_BEW_SOCKET
    mensaje_json = json.dumps(data).encode('utf-8') # Specify encoding explicitly

    logger.info(f"Intentando conectar a websocket: {uri}")
    logger.debug(f"Enviando datos: {data}") # Log the data being sent (consider redacting sensitive info if necessary)

    try:
        # Consider adding timeouts to connect and recv operations
        # async with websockets.connect(uri, open_timeout=10, close_timeout=5) as websocket:
        async with websockets.connect(uri) as websocket:
            logger.info("Conexión Websocket establecida.")
            await websocket.send(mensaje_json)
            logger.debug("Mensaje enviado al websocket.")

            # Add timeout for receiving response
            # respuesta = await asyncio.wait_for(websocket.recv(), timeout=10)
            respuesta = await websocket.recv()
            logger.debug(f"Respuesta cruda recibida del websocket (tipo: {type(respuesta)})")
            # Log the raw response only at debug level, it might be large
            # logger.debug(f"Contenido crudo: {respuesta}") # Uncomment if needed for deep debug

            if isinstance(respuesta, (str, bytes)): # Handle bytes too, decode if necessary
                if isinstance(respuesta, bytes):
                    try:
                        respuesta_str = respuesta.decode('utf-8')
                    except UnicodeDecodeError as ude:
                        logger.error(f"Error al decodificar respuesta bytes como UTF-8: {ude}", exc_info=True)
                        return {"error": "Respuesta bytes no es UTF-8 válido", "respuesta_bytes": respuesta.hex()} # Return hex representation
                else:
                    respuesta_str = respuesta

                try:
                    respuesta_json = json.loads(respuesta_str)
                    logger.debug(f"Respuesta parseada como JSON (tipo: {type(respuesta_json)}): {respuesta_json}")
                    logger.info("Respuesta JSON recibida y parseada exitosamente.")
                    return respuesta_json
                except json.JSONDecodeError as e:
                    # Log warning as the communication worked, but format is wrong
                    logger.warning(f"Error al decodificar respuesta como JSON: {e}. Respuesta recibida: {respuesta_str}", exc_info=False)
                    return {"error": "Respuesta no es JSON válido", "respuesta": respuesta_str}
            else:
                 # Log warning if the type is unexpected
                 logger.warning(f"Respuesta del websocket no es una cadena o bytes (tipo: {type(respuesta)}).")
                 return {"error": "Respuesta no es una cadena o bytes", "respuesta": str(respuesta)}

    except websockets.ConnectionClosedError as e:
        # Connection closed, could be normal or error
        logger.warning(f"Conexión websocket cerrada: Código={e.code}, Razón='{e.reason}'", exc_info=False)
        return {"error": "Conexión cerrada", "code": e.code, "reason": e.reason}
    except websockets.exceptions.InvalidURI:
        logger.error(f"URI del websocket inválida: '{uri}'", exc_info=True)
        return {"error": "URI inválida", "uri": uri}
    except ConnectionRefusedError as e:
         logger.error(f"Conexión websocket rechazada para URI: '{uri}'. ¿Servidor corriendo?", exc_info=True)
         return {"error": "Conexión rechazada", "uri": uri}
    except asyncio.TimeoutError as e: # Catch timeouts if added above
        logger.error(f"Timeout durante la operación websocket con {uri}", exc_info=True)
        return {"error": "Timeout en operación websocket"}
    except Exception as e:
        # Catch-all for other unexpected errors during connect/send/recv
        logger.error(f"Error inesperado durante la comunicación websocket con {uri}.", exc_info=True)
        return {"error": "Error inesperado de websocket", "detalle": str(e)}