import cv2
from cv2 import CAP_DSHOW
import asyncio
import websockets
import base64
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def stream_camera(websocket, path):
    cap1 = cv2.VideoCapture(0, CAP_DSHOW)
    cap2 = cv2.VideoCapture(1, CAP_DSHOW)

    for cap in [cap1, cap2]:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not (cap1.isOpened() and cap2.isOpened()):
        logging.error("Failed to open one or both cameras")
        return

    try:
        frame_count = 0
        while True:
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()

            if not ret1 or not ret2:
                logging.warning("Failed to capture image, retrying...")
                await asyncio.sleep(0.1)
                continue

            _, buffer1 = cv2.imencode('.jpg', frame1, [cv2.IMWRITE_JPEG_QUALITY, 80])
            _, buffer2 = cv2.imencode('.jpg', frame2, [cv2.IMWRITE_JPEG_QUALITY, 80])

            jpg_as_text1 = base64.b64encode(buffer1).decode('utf-8')
            jpg_as_text2 = base64.b64encode(buffer2).decode('utf-8')

            data_to_send = jpg_as_text1 + "|" + jpg_as_text2
            
            await websocket.send(data_to_send)
            frame_count += 1
            if frame_count % 100 == 0:
                logging.info(f"Sent {frame_count} frames")
            
            await asyncio.sleep(0.033)  # ~30 fps

    except websockets.exceptions.ConnectionClosed:
        logging.info("Client disconnected")
    except Exception as e:
        logging.error(f"Error in stream_camera: {e}")
    finally:
        logging.info("Closing cameras")
        cap1.release()
        cap2.release()

async def main():
    server = await websockets.serve(stream_camera, "0.0.0.0", 8765)
    logging.info("Server started on 0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
