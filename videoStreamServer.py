import socket
import cv2
import camera
import io
import pickle
import zstandard

s = socket.socket()
s.bind(('', 444))

s.listen(10)

while True:
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    break

cam = camera.Camera()

while True:
    b = io.BytesIO()
    img=cam.image
    b.write(pickle.dumps(zstandard.ZstdCompressor().compress(img)))
    conn.send(b.getvalue())

s.close()
