import numpy as np
import cv2

from repositories import ann_loader

class digitPictureService:
    def __init__(self):
        self.model = ann_loader.get_digit_classify_model()

    def preproc_img(self, img):
        img = self.model.in_norm(img)
        return img
    
    def infer(self, img):
        x = self.preproc_img(img)
        output = self.model.forward(x)
        pred = self.model.get_pred(output)
        return pred
    
def classify_digit_in_image(file):
    """file: byte data"""
    img_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img_array = cv2.imdecode(img_bytes, cv2.IMREAD_GRAYSCALE) # model only receive 1 color channel
    srv = digitPictureService()
    return srv.infer(img_array)