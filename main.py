import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from Image import Image
from main_layout import Ui_MainWindow
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s - %(message)s')

file_handler = logging.FileHandler('log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.images = {
            '1': {
                'original': self.ui.image_1_original,
                'filtered': self.ui.image_1_after_filter,
                'picker': self.ui.image_1_pick
            },
            '2': {
                'original': self.ui.image_2_original,
                'filtered': self.ui.image_2_after_filter,
                'picker': self.ui.image_2_pick
            }
        }

        self.img = {}

        self.modes = {'Output 1': '', 'Output 2': ''}

        self.output_channels = {
            'Output 1': self.ui.output_1,
            'Output 2': self.ui.output_2
        }

        self.output_channels_controlers = {
            '': {
                'select1': '',
                'select2': '',
                'slider1': 0,
                'slider2': 0,
                'type1': '',
                'type2': '',
                'percentage1': 0,
                'percentage2': 0,
            },
            'Output 1': {
                'select1': '',
                'select2': '',
                'slider1': 0,
                'slider2': 0,
                'type1': '',
                'type2': '',
                'percentage1': 0,
                'percentage2': 0,
            },
            'Output 2': {
                'select1': '',
                'select2': '',
                'slider1': 0,
                'slider2': 0,
                'type1': '',
                'type2': '',
                'percentage1': 0,
                'percentage2': 0,
            },
        }

        self.output_complementary = {
            '': ['', 'Magnitude', 'Phase', 'Real', 'Imaginary', 'Uniform Magnitude', 'Uniform Phase'],
            'Magnitude': ['Phase', 'Uniform Phase'],
            'Phase': ['Magnitude', 'Uniform Magnitude'],
            'Real': ['Imaginary'],
            'Imaginary': ['Real'],
            'Uniform Magnitude': ['Phase', 'Uniform Phase'],
            'Uniform Phase': ['Magnitude', 'Uniform Magnitude'],
        }

        self.available_images = {
            '': ''
        }

        self.enables = {
            '': [self.ui.component_1_select, self.ui.component_2_select, self.ui.component_1_percentage, 
                    self.ui.component_1_slider, self.ui.component_1_type, 
                    self.ui.component_2_percentage, self.ui.component_2_slider, self.ui.component_2_type],
            'output-select': [self.ui.component_1_select, self.ui.component_2_select],
            'select1': [self.ui.component_1_percentage, self.ui.component_1_type],
            'select2': [self.ui.component_2_percentage, self.ui.component_2_type],
            'type1': [self.ui.component_1_slider],
            'type2': [self.ui.component_2_slider]
        }

        self.current_output_channel = None

        self.ui.action_new.triggered.connect(self.new_instance)
        self.ui.action_exit.triggered.connect(self.close)

        self.ui.action_open_image_1.triggered.connect(lambda: self.open_image(self.images['1'], 1))
        self.ui.action_open_image_2.triggered.connect(lambda: self.open_image(self.images['2'], 2))

        self.ui.image_1_pick.currentIndexChanged.connect(lambda: self.display_component(self.img['Image 1']))
        self.ui.image_2_pick.currentIndexChanged.connect(lambda: self.display_component(self.img['Image 2']))

        self.ui.output_select.currentIndexChanged.connect(lambda: self.pick_mixer_output())

        self.ui.component_1_select.currentIndexChanged.connect(lambda: self.select_enable('select1', self.ui.component_1_select.currentText()))
        self.ui.component_2_select.currentIndexChanged.connect(lambda: self.select_enable('select2', self.ui.component_2_select.currentText()))
        self.ui.component_1_slider.sliderReleased.connect(lambda: self.mixer('slider1', str(self.ui.component_1_slider.value())))
        self.ui.component_2_slider.sliderReleased.connect(lambda: self.mixer('slider2', str(self.ui.component_2_slider.value())))
        self.ui.component_1_percentage.valueChanged.connect(lambda: self.change_image('percentage1', str(self.ui.component_1_percentage.value())))
        self.ui.component_2_percentage.valueChanged.connect(lambda: self.change_image('percentage2', str(self.ui.component_2_percentage.value())))
        self.ui.component_1_type.currentIndexChanged.connect(lambda: self.component_1_conplementary())
        self.ui.component_1_type.currentIndexChanged.connect(lambda: self.select_enable('type1', str(self.ui.component_1_type.currentText())))
        self.ui.component_2_type.currentIndexChanged.connect(lambda: self.select_enable('type2', str(self.ui.component_2_type.currentText())))
        
    def new_instance(self) -> None:
        self.child_window = MainWindow()
        self.child_window.show()

    def open_image(self, imageWidget: dict, channel: int) -> None:
        image = Image()
        if not image.path:
            return
        if len(self.img) == 1:
            if f'Image {2//channel}' in self.img:
                if not image.compare(self.img[f'Image {2//channel}']['image']):
                    qtw.QMessageBox.warning(self, 'failed', 'The Two Images Must be of the same size')
                    return
                else :
                    self.img[f'Image {channel}'] = {'image': image, 'widgets': imageWidget}
                    if f'Image {channel}' not in self.available_images:
                        self.available_images[f'Image {channel}'] = f'Image {channel}'
                        self.append_outputs(isOneChanneled=False)
            else :
                self.img[f'Image {channel}'] = {'image': image, 'widgets': imageWidget}
        elif len(self.img) >= 2:
            if not image.compare(self.img[f'Image {2//channel}']['image']):
                qtw.QMessageBox.warning(self, 'failed', 'The Two Images Must be of the same size')
                return
            self.img[f'Image {channel}']["image"] = image
            self.img[f'Image {channel}']["widgets"] = imageWidget
        else :
            self.img[f'Image {channel}'] = {'image': image, 'widgets': imageWidget}
            if f'Image {channel}' not in self.available_images:
                self.available_images[f'Image {channel}'] = f'Image {channel}'
                self.append_outputs(channel=self.available_images[f'Image {channel}'])
        imageWidget['original'].setPixmap(image.get_pixmap().scaled(300,300, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))
        imageWidget['picker'].setDisabled(False)
        self.ui.output_select.setDisabled(False)

    def append_outputs(self, isOneChanneled: bool=True, channel: str='') -> None:
        if isOneChanneled:
            self.ui.component_1_select.addItem('')
            self.ui.component_2_select.addItem('')
            self.ui.component_1_select.setItemText(0, '')
            self.ui.component_1_select.setItemText(1, channel)
            self.ui.component_2_select.setItemText(0, '')
            self.ui.component_2_select.setItemText(1, channel)
        else:
            self.ui.component_1_select.addItem('')
            self.ui.component_2_select.addItem('')
            self.ui.component_1_select.setItemText(0, '')
            self.ui.component_1_select.setItemText(1, 'Image 1')
            self.ui.component_1_select.setItemText(2, 'Image 2')
            self.ui.component_2_select.setItemText(0, '')
            self.ui.component_2_select.setItemText(1, 'Image 1')
            self.ui.component_2_select.setItemText(2, 'Image 2')

    def display_component(self, imageWidget: dict) -> None:
        component = imageWidget['widgets']['picker'].currentText()
        imageWidget['widgets']['filtered'].setPixmap(imageWidget['image'].get_component_pixmap(component).scaled(300,300, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))
        try:
            os.remove('test.png')
        except:
            pass

    def pick_mixer_output(self) -> None:
        self.current_output_channel = self.ui.output_select.currentText()
        self.ui.component_1_slider.setValue(int(self.output_channels_controlers[self.ui.output_select.currentText()]['slider1']))
        self.ui.component_1_percentage.setValue(int(self.output_channels_controlers[self.ui.output_select.currentText()]['percentage1']))
        self.ui.component_1_select.setCurrentText(self.output_channels_controlers[self.ui.output_select.currentText()]['select1'])
        self.ui.component_1_type.setCurrentText(self.output_channels_controlers[self.ui.output_select.currentText()]['type1'])
        
        self.ui.component_2_slider.setValue(int(self.output_channels_controlers[self.ui.output_select.currentText()]['slider2']))
        self.ui.component_2_percentage.setValue(int(self.output_channels_controlers[self.ui.output_select.currentText()]['percentage2']))
        self.ui.component_2_select.setCurrentText(self.output_channels_controlers[self.ui.output_select.currentText()]['select2'])
        self.ui.component_2_type.setCurrentText(self.output_channels_controlers[self.ui.output_select.currentText()]['type2'])
        if self.ui.output_select.currentText() != '':
            self.set_mixer_components_disabled(self.enables['output-select'] ,False)
        else:
            self.set_mixer_components_disabled(self.enables['output-select'], True)

    def set_mixer_components_disabled(self, components: list, logic: bool) -> None:
        for component in components:
            component.setDisabled(logic)

    def select_enable(self, component: str, value: str):
        self.change_image(component, value)
        if value != '':
            self.set_mixer_components_disabled(self.enables[component], False)
        else:    
            self.set_mixer_components_disabled(self.enables[component], True)

    def change_image(self, component: str, value: str) -> None:
        self.output_channels_controlers[self.current_output_channel][component] = value

    def component_1_conplementary(self):
        self.ui.component_2_type.clear()
        self.ui.component_2_type.addItems(self.output_complementary[self.ui.component_1_type.currentText()])
        self.ui.component_2_type.update()

        self.change_image('type1', self.ui.component_1_type.currentText())

    def mixer(self, slider: str, sliderValue: str) -> None:
        self.change_image(slider, sliderValue)
        
        channel_1_ratio = float(self.output_channels_controlers[self.current_output_channel]['slider1']) / 100
        channel_2_ratio = float(self.output_channels_controlers[self.current_output_channel]['slider2']) / 100

        image_1 = self.output_channels_controlers[self.current_output_channel]['select1']
        image_2 = self.output_channels_controlers[self.current_output_channel]['select2']

        type1 = self.output_channels_controlers[self.current_output_channel]['type1'] 
        type2 = self.output_channels_controlers[self.current_output_channel]['type2'] 
 
        if image_1 == "" or image_2 == "" or type1 == "" or type2 == "":
            return

        try:
            if (type1 in ['Magnitude', 'Phase', 'Uniform Magnitude', 'Uniform Phase']
                and type2 in ['Magnitude', 'Phase', 'Uniform Magnitude', 'Uniform Phase']):
                self.modes[self.current_output_channel] = 'mag-phase'
            elif (type1 in ['Real', 'Imaginary']and type2 in ['Real', 'Imaginary']):
                self.modes[self.current_output_channel] = 'real-imag'
            else:
                print('Error')
                return
            self.outImage = self.img[image_1]['image'].mix(self.img[image_2]['image'], self.output_channels_controlers[self.current_output_channel]['type1'], self.output_channels_controlers[self.current_output_channel]['type2'], channel_1_ratio, channel_2_ratio, self.modes[self.current_output_channel])

            self.output_channels[self.current_output_channel].setPixmap(self.outImage.scaled(300,300, aspectRatioMode=qtc.Qt.KeepAspectRatio, transformMode=qtc.Qt.SmoothTransformation))
        except:
            pass

        try:
            os.remove('test.png')
        except:
            pass


def main_window():
    app = qtw.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main_window()