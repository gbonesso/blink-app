import math
import cv2

from kivy.graphics.texture import Texture

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


def get_texture_from_rgba_array(pixel_array_rgba, rect, size):
    cropped_img_rgba = pixel_array_rgba[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
    img_rgba_resized = cv2.resize(cropped_img_rgba, size)
    texture = Texture.create(size=size)
    texture.blit_buffer(bytes(img_rgba_resized), colorfmt="rgba", bufferfmt="ubyte")
    return texture
