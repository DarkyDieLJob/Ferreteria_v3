#!/usr/bin/env python
### Servidor fake WebSocket para pruebas de integración con la impresora fiscal
# Este script crea un servidor WebSocket que responde a cualquier mensaje recibido
import asyncio
import websockets
import logging
import json # <--- Importar la librería JSON

# Configuración del logger para ver mensajes
logging.basicConfig(level=logging.INFO)

# --- Configuración del Servidor ---
HOST_IP = "169.254.0.251" # O "0.0.0.0" para todas las interfaces
HOST_IP = "0.0.0.0"
PORT = 12000
PATH = "/ws"

# --- Estructura de Datos Fija a Devolver ---
# Define el diccionario exacto que quieres que el servidor devuelva
respuesta_fija = {
    'rta': [{
        'action': 'dailyClose',
        'rta': {
            'monto_iva_no_inscripto': '0.00',
            'cant_nc_canceladas': '0',
            'RESERVADO_SIEMPRE_CERO': '0',
            'cant_doc_nofiscales_homologados': '0',
            'ultima_nc_a': '0',
            'ultima_nc_b': '0',
            'monto_percepciones': '0.00',
            'monto_percepciones_nc': '0.00',
            'monto_credito_nc': '0.00',
            'ultimo_doc_a': '4498',
            'ultimo_doc_b': '83894',
            'cant_doc_fiscales_a_emitidos': '2',
            'zeta_numero': '2285',
            'monto_imp_internos_nc': '0.00',
            'cant_doc_fiscales': '40',
            'cant_doc_fiscales_bc_emitidos': '38',
            'monto_iva_no_inscripto_nc': '0.00',
            'cant_nc_bc_emitidos': '0',
            'ultimo_remito': '0',
            'cant_doc_fiscales_cancelados': '0',
            'monto_iva_doc_fiscal': '54059.39',
            'monto_imp_internos': '0.00',
            'status_fiscal': '0600',
            'status_impresora': 'C080',
            'cant_nc_a_fiscales_a_emitidos': '0',
            'monto_iva_nc': '0.00',
            'monto_ventas_doc_fiscal': '311485.01',
            'cant_doc_nofiscales': '0'
        }
    }]
}
# Convierte el diccionario a una cadena JSON una sola vez
respuesta_fija_json = json.dumps(respuesta_fija)


async def handler(websocket, path):
    """
    Esta función se ejecuta para cada cliente WebSocket que se conecta.
    Ahora enviará una respuesta JSON fija después de recibir cualquier mensaje.
    """
    client_address = websocket.remote_address
    logging.info(f"Cliente conectado desde: {client_address} en path '{path}'")

    if path != PATH:
        logging.warning(f"Cliente conectado al path incorrecto '{path}'. Esperado: '{PATH}'. Desconectando.")
        await websocket.close(code=1003, reason="Path incorrecto")
        return

    try:
        async for message in websocket:
            logging.info(f"Mensaje recibido de {client_address}: {message}")

            # --- Enviar la respuesta JSON fija ---
            # En lugar de enviar un eco, enviamos la estructura JSON predefinida.
            await websocket.send(respuesta_fija_json)
            logging.info(f"Respuesta JSON fija enviada a {client_address}.")
            # Puedes descomentar la línea de abajo si quieres ver el JSON enviado
            # logging.debug(f"JSON enviado: {respuesta_fija_json}")

            # NOTA: Si necesitaras enviar esta respuesta SOLO cuando el mensaje
            #       recibido es específico (ej. si message == 'getCierreZ'),
            #       deberías agregar un 'if message == "tu_comando":' aquí.
            #       Actualmente, responde a CUALQUIER mensaje recibido.

    except websockets.exceptions.ConnectionClosedOK:
        logging.info(f"Cliente {client_address} desconectado limpiamente.")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Cliente {client_address} desconectado con error: {e}")
    except Exception as e:
        logging.error(f"Error inesperado con el cliente {client_address}: {e}")
        if not websocket.closed:
            await websocket.close(code=1011, reason="Error interno del servidor")
    finally:
        logging.info(f"Conexión finalizada con {client_address}.")

async def main():
    """
    Función principal para iniciar el servidor WebSocket.
    """
    logging.info(f"Iniciando servidor WebSocket en ws://{HOST_IP}:{PORT}{PATH}")
    try:
        async with websockets.serve(handler, HOST_IP, PORT):
            await asyncio.Future() # Mantiene el servidor corriendo
    except OSError as e:
        logging.error(f"No se pudo iniciar el servidor en {HOST_IP}:{PORT}. Error: {e}")
        logging.error("Verifica IPs, puertos, permisos y configuración de red.")
        logging.error("Considera usar '0.0.0.0' como HOST_IP si tienes problemas.")
    except Exception as e:
        logging.error(f"Ocurrió un error al iniciar el servidor: {e}")

if __name__ == "__main__":
    try:
        # Si quieres ver el JSON enviado en el log, cambia el nivel a DEBUG
        # logging.basicConfig(level=logging.DEBUG)
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Servidor detenido manualmente (Ctrl+C).")