import cv2
from camera import Camera
import numpy as np
import time


def grayscale(img): return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def autoCanny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged


def unzero(x):
    if x == 0:
        x = 0.001
    return x


def getLineColor(img, m, b, step=2):
    bottom = min(max((-b)/m, 0), img.shape[1]-1)

    top = max(min((img.shape[0]-b)/m, img.shape[1]-1), 0)

    if top < bottom:
        bottom, top = top, bottom
    total = np.array([0, 0, 0])
    size = 0

    for x in range(int(bottom), int(top), step):
        y = min(max(int(m*x+b), 0), img.shape[0]-1)
        color = img[y, x]
        total += color
        size += 1
    if size == 0:
        return None
    avg = total/size

    return avg

def UnPerp(img):
    pass
    M=cv2.getPerspectiveTransform()
    return cv2.warpPerspective(img,M)
    
def process(color):
    color = color[color.shape[0]//2:, :]
    img = grayscale(color)
    kernel = np.ones((5, 5), np.float32)/25
    img = cv2.filter2D(img, -1, kernel)
    edges = autoCanny(img)
    output = color #np.zeros(color.shape)  # edges.reshape([edges.shape[0],edges.shape[1],1])

    lines = cv2.HoughLines(edges, 1, np.pi/180, 80)
    if lines is None:
        return output
    for line in lines[:10]:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            m = unzero((y2-y1)/(unzero(x2-x1)))
            b = y1-m*x1
            lineColor = getLineColor(color, m, b)
            if lineColor is None:
                continue
            
            cv2.line(output, (0, int(b)),
                     (1000, int(m*1000+b)), tuple(lineColor), 2)
            #print(lineColor)
            cv2.circle(output, (int(x0), int(y0)), 4, (255, 0, 0), -1)
    return output


if __name__ == "__main__":
    cam = Camera(mirror=True)
    while 1:
        cv2.imshow('my webcam', process(cam.image))
        if cv2.waitKey(1) == 27:
            break  # esc to quit
