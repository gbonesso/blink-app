import logging
import datetime
import json
from enum import Enum
import numpy as np
import cv2
import os.path
from datetime import datetime

# Kivy imports...
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.graphics.texture import Texture
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.screen import MDScreen
from kivymd.uix.fitimage import FitImage
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar.toolbar import MDTopAppBar
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy import platform
from kivy.metrics import dp
from kivy.graphics import Rectangle, Line, Color, Ellipse, InstructionGroup

# blink imports
import camera_desktop
from tela_inicial import TelaInicial
from historico_analises_list import HistoricoAnalises
from dados_analise_pos_manual import TelaDadosAnalise
from tela_login import TelaLogin
from tela_cadastro import TelaCadastro
from tela_configuracao import TelaConfiguracao
from dados.modelo import DadoFrame, DadosAnalise
from sobre import Sobre
from cadastro_utils import get_storage_path
from utils import rotate

# from blink import blink_utils as blink

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

if platform == "macosx" or platform == "android":
    try:
        # Import TFLite interpreter from tflite_runtime package if it's available.
        from tflite_runtime.interpreter import Interpreter
        from tflite_runtime.interpreter import load_delegate
    except ImportError:
        # If not, fallback to use the TFLite interpreter from the full TF package.
        import tensorflow as tf
        Interpreter = tf.lite.Interpreter
        load_delegate = tf.lite.experimental.load_delegate

# Define se usaremos dados reais (dos arquivos json criados nas análises) ou dados "fake" para testes
REAL_DATA = True
if REAL_DATA:
    from dados.repositorio_dados_reais import RepositorioDadosAnalise
else:
    from dados.repositorio_dados_fake import RepositorioDadosAnalise

if platform == "android":
    from android.permissions import request_permission, check_permission, Permission
    from camera2.camerawidget import CameraDisplayWidget

cascPath = "assets/haarcascade_frontalface_default.xml"
eyePath = "assets/haarcascade_eye.xml"
# eyePath = "assets/haarcascade_eye_tree_eyeglasses.xml"

faceCascade = cv2.CascadeClassifier(cascPath)
eyeCascade = cv2.CascadeClassifier(eyePath)

KV = """ 
<ContentNavigationDrawer>:
    orientation: "vertical"
    padding: "8dp"
    spacing: "8dp"

    Image:
        #id: avatar
        size_hint: None, None
        size: "56dp", "56dp"
        source: "assets/Blink_Logo_Nome_Fundo_Branco.png"

    MDLabel:
        text: "gustavo_bonesso@hotmail.com"
        font_style: "Caption"
        size_hint_y: None
        height: self.texture_size[1]
        color:33/255, 90/255, 54/255, 1

    MDNavigationDrawerDivider:
        color:33/255, 90/255, 54/255, 1

    OneLineListItem:
        text: "Tela Inicial"
        #IconLeftWidget:
        #    icon: "home"
        on_press:
            root.main_app.go_to_screen("screen_00")
        
    OneLineListItem:
        id: novaanalise
        text: "Nova análise..."
        disabled: True
        on_press:
            root.main_app.go_to_screen("screen_01")

    OneLineListItem:
        id: historicoanalises
        text: "Histórico de análises"
        disabled: True
        on_press:
            root.main_app.go_to_screen("screen_02")
            
    OneLineListItem:
        id: configuracoes
        text: "Configurações"
        disabled: True
        on_press:
            root.main_app.go_to_screen("screen_07")

    OneLineListItem:
        id: "sobre"
        text: "Sobre"
        on_press:
            root.main_app.go_to_screen("screen_03")
"""


class ContentNavigationDrawer(BoxLayout):
    main_app = ObjectProperty()

"""
class RootLayout(FloatLayout):
    buttons_visible = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
"""


