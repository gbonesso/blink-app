from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

Builder.load_string('''
<CameraDisplayWidget>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (1920, 1080)
        play: True
        index: 0  # USB Spedal?
''')


class CameraDisplayWidget(BoxLayout):
    pass
