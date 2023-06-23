import logging
import numpy as np
import cv2

from kivy import platform

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
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


class TensorflowModel:

    def __init__(self, **kwargs):
        if platform == "macosx" or platform == "android":
            self.interpreter = Interpreter(model_path="assets/Blink_YOLOv5_v2_best-fp16.tflite")
            self.interpreter.allocate_tensors()
            input_details = self.interpreter.get_input_details()[0]
            logger.info("yolo - input_tensor.shape: {}".format(input_details['shape']))
            logger.info("yolo - input_tensor.quantization_parameters: {}".format(input_details['quantization_parameters']))
            logger.info("yolo - input_tensor.quantization_parameters.scales: {}".
                        format(input_details['quantization_parameters']['scales']))
            # logger.info("input_tensor.quantization_parameters: {}".format(input['quantization_parameters']))

    def get_eyes_coordinates(self, pixel_array):
        logger.info("yolo - len(pixel_array): {} min: {} max: {}".format(len(pixel_array), np.min(pixel_array),
                                                                         np.max(pixel_array)))
        # Normalizing the array to 0-1 range
        pixel_array = (pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))
        logger.info("yolo - after norm - min: {} max: {}".format(np.min(pixel_array), np.max(pixel_array)))

        image_color_resized = cv2.resize(pixel_array, (640, 640))
        input_data = np.float32(image_color_resized)
        # input_data = image_color_resized
        input_data = np.array([input_data])  # Convert single image to a batch

        # *** TensorflowLite
        if platform == "macosx" or platform == "android":
            # output = self.interpreter.get_output_details()[0]
            logger.info("yolo - get_output_details - before invoke: {}".format(self.interpreter.get_output_details()))
            input_details = self.interpreter.get_input_details()[0]
            self.interpreter.set_tensor(input_details['index'], input_data)
            self.interpreter.invoke()

            output_details = self.interpreter.get_output_details()
            output_data = self.interpreter.get_tensor(output_details[0]['index'])  # get tensor  x(1, 25200, 7)
            xyxy, classes, scores = self.yolo_detect(output_data)  # boxes(x,y,x,y), classes(int), scores(float) [25200]
            for i in range(len(scores)):
                if (scores[i] > 0.5) and (scores[i] <= 1.0):
                    """
                    H = frame.shape[0]
                    W = frame.shape[1]
                    xmin = int(max(1, (xyxy[0][i] * W)))
                    ymin = int(max(1, (xyxy[1][i] * H)))
                    xmax = int(min(H, (xyxy[2][i] * W)))
                    ymax = int(min(W, (xyxy[3][i] * H)))

                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
                    """
                    logger.info("xmin: {} ymin: {} xmax: {} ymax: {} score: {} classe: {}".format(xyxy[0][i],
                        xyxy[1][i], xyxy[2][i], xyxy[3][i], scores[i], classes[i]))
            logger.debug("yolo - xyxy: {} classes: {} scores: {}".format(xyxy, classes, scores))

            output_tensor = self.interpreter.get_tensor(output_details[0]['index'])
            output_tensor = np.squeeze(output_tensor)

            # teste_tflite_output = output['index']
            logger.info("yolo - output_tensor: {}".format(output_tensor[0]))
            logger.info("yolo - get_output_details - after invoke: {}".format(self.interpreter.get_output_details()))
            # logger.info("yolo - output_tensor.shape: {}".format(output_tensor.shape))

    def class_filter(self, classdata):
        classes = []  # create a list
        for i in range(classdata.shape[0]):  # loop through all predictions
            classes.append(classdata[i].argmax())  # get the best classification location
        return classes  # return classes (int)

    def yolo_detect(self, output_data):  # input = interpreter, output is boxes(xyxy), classes, scores
        output_data = output_data[0]  # x(1, 25200, 7) to x(25200, 7)
        boxes = np.squeeze(output_data[..., :4])  # boxes  [25200, 4]
        scores = np.squeeze(output_data[..., 4:5])  # confidences  [25200, 1]
        classes = self.class_filter(output_data[..., 5:])  # get classes
        # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
        x, y, w, h = boxes[..., 0], boxes[..., 1], boxes[..., 2], boxes[..., 3]  # xywh
        xyxy = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]  # xywh to xyxy   [4, 25200]

        return xyxy, classes, scores  # output is boxes(x,y,x,y), classes(int), scores(float) [predictions length]