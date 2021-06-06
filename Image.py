import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import matplotlib.pyplot as plt
import numpy as np
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s - %(message)s')

file_handler = logging.FileHandler('log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class Image:
    def __init__(self):
        self.path = qtw.QFileDialog.getOpenFileName(None, 'Load Image', './', "Image File(*.png *.jpg *.jpeg)")[0]
        if self.path:
            self.raw_data = plt.imread(self.path)
            self.format = self.path.split('.')[-1]
            if (self.format in ['jpg', 'jpeg']):
                self.raw_data = self.raw_data.astype('float32')
                self.raw_data /= 255
            self.shape = self.raw_data.shape
            self.WIDTH = self.shape[0]
            self.HEIGHT = self.shape[1]
            self.fft = np.fft.fft2(self.raw_data)
            self.magnitude = np.abs(self.fft)
            self.phase = np.angle(self.fft)
            self.real = np.real(self.fft)
            self.imaginary = np.imag(self.fft)
            self.pixmap = qtg.QPixmap(self.path)
            self.components = {
                '':'',
                'Magnitude':self.magnitude,
                'Phase':self.phase,
                'Real':self.real,
                'Imaginary': self.imaginary,
            }

    def get_pixmap(self):
        return self.pixmap

    def compare(self, image2: 'Image') -> bool:
        return self.WIDTH == image2.WIDTH and self.HEIGHT == image2.HEIGHT

    def mix(self, image_2: 'Image', type_1: str, type_2: str, component_1_ratio: float, component_2_ratio: float, mode: str) -> qtg.QPixmap:
        first = self.get_component(type_1, component_1_ratio)
        second = image_2.get_component(type_2, component_2_ratio)

        if mode == 'mag-phase':
            construct = np.real(np.fft.ifft2(np.multiply(first, second)))
        if mode == 'real-imag':
            construct = np.real(np.fft.ifft2(first + second))

        if np.max(construct) > 1.0:
            construct /= np.max(construct)
        plt.imsave('test.png', np.abs(construct))
        return qtg.QPixmap('test.png')

    def get_component(self, type: str, ratio: float) -> np.ndarray:
        if type == "Magnitude":
            return self.components[type] * ratio
        elif type == "Phase":
            return np.exp(1j * self.components[type] * ratio)
        elif type == "Real":
            return self.components[type] * ratio
        elif type == "Imaginary":
            return 1j* self.components[type] * ratio
        elif type =="Uniform Magnitude" :
            return np.ones(shape=self.shape) * ratio
        elif type == "Uniform Phase":
            return np.exp(1j * np.zeros(shape=self.shape) * ratio)

    def get_component_pixmap(self, component: str) -> qtg.QPixmap:
        # component_val = np.dot(self.components[component][...,:3], [0.2989, 0.5870, 0.1140])
        if component != '':
            component_val = np.dot(self.components[component][...,:3], [0.2125, 0.7154, 0.0721])

        if component in ['Magnitude', 'Real']:
            plt.imsave('test.png',np.log(np.abs((component_val))), cmap='gray')
        elif component == 'Phase' :
            plt.imsave('test.png',(np.abs((component_val))), cmap='gray')
        elif component=='Imaginary':
            component_tmp  = np.where(component_val > 1.0e-10, component_val, 1.0e-10)
            result = np.where(component_val > 1.0e-10, np.log10(component_tmp), -10)
            plt.imsave('test.png',(np.abs(result)), cmap='gray')
        else :
            return qtg.QPixmap("./assets/placeholder.png")
        return qtg.QPixmap('test.png')