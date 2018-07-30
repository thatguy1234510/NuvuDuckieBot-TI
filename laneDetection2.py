import cv2
from rpistream.camera import Camera
import numpy as np
import time
import colorsys
def normLayer(l):
    return (l-np.min(l))/(np.max(l)-np.min(l))
class ColorProfile:
    lanes = {
        "yellow":(213,177,91),
        "white":(255,255,255),
        "grey":(150,150,150)
    }
class LaneDetector:
    def __init__(self, **kwargs):
        self.KmeansProfile = None
        self.calibrated = False

    def calibrate(self, img, profile, **kwargs):
        K = kwargs.get("K",3)
        debug=kwargs.get("debug",False)
        blurSize = kwargs.get("blurSize",(5,5))
        w = img.shape[1]
        h = img.shape[0]
        img=cv2.GaussianBlur(img,blurSize,0)
        Z = img.reshape((-1,3))

        # convert to np.float32
        Z = np.float32(Z)
        KmeansProfile = {}
        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
        
        chsv = np.array([colorsys.rgb_to_hsv(*(c/255)) for c in center])

        for name in ColorProfile.lanes:
            color = np.array(colorsys.rgb_to_hsv(*np.array(ColorProfile.lanes[name])/255))
            losses = np.abs(chsv-color).mean(axis=1)
            n = np.argmin(losses)
            KmeansProfile[name] = center[n]

        center = np.uint8(center)
        res = center[label.flatten()]
        res2 = res.reshape((img.shape))
        self.KmeansProfile = KmeansProfile
        self.calibrated = True
        if debug:
            return res2

    def process(self,img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        l = []
        for name in profile:
            color = np.array(colorsys.rgb_to_hsv(*np.array(profile[name])))
            losses = np.abs(hsv-color).mean(axis=2)
            l.append(losses.reshape(img.shape[0],img.shape[1],1))
        

        print(np.mean(l[0]-l[1]))
        l = np.concatenate((l[0],l[1],l[2]),axis=2)
        print(l[0,1])
        #return normLayer(l)
        l = np.argmin(l,2)
        return (l==0).astype("float")

    def getCalibImage(self,cam,iters=10):
        img = None
        for i in range(iters):
            img = cam.image
        return img

if __name__ == "__main__":
    cam = Camera(mirror=True)
    LD=LaneDetector()
    profile=ColorProfile.lanes
    calibImg = LD.getCalibImage(cam)
    res=LD.calibrate(calibImg, profile, debug=True)
    print(LD.KmeansProfile)
    while 1:
        cv2.imshow('my webcam', LD.process(cam.image))
        if cv2.waitKey(1) == 27:
            break  # esc to quit