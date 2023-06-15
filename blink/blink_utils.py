import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

from scipy.spatial import distance as dist
import platform
try:
    import dlib

    # initialize dlib variables
    dlib_detector = dlib.get_frontal_face_detector()
    dlib_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
except:
    logger.info("Erro ao importar dlib...")
import numpy as np  # linear algebra
import tensorflow as tf




logger.info("platform.system(): {}".format(platform.system()))

# define three constants.
# You can later experiment with these constants by changing them to adaptive variables.
EAR_THRESHOLD = 0.21  # eye aspect ratio to indicate blink
EAR_CONSEC_FRAMES = 3  # number of consecutive frames the eye must be below the threshold
SKIP_FIRST_FRAMES = 0  # how many frames we should skip at the beggining




def create_box(eyes_coordinates):
    hor_dist = eyes_coordinates[3][0] - eyes_coordinates[0][0]
    mid_y = eyes_coordinates[1][1] - int((eyes_coordinates[1][1] - eyes_coordinates[5][1]) / 2)
    mid_x = eyes_coordinates[0][0] + int(hor_dist / 2)
    base_sq = int(hor_dist * 1.2)  # 20% maior que a distancia entre as extremidades horizontais detectadas
    half_base_sq = int(base_sq / 2)
    # print(base_sq, hor_dist_l, mid_x, mid_y)
    box_x = mid_x - half_base_sq
    box_y = mid_y - half_base_sq
    return box_x, box_y, base_sq, base_sq


# define ear function
def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear


def get_eyes_landmarks(frame):
    l_start = 42
    l_end = 48
    r_start = 36
    r_end = 42
    left_eye = right_eye = None
    # detect faces in the grayscale frame
    rects = dlib_detector(frame, 0)
    #print(rects, len(rects))
    face_detected = False
    # loop over the face detections
    for rect in rects:
        face_detected = True
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = dlib_predictor(frame, rect)
        shape = np.array([[p.x, p.y] for p in shape.parts()])
        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes
        left_eye = shape[l_start:l_end]
        right_eye = shape[r_start:r_end]
        # print(left_eye, right_eye)

    return left_eye, right_eye, face_detected


def get_eye_image(frame, eye_coordinates):
    eye_box = create_box(eye_coordinates)
    eye_img = frame[eye_box[1]:eye_box[1] + eye_box[3],
                   eye_box[0]:eye_box[0] + eye_box[2]]
    return eye_img


def get_prediction(model, image):
    input_arr = tf.keras.preprocessing.image.img_to_array(image)
    input_arr = np.array([input_arr])  # Convert single image to a batch.
    # input_arr = input_arr.astype('float32') / 255.  # This is VERY important
    predictions = model.predict(input_arr, verbose=0)
    print(predictions)
    return predictions.argmax()
