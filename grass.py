import asyncio
import random
import ssl
import json
import time
import uuid
import websockets
from loguru import logger
from fake_useragent import UserAgent

# Konfigurasi User-Agent acak
user_agent = UserAgent(os='windows', platforms='pc', browsers='chrome')
random_user_agent = user_agent.random

# User ID default
DEFAULT_USER_ID = "2oSjgJ8VS3Rg9j46tDpo0v17ttM"

async def connect_to_wss(user_id):
    device_id = str(uuid.uuid4())  # Membuat UUID unik untuk browser_id
    logger.info(f"Device ID: {device_id}")
    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)  # Random delay antara 0.1 - 1.0 detik
            custom_headers = {
                "User-Agent": random_user_agent,
                "Origin": "chrome-extension://lkbnfiajjmbhnfledhphioinpickokdi"
            }

            # Nonaktifkan verifikasi SSL
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # Pilih URI WebSocket secara acak
            urilist = ["wss://proxy2.wynd.network:4444/", "wss://proxy2.wynd.network:4650/"]
            uri = random.choice(urilist)
            server_hostname = "proxy2.wynd.network"

            # Membuka koneksi WebSocket
            async with websockets.connect(uri, ssl=ssl_context, extra_headers=custom_headers,
                                          server_hostname=server_hostname) as websocket:
                async def send_ping():
                    while True:
                        send_message = json.dumps(
                            {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}})
                        logger.debug(f"Send: {send_message}")
                        await websocket.send(send_message)
                        await asyncio.sleep(5)  # Kirim PING setiap 5 detik

                await asyncio.sleep(1)
                asyncio.create_task(send_ping())  # Mulai tugas PING

                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.info(f"Received: {message}")

                    # Tangani pesan AUTH
                    if message.get("action") == "AUTH":
                        auth_response = {
                            "id": message["id"],
                            "origin_action": "AUTH",
                            "result": {
                                "browser_id": device_id,
                                "user_id": user_id,
                                "user_agent": custom_headers['User-Agent'],
                                "timestamp": int(time.time()),
                                "device_type": "extension",
                                "version": "4.26.2",
                                "extension_id": "lkbnfiajjmbhnfledhphioinpickokdi"
                            }
                        }
                        logger.debug(f"Send AUTH Response: {auth_response}")
                        await websocket.send(json.dumps(auth_response))

                    # Tangani pesan PONG
                    elif message.get("action") == "PONG":
                        pong_response = {"id": message["id"], "origin_action": "PONG"}
                        logger.debug(f"Send PONG Response: {pong_response}")
                        await websocket.send(json.dumps(pong_response))
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)  # Tunggu 5 detik sebelum mencoba kembali

async def main():
    # Menggunakan user_id default
    logger.info(f"Using default user ID: {DEFAULT_USER_ID}")
    await connect_to_wss(DEFAULT_USER_ID)

if __name__ == '__main__':
    asyncio.run(main())
