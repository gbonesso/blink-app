import logging
from functools import partial

from kivy import platform
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.context_instructions import PushMatrix, PopMatrix, Rotate
from kivy.uix.stencilview import StencilView
from kivy.properties import (
    ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty, OptionProperty)

from camera2.camera2 import PyCameraInterface

if platform == "android":
    from android.permissions import request_permission, check_permission, Permission

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class CameraDisplayWidget(StencilView):
    texture = ObjectProperty(None, allownone=True)
    resolution = ListProperty([1, 1])

    tex_coords = ListProperty([0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0])
    correct_camera = BooleanProperty(False)

    _rect_pos = ListProperty([0, 0])
    _rect_size = ListProperty([1, 1])

    camera_resolution = ListProperty([1920, 1080])

    current_camera = ObjectProperty(None, allownone=True)
    camera_display_widget = ObjectProperty(None, allownone=True)

    cameras_to_use = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.camera_interface = PyCameraInterface()
        self.debug_print_camera_info()
        self.inspect_cameras()

        # Rotaciona a imagem no Android
        with self.canvas.before:
            PushMatrix()
            Rotate(angle=-90, origin=self.center)

        with self.canvas.after:
            PopMatrix()

        self.bind(
            pos=self._update_rect,
            size=self._update_rect,
            resolution=self._update_rect,
            texture=self._update_rect,
        )
        logger.info("*** CameraDisplayWidget.__init__()...")

        self.restart_stream()

    def inspect_cameras(self):
        cameras = self.camera_interface.cameras

        for camera in cameras:
            if camera.facing == "BACK":
                self.cameras_to_use.append(camera)
        for camera in cameras:
            if camera.facing == "FRONT":
                self.cameras_to_use.append(camera)

    def rotate_cameras(self):
        logger.info("rotate_cameras acionado...")
        self.ensure_camera_closed()
        self.cameras_to_use = self.cameras_to_use[1:] + [self.cameras_to_use[0]]
        self.attempt_stream_camera(self.cameras_to_use[0])

    def restart_stream(self):
        self.ensure_camera_closed()
        Clock.schedule_once(self._restart_stream, 0)

    def _restart_stream(self, dt):
        # logger.info("On restart, state is {}".format(self.camera_permission_state))
        self.attempt_stream_camera(self.cameras_to_use[0])

    def debug_print_camera_info(self):
        cameras = self.camera_interface.cameras
        camera_infos = ["Camera ID {}, facing {}".format(c.camera_id, c.facing) for c in cameras]
        for camera in cameras:
            logger.info("Camera ID {}, facing {}, resolutions {}".format(
                camera.camera_id, camera.facing, camera.supported_resolutions))

    def stream_camera_index(self, index):
        self.attempt_stream_camera(self.camera_interface.cameras[index])

    def attempt_stream_camera(self, camera):
        """Start streaming from the given camera, if we have the CAMERA
        permission, otherwise request the permission first.
        """

        self.stream_camera(camera)

    def stream_camera(self, camera):
        resolution = self.select_resolution(
            Window.size,
            camera.supported_resolutions,
            #best=(1920, 1080)
            best=(720, 720)
        )
        if resolution is None:
            logger.error(f"Found no good resolution in {camera.supported_resolutions} for Window.size {Window.size}")
            return
        else:
            logger.info(f"Chose resolution {resolution} from choices {camera.supported_resolutions}")
        self.camera_resolution = resolution
        camera.open(callback=self._stream_camera_open_callback)

    def _stream_camera_open_callback(self, camera, action):
        if action == "OPENED":
            logger.info("Camera opened, preparing to start preview")
            Clock.schedule_once(partial(self._stream_camera_start_preview, camera), 0)
        else:
            logger.info("Ignoring camera event {action}")

    def _stream_camera_start_preview(self, camera, *args):
        logger.info("Starting preview of camera {camera}")
        if camera.facing == "FRONT":
            self.correct_camera = True
        else:
            self.correct_camera = False
        self.texture = camera.start_preview(tuple(self.camera_resolution))
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                pos=self._rect_pos,
                size=self._rect_size,
                texture=self.texture,
                tex_coords=self.tex_coords
            )

        self.current_camera = camera

    def select_resolution(self, window_size, resolutions, best=None):
        if best in resolutions:
            return best

        if not resolutions:
            return None

        win_x, win_y = window_size
        larger_resolutions = [(x, y) for (x, y) in resolutions if (x > win_x and y > win_y)]

        if larger_resolutions:
            return min(larger_resolutions, key=lambda r: r[0] * r[1])

        smaller_resolutions = resolutions  # if we didn't find one yet, all are smaller than the requested Window size
        return max(smaller_resolutions, key=lambda r: r[0] * r[1])

    def ensure_camera_closed(self):
        if self.current_camera is not None:
            self.current_camera.close()
            self.current_camera = None

    def on_pause(self):

        logger.info("Closing camera due to pause")
        self.ensure_camera_closed()

        return super().on_pause()

    def on_resume(self):
        logger.info("Opening camera due to resume")
        self.restart_stream()

    def on_correct_camera(self, instance, correct):
        logger.info("Correct became", correct)
        if correct:
            self.tex_coords = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
            logger.info("Set 0!")
        else:
            self.tex_coords = [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]
            logger.info("Set 1!")

    def on_tex_coords(self, instance, value):
        logger.info("tex_coords became", self.tex_coords)

    def _update_rect(self, *args):
        self._update_rect_to_fill()

    def _update_rect_to_fit(self, *args):
        logger.info('*** _update_rect_to_fit')
        w, h = self.resolution
        aspect_ratio = h / w

        aspect_width = self.width
        aspect_height = self.width * h / w
        if aspect_height > self.height:
            aspect_height = self.height
            aspect_width = aspect_height * w / h

        aspect_height = int(aspect_height)
        aspect_width = int(aspect_width)

        self._rect_pos = [self.center_x - aspect_width / 2,
                          self.center_y - aspect_height / 2]

        self._rect_size = [aspect_width, aspect_height]

    def _update_rect_to_fill(self, *args):
        logger.info('*** _update_rect_to_fit')
        w, h = self.resolution

        aspect_ratio = h / w

        aspect_width = self.width
        aspect_height = self.width * h / w
        if aspect_height < self.height:
            aspect_height = self.height
            aspect_width = aspect_height * w / h

        aspect_height = int(aspect_height)
        aspect_width = int(aspect_width)

        self._rect_pos = [self.center_x - aspect_width / 2,
                          self.center_y - aspect_height / 2]

        self._rect_size = [aspect_width, aspect_height]