class BlinkApp(MDApp):
    camera_display_widget = ObjectProperty()
    navigation_drawer = ObjectProperty()
    screen_manager = ObjectProperty()
    screen_02 = ObjectProperty()
    root = ObjectProperty()

    menu = ObjectProperty()
    content_navigation_drawer = ObjectProperty()
    flip_camera_button = ObjectProperty()
    start_analysis_button = ObjectProperty()

    # Coordenadas da face e dos olhos
    face_rect = ObjectProperty()
    left_eye_rect = ObjectProperty()
    right_eye_rect = ObjectProperty()

    # Controle de status
    analise_iniciada = False

    # TensorflowLite Interpreter
    interpreter = ObjectProperty()
    model = ObjectProperty()

    # Repositório de dados de análise
    repositorio_dados = ObjectProperty()
    dados_analise_selecionado = ObjectProperty()
    ultima_analise = ObjectProperty()

    Eyes = Enum('Eyes', ['LEFT', 'RIGHT', 'UNDEFINED'])

    # Propriedades relacionadas a análise / detecção de face e olhos
    DEBUG_EYES = True
    min_size_face = NumericProperty()
    min_neighbors_face = NumericProperty()
    min_size_eyes = NumericProperty()
    min_neighbors_eyes = NumericProperty()
    left_eye_image_card = ObjectProperty()
    left_eye_image_dbg = ObjectProperty()
    left_eye_label_dbg = ObjectProperty()
    right_eye_image_card = ObjectProperty()
    right_eye_image_dbg = ObjectProperty()
    right_eye_label_dbg = ObjectProperty()
    instruction_group = ObjectProperty()
    canvas_widget = ObjectProperty()

    # Configuração inicial do arquivo "config.ini"
    def build_config(self, config):
        logger.info("build_config...")
        config.setdefaults(
            'cascade-desktop', {
                'minSize-face': '450',
                'minNeighbors-face': '5',
                'minSize-eyes': '80',
                'minNeighbors-eyes': '5'
            }
        )
        config.setdefaults(
            'cascade-mobile', {
                'minSize-face': '200',
                'minNeighbors-face': '5',
                'minSize-eyes': '70',
                'minNeighbors-eyes': '5'
            }
        )
        config.setdefaults(
            'debug', {
                'debug-eyes': False
            }
        )

    # Método invocado quando uma configuração é modificada via callback...
    def configuracao_modificada(self, section, key, value):
        logger.info("Configuração modificada - section: {}, key: {}, value: {}".format(section, key, value))
        self.DEBUG_EYES = self.config.getboolean('debug', 'debug-eyes')
        if self.DEBUG_EYES:
            if self.root is not None:  # build() já aconteceu...
                if self.left_eye_image_card is None:  # Os cards dos olhos de debug não foram construídos
                    self.build_debug_eyes()
        if platform == "macosx" or platform == "windows":
            self.min_size_face = self.config.getint('cascade-desktop', 'minsize-face')
            self.min_neighbors_face = self.config.getint('cascade-desktop', 'minneighbors-face')
            self.min_size_eyes = self.config.getint('cascade-desktop', 'minsize-eyes')
            self.min_neighbors_eyes = self.config.getint('cascade-desktop', 'minneighbors-eyes')
        elif platform == "android":
            self.min_size_face = self.config.getint('cascade-mobile', 'minsize-face')
            self.min_neighbors_face = self.config.getint('cascade-mobile', 'minneighbors-face')
            self.min_size_eyes = self.config.getint('cascade-mobile', 'minsize-eyes')
            self.min_neighbors_eyes = self.config.getint('cascade-mobile', 'minneighbors-eyes')

    def go_to_screen(self, screen_to_go):
        self.navigation_drawer.set_state("close")
        self.screen_manager.current = screen_to_go
        if screen_to_go == "screen_01":
            self.flip_camera_button.opacity = 1
            self.start_analysis_button.opacity = 1
            if self.DEBUG_EYES:
                self.left_eye_image_card.opacity = 1
                self.right_eye_image_card.opacity = 1
                self.canvas_widget.opacity = 1
        else:
            self.flip_camera_button.opacity = 0
            self.start_analysis_button.opacity = 0
            if self.DEBUG_EYES:
                self.left_eye_image_card.opacity = 0
                self.right_eye_image_card.opacity = 0
                self.canvas_widget.opacity = 0

    def habilita_menu(self):
        self.content_navigation_drawer.ids.novaanalise.disabled = False
        self.content_navigation_drawer.ids.historicoanalises.disabled = False
        self.content_navigation_drawer.ids.configuracoes.disabled = False

    def build_debug_eyes(self):
        self.right_eye_image_card = MDCard(
            pos_hint={"top": 0.9},
            size_hint=(.45, .15),
            opacity=0,
        )
        self.right_eye_image_dbg = FitImage()
        with self.right_eye_image_dbg.canvas:
            Color(1, 1, 1)
        self.right_eye_label_dbg = MDLabel(
            text="?",
            pos_hint={"top": 1}
        )
        self.right_eye_image_card.add_widget(self.right_eye_label_dbg)
        self.right_eye_image_card.add_widget(self.right_eye_image_dbg)
        self.root.add_widget(self.right_eye_image_card)

        # Olho esquerdo...
        self.left_eye_image_card = MDCard(
            pos_hint={"top": 0.9, "right": 1.0},
            size_hint=(.45, .15),
            opacity=0,
        )
        self.left_eye_image_dbg = FitImage()
        with self.left_eye_image_dbg.canvas:
            Color(1, 1, 1)
        self.left_eye_label_dbg = MDLabel(
            text="?",
            pos_hint={"top": 1}
        )
        self.left_eye_image_card.add_widget(self.left_eye_label_dbg)
        self.left_eye_image_card.add_widget(self.left_eye_image_dbg)
        self.root.add_widget(self.left_eye_image_card)

        # Widget para sobrepor a imagem e desenhar os retangulos de detecção no cado do Android
        self.canvas_widget = Widget(
            pos_hint={"top": 1},
            size_hint=(1, 1),
            opacity=0,
        )
        """
        with self.canvas_widget.canvas:
            Color(1, 0, 0),
            Line(
                rectangle=(50, 50, 180, 250),
                width=2,
            ),
        """
        self.root.add_widget(self.canvas_widget)

    def build(self):
        """menu_items = [  # variável usada para configura os itens do menu
            {
                "viewclass": "OneLineListItem",  # usado para mostrar o menu como lista
                "text": f"Opção {i}",
                "height": dp(56),
            } for i in range(5)
        ]
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)
        """
        self.config.add_callback(self.configuracao_modificada)
        self.configuracao_modificada(None, None, None)  # Força a atualização das configurações

        # ToDo: Pensar nas cargas que podem ser feitas offline, para não travar a thread principal...
        if platform == "macosx" or platform == "android":
            self.interpreter = Interpreter(model_path="assets/talking_300W_50_epoch.tflite")
            self.interpreter.allocate_tensors()
            input = self.interpreter.get_input_details()[0]
            logger.info("input_tensor.shape: {}".format(input['shape']))
            logger.info("input_tensor.quantization_parameters: {}".format(input['quantization_parameters']))
            logger.info("input_tensor.quantization_parameters.scales: {}".
                        format(input['quantization_parameters']['scales']))
            # logger.info("input_tensor.quantization_parameters: {}".format(input['quantization_parameters']))

        self.repositorio_dados = RepositorioDadosAnalise()

        if platform == "android":
            if not check_permission(Permission.CAMERA):
                request_permission(Permission.CAMERA)

        self.root = MDScreen(name="root")

        app_bar = MDTopAppBar(
            title='Blink',
            pos_hint={'top': 1},
            left_action_items=[['menu', lambda x: self.navigation_drawer.set_state('open')]],
        )

        Builder.load_string(KV)
        self.content_navigation_drawer = ContentNavigationDrawer()
        self.content_navigation_drawer.main_app = self
        self.navigation_drawer = MDNavigationDrawer(
            self.content_navigation_drawer,
            id="nav_drawer",
            radius=(0, 16, 16, 0),
        )

        logger.info("platform: {}".format(platform))
        if platform == "android":
            self.camera_display_widget = CameraDisplayWidget(
                size_hint_y=None,
                height=Window.height - app_bar.height - dp(40),
                width=Window.width,
                y=dp(20)
            )
        elif platform == "macosx":
            self.camera_display_widget = camera_desktop.CameraDisplayWidget(
                size_hint_y=None,
                height=Window.height - app_bar.height - dp(40),
                width=Window.width,
                y=dp(20)
            )

        logger.info('*** cdw size: {}'.format(self.camera_display_widget.size))

        navigation_layout = MDNavigationLayout()
        self.screen_manager = MDScreenManager()

        # Tela de nova análise
        screen_01 = MDScreen(name="screen_01")

        # screen_01.add_widget(app_bar)
        screen_01.add_widget(self.camera_display_widget)

        # Tela inicial
        screen_00 = TelaInicial(
            name="screen_00",
            md_bg_color=(33/255., 90/255., 54/255., 1),
        )
        screen_00.main_app = self
        self.screen_manager.add_widget(screen_00)

        # Tela de Histórico de Análises
        self.screen_02 = HistoricoAnalises(
            name="screen_02",
            main_app=self,
            # md_bg_color=(33 / 255., 90 / 255., 54 / 255., 1)
        )
        self.screen_manager.add_widget(self.screen_02)

        # Tela Sobre
        screen_03 = Sobre(
            name="screen_03",
            md_bg_color=(33 / 255., 90 / 255., 54 / 255., 1),
        )
        self.screen_manager.add_widget(screen_03)

        # Tela com os detalhes sobre uma análise
        screen_04 = TelaDadosAnalise(
            name="screen_04"
        )
        screen_04.main_app = self
        self.screen_manager.add_widget(screen_04)

        # Tela de Login
        screen_05 = TelaLogin(
            name="screen_05",
            md_bg_color=(33 / 255., 90 / 255., 54 / 255., 1),
        )
        screen_05.main_app = self
        self.screen_manager.add_widget(screen_05)

        # Tela de Cadastro
        screen_06 = TelaCadastro(
            name="screen_06",
            md_bg_color=(33 / 255., 90 / 255., 54 / 255., 1),
        )
        screen_06.main_app = self
        self.screen_manager.add_widget(screen_06)

        # Tela de Configuração
        screen_07 = TelaConfiguracao(
            name="screen_07",
            md_bg_color=(33 / 255., 90 / 255., 54 / 255., 1),
        )
        screen_07.main_app = self
        self.screen_manager.add_widget(screen_07)

        self.screen_manager.add_widget(screen_01)
        navigation_layout.add_widget(self.screen_manager)

        navigation_layout.add_widget(self.navigation_drawer)

        self.flip_camera_button = MDFloatingActionButton(
            icon='camera-flip-outline',
            pos_hint={'right': 0.9, 'top': 0.1},
            opacity=0,  # Escondido na primeira tela
        )
        self.flip_camera_button.bind(on_press=self.flip_camera_button_press)

        self.root.add_widget(navigation_layout)
        # O botão de flip da câmera está vinculado a tela raiz, para ficar sobre a imagem da câmera...
        self.root.add_widget(self.flip_camera_button)

        # Botão de início de análise
        self.start_analysis_button = MDFloatingActionButton(
            icon='play-circle-outline',
            pos_hint={'center_x': 0.5, 'top': 0.1},
            md_bg_color=[0, 1, 0, 1],  # Verde...
            opacity=0,  # Escondido na primeira tela
        )
        self.start_analysis_button.bind(on_press=self.start_analysis_button_press)
        self.root.add_widget(self.start_analysis_button)

        Clock.schedule_interval(self.update, 0)

        self.root.add_widget(app_bar)

        # Imagem do olho para debug...
        if self.DEBUG_EYES:
            self.build_debug_eyes()

        return self.root

    # on_start é executado após o build()
    # ToDo: Ainda tenho que descobrir como deixar a camera frontal como padrão no Android
    def on_start(self):
        if platform == "android":
            # self.camera_display_widget.restart_stream()
            Clock.schedule_once(self.flip_camera_button_press, 1)
            Clock.schedule_once(self.flip_camera_button_press, 3)
            Clock.schedule_once(self.flip_camera_button_press, 5)

            # self.camera_display_widget.rotate_cameras()
            # self.camera_display_widget.rotate_cameras()

    def flip_camera_button_press(self, button):
        self.camera_display_widget.rotate_cameras()

    def start_analysis_button_press(self, button):
        if not self.analise_iniciada:
            self.analise_iniciada = True
            self.start_analysis_button.icon = "stop-circle-outline"
            # self.start_analysis_button.md_bg_color = [1, 0, 0, 1],  # Vermelho...
            self.ultima_analise = DadosAnalise(
                data_hora_analise=datetime.now(),
                duracao_analise=-1,
                quantidade_de_piscadas=-1,
                piscadas_por_minuto=-1,
                dados_frames=[],
            )
        else:
            self.analise_iniciada = False
            self.start_analysis_button.icon = "play-circle-outline"
            nome_arquivo = "ANALISE_{}.json".format(self.ultima_analise.data_hora_analise.strftime("%Y%m%d%H%M%S"))
            # Checa se o diretório de dados existe e criar caso não exista...
            file_folder = os.path.join(get_storage_path(), "json_data")
            if not os.path.isdir(file_folder):
                os.mkdir(file_folder)
            file_path = os.path.join(get_storage_path(), "json_data", nome_arquivo)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.ultima_analise.toJSON(), file, ensure_ascii=False, indent=4)
                logger.info("JSON: {}".format(self.ultima_analise.toJSON()))
                file.close()
            # self.start_analysis_button.md_bg_color = [0, 1, 0, 1],  # Vermelho...
            # Força atualização da lista de análises
            self.repositorio_dados = RepositorioDadosAnalise()
            self.screen_02 = HistoricoAnalises(
                name="screen_02",
                main_app=self,
            )

    """
    def on_start(self):
        #self.root.ids.box.add_widget(self.camera_display_widget)
        Clock.schedule_interval(self.teste, 1)
    """

    def on_texture(self, instance, value):
        print("App texture changed to {}".format(value))

    def update(self, dt):
        # Se a tela atual não for a tela de análise não faz o update da tela...
        if self.screen_manager.current != "screen_01":
            return

        self.root.canvas.ask_update()

        img = self.camera_display_widget.export_as_image()
        # logger.info('*** img: {}'.format(img))
        logger.info("self.min_size_face: {}".format(self.min_size_face))

        if img is not None:
            # texture.pixels have the RGBA data
            # logger.info('*** img.texture.pixels: {}'.format(img.texture.pixels))
            pixel_array = np.frombuffer(img.texture.pixels, np.uint8)
            logger.info("pixel_array_shape: {}".format(pixel_array.shape))
            # logger.info('*** pixel_array - len: {} height: {}, width: {}'.
            #             format(len(pixel_array), img.height, img.width))
            pixel_array_rgba = pixel_array.reshape(img.height, img.width, 4)
            pixel_array = pixel_array_rgba[:, :, :3]  # Elimina o canal alpha
            logger.info("pixel_array_shape (after reshape): {}".format(pixel_array.shape))
            # logger.info('*** pixel_array: {}'.format(pixel_array))
            # Aumenta o contraste...
            # pixel_array = self.pre_process_image(pixel_array)
            gray = cv2.cvtColor(pixel_array, cv2.COLOR_BGR2GRAY)
            # logger.info('*** gray: {}'.format(gray))
            begin = datetime.now()
            min_size_face = self.min_size_face
            min_neighbors_face = self.min_neighbors_face
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=min_neighbors_face,
                minSize=(min_size_face, min_size_face),
                flags=cv2.CASCADE_SCALE_IMAGE,
            )
            logger.info('*** Tempo faceCascade: {} #faces:{} '.format(datetime.now() - begin, len(faces)))
            for (x, y, w, h) in faces:
                logger.info('*** x:{} y:{}, w:{}, h:{}'.format(x, y, w, h))
                y = y + int(h/8)
                self.face_rect = (x, y, w, int(h/2))  # h/3 -> Elimina a metade da boca...

                # Cria uma imagem recortada somente da face para acelerar o processo de detecção dos olhos
                face_img_rgba = pixel_array_rgba[
                    self.face_rect[1]:self.face_rect[1] + self.face_rect[3],
                    self.face_rect[0]:self.face_rect[0] + self.face_rect[2]
                ]
                face_img_rgb = face_img_rgba[:, :, :3]  # Elimina o canal alpha
                face_gray = cv2.cvtColor(face_img_rgb, cv2.COLOR_BGR2GRAY)

                # Tamanho mínimo de detecção. Nas cameras de desktops o tamanho dos olhos é menor
                # ToDo: Colocar scaleFactor nas configurações
                min_size_eyes = self.min_size_eyes
                min_neighbors_eyes = self.min_neighbors_eyes
                begin = datetime.now()
                eyes = eyeCascade.detectMultiScale(
                    # gray,
                    face_gray,
                    scaleFactor=1.02,  # Não precisa escalar muito, a distância da selfie não varia muito...
                    minNeighbors=min_neighbors_eyes,  # Valores maiores fazem menos detecções mais precisas
                    # 5 não estava detectando olho direito...
                    minSize=(min_size_eyes, min_size_eyes),
                    flags=cv2.CASCADE_SCALE_IMAGE,
                )

                # Registra frame
                if self.analise_iniciada:
                    if self.ultima_analise is not None:
                        dados_frame_atual = DadoFrame(
                            data_hora_frame=datetime.now(),
                            numero_frame=-1,
                            olho_direito_aberto=-1,
                            olho_esquerdo_aberto=-1,
                        )

                logger.info('*** Tempo eyeCascade: {} #eyes:{} '.format(datetime.now() - begin, len(eyes)))
                for (ex, ey, ew, eh) in eyes:
                    logger.info('*** eyes - ex:{} ey:{}, ew:{}, eh:{}'.format(ex, ey, ew, eh))
                    # which_eye = self.get_eye(x, y, w, h, ex, ey, ew, eh)
                    # Na imagem da face recortada a posição relativa da imagem é zero...
                    which_eye = self.get_eye(0, 0, w, h, ex, ey, ew, eh)
                    logger.info("which_eye: {}".format(which_eye))
                    # ey_ajustado = float(img.height / 2 - eh - ey)

                    if which_eye == self.Eyes.LEFT:
                        # self.left_eye_rect = (ex, ey, ew, eh)
                        self.left_eye_rect = (x + ex, y + ey, ew, eh)

                    elif which_eye == self.Eyes.RIGHT:
                        # self.right_eye_rect = (ex, ey, ew, eh)
                        self.right_eye_rect = (x + ex, y + ey, ew, eh)

                # Faces e olhos processados para esse frame, fazer a detecção de olhos abertos / fechados
                # via tensorflow
                # Para copiar uma área do frame: frame[y:y+h, x:x+w]
                # Processa olho direito.
                # ToDo: Generalizar essa parte do código, criando uma função
                if self.right_eye_rect is not None:
                    right_eye_img = pixel_array[
                        self.right_eye_rect[1]:self.right_eye_rect[1] + self.right_eye_rect[3],
                        self.right_eye_rect[0]:self.right_eye_rect[0] + self.right_eye_rect[2]
                    ]
                    image_color_resized = cv2.resize(right_eye_img, (32, 32))
                    logger.info("pixel_array.shape: {} image_color_resized.shape {} right_eye_img.shape {}".format(
                        pixel_array.shape, image_color_resized.shape, right_eye_img.shape))

                    # *** Cria imagem para debug...
                    if self.DEBUG_EYES:
                        right_eye_img_rgba = pixel_array_rgba[
                            self.right_eye_rect[1]:self.right_eye_rect[1] + self.right_eye_rect[3],
                            self.right_eye_rect[0]:self.right_eye_rect[0] + self.right_eye_rect[2]
                        ]
                        image_color_resized_debug = cv2.resize(right_eye_img_rgba, (200, 200))
                        texture = Texture.create(size=(200, 200))
                        texture.blit_buffer(bytes(image_color_resized_debug), colorfmt="rgba", bufferfmt="ubyte")
                        with self.right_eye_image_dbg.canvas:
                            Rectangle(texture=texture, pos=self.right_eye_image_dbg.pos, size=(200, 200))

                    # image_prediction = blink.get_prediction(self.model, image_color_resized)

                    input_data = np.float32(image_color_resized)
                    # input_data = image_color_resized
                    input_data = np.array([input_data])  # Convert single image to a batch

                    # *** TensorflowLite
                    if platform == "macosx" or platform == "android":
                        output = self.interpreter.get_output_details()[0]
                        input = self.interpreter.get_input_details()[0]
                        self.interpreter.set_tensor(input['index'], input_data)
                        self.interpreter.invoke()
                        output_tensor = self.interpreter.get_tensor(output['index'])
                        output_tensor = np.squeeze(output_tensor)

                        if self.analise_iniciada:
                            dados_frame_atual.olho_direito_aberto = 1 if output_tensor[1] > output_tensor[0] else 0

                        teste_tflite_output = "tflite output: {}".format(
                            output_tensor,
                        )
                        logger.info(teste_tflite_output)

                        # teste_tflite_output = self.model.pred(input_data)
                        # teste_tflite_output = output['index']
                        logger.info("teste tflite output: {}".format(teste_tflite_output))
                    ###

                    if self.DEBUG_EYES:
                        self.right_eye_label_dbg.text = "Open" if output_tensor[1] > output_tensor[0] else "Closed"

                # Código repetido, generalizar...
                if self.left_eye_rect is not None:
                    left_eye_img = pixel_array[
                        self.left_eye_rect[1]:self.left_eye_rect[1] + self.left_eye_rect[3],
                        self.left_eye_rect[0]:self.left_eye_rect[0] + self.left_eye_rect[2]
                    ]
                    image_color_resized = cv2.resize(left_eye_img, (32, 32))
                    logger.info("pixel_array.shape: {} image_color_resized.shape {} right_eye_img.shape {}".format(
                        pixel_array.shape, image_color_resized.shape, left_eye_img.shape))

                    # Cria imagem para debug...
                    if self.DEBUG_EYES:
                        left_eye_img_rgba = pixel_array_rgba[
                            self.left_eye_rect[1]:self.left_eye_rect[1] + self.left_eye_rect[3],
                            self.left_eye_rect[0]:self.left_eye_rect[0] + self.left_eye_rect[2]
                        ]
                        image_color_resized_debug = cv2.resize(left_eye_img_rgba, (200, 200))
                        texture = Texture.create(size=(200, 200))
                        texture.blit_buffer(bytes(image_color_resized_debug), colorfmt="rgba", bufferfmt="ubyte")
                        with self.left_eye_image_dbg.canvas:
                            Rectangle(texture=texture, pos=self.left_eye_image_dbg.pos, size=(200, 200))

                    # image_prediction = blink.get_prediction(self.model, image_color_resized)

                    input_data = np.float32(image_color_resized)
                    # input_data = image_color_resized
                    input_data = np.array([input_data])  # Convert single image to a batch

                    # *** TensorflowLite
                    if platform == "macosx" or platform == "android":
                        output = self.interpreter.get_output_details()[0]
                        input = self.interpreter.get_input_details()[0]
                        self.interpreter.set_tensor(input['index'], input_data)
                        self.interpreter.invoke()
                        output_tensor = self.interpreter.get_tensor(output['index'])
                        output_tensor = np.squeeze(output_tensor)

                        if self.analise_iniciada:
                            dados_frame_atual.olho_esquerdo_aberto = 1 if output_tensor[1] > output_tensor[0] else 0

                        teste_tflite_output = "tflite output: {}".format(
                            output_tensor,
                        )
                        logger.info(teste_tflite_output)

                        # teste_tflite_output = self.model.pred(input_data)
                        # teste_tflite_output = output['index']
                        logger.info("teste tflite output: {}".format(teste_tflite_output))
                    ###

                    if self.analise_iniciada:
                        if self.ultima_analise.dados_frames is None:
                            # Primeiro frame...
                            self.ultima_analise.dados_frames = []
                            self.ultima_analise.dados_frames.append(dados_frame_atual)
                        else:
                            self.ultima_analise.dados_frames.append(dados_frame_atual)

                    if self.DEBUG_EYES:
                        self.left_eye_label_dbg.text = "Open" if output_tensor[1] > output_tensor[0] else "Closed"

        # Desenha os retângulos da face e dos olhos no canvas
        if platform == "macosx" or platform == "android":
            if self.instruction_group is not None:
                # if platform == "macosx":
                # self.camera_display_widget.canvas.remove(self.instruction_group)
                self.canvas_widget.canvas.remove(self.instruction_group)
            if self.DEBUG_EYES:
                self.instruction_group = InstructionGroup()
                if self.face_rect is not None:
                    # Cria sequencia de instrucoes para a face
                    self.create_group_instructions_rect(
                        self.camera_display_widget,
                        self.face_rect,
                        Color(1, 1, 1),  # Face será cinza
                    )
                if self.left_eye_rect is not None:
                    # Cria sequencia de instrucoes para olho esquerdo
                    self.create_group_instructions_rect(
                        self.camera_display_widget,
                        self.left_eye_rect,
                        Color(0, 1, 0),  # Olho esquerdo será verde
                    )
                if self.right_eye_rect is not None:
                    # Cria sequencia de instrucoes para olho direito
                    self.create_group_instructions_rect(
                        self.camera_display_widget,
                        self.right_eye_rect,
                        Color(0, 0, 1),  # Olho direito será azul
                    )

                # for instruction in self.instruction_group.get_group('my_group'):
                #    logger.info("Instruction :{}".format(instruction))

                # if platform == "macosx":
                # self.camera_display_widget.canvas.add(self.instruction_group)
                self.canvas_widget.canvas.add(self.instruction_group)

                """
                elif platform == "android":
                    # Na plataforma Android passa o grupo de instruções para a classe que faz a interface
                    # com a camera, que vai renderizar os retângulos no método _update_preview...

                    if self.camera_display_widget.current_camera is not None:
                        self.camera_display_widget.current_camera.instruction_group = self.instruction_group
                """
        # logger.info("***Updating Canvas...")

    def create_group_instructions_rect(self, cdw, rect, color):
        # O y deve ser ajustado, no canvas a origem (0,0) é no canto inferior esquerdo. As coordenadas
        # de detecção tem origem no canto superior esquerdo.
        ey_ajustado = float(cdw.height - rect[1] + cdw.pos[1] - rect[3])
        logger.info("self.camera_display_widget.pos: {}".format(cdw.pos))
        self.instruction_group.add(color)
        self.instruction_group.add(
            Line(
                rectangle=(rect[0], ey_ajustado, rect[2], rect[3]),
                width=2,
                # group="faces_olhos",
            )
        )
        # self.eye_rectangle.add(Line(rectangle=(0, 0, 50, 50), width=3))
        # self.eye_rectangle.add(Line(rectangle=(0, self.camera_display_widget.height, 50, 50), width=3))

    # =========== Define uma Snackbar
    def snackbar_show(self, texto):
        snackbar = Snackbar(text=texto)
        snackbar.open()

    # Tentando aumentar o contraste da imagem para ver o resultado na detecção de olhos...
    # https://stackoverflow.com/questions/39308030/how-do-i-increase-the-contrast-of-an-image-in-python-opencv
    def pre_process_image(self, img):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)

        # Applying CLAHE to L-channel
        # feel free to try different values for the limit and grid size:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)

        # merge the CLAHE enhanced L-channel with the a and b channel
        limg = cv2.merge((cl, a, b))

        # Converting image from LAB Color model to BGR color spcae
        enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        return enhanced_img

    def get_eye(self, x, y, w, h, ex, ey, ew, eh):
        # Calcula o retangulo possível para os olhos
        dist = 0.1
        _xr = x + w * dist  # right eye x
        _xl = x + (w / 2) + w * dist  # left eye x
        _y = y + h * dist
        _w = (w * (1 - 4 * dist)) / 2
        _h = (h * (1 - 4 * dist)) / 2
        # Calcula o x,y central dos olhos
        _ex = ex + ew / 2
        _ey = ey + eh / 2
        logger.info("_xr:{} _xl:{} _y:{} _w:{} _h:{} / _ex:{} _ey:{}".format(_xr, _xl, _y, _w, _h, _ex, _ey))
        if(_ex < (_xr + _w)) and (_ex > _xr) and (_ey < (_y + _h)) and (_ey > _y):
            return self.Eyes.RIGHT
        # elif (_ex < (_xl + _w)) and (_ex > _xl) and (_ey < (_y + _h)) and (_ey > _y):
        elif (
                (_ex < (_xl + _w)) and
                (_ex > _xl) and (_ey < (_y + _h)) and (_ey > _y)
        ):
            return self.Eyes.LEFT
        else:
            return self.Eyes.UNDEFINED


if __name__ == "__main__":
    BlinkApp().run()
