import os

CONNECTIONS_LIST = [
    ("nose", "neck"), 
    ("right_eye", "right_ear"), ("left_eye", "left_ear"),
    ("right_eye", "nose"), ("left_eye", "nose"),
    ("neck", "right_shoulder"), ("neck", "left_shoulder"),
    ("neck", "right_hip",), ("neck", "left_hip"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
]
KEYPOINTS_LIST = [
    "nose", "neck", "right_eye", "left_eye", "right_ear", "left_ear",
    "right_shoulder", "left_shoulder", "right_elbow", "left_elbow",
    "right_wrist", "left_wrist", "right_hip", "left_hip", "right_knee",
    "left_knee", "right_ankle", "left_ankle"
]
KEYPOINT_COLOR = [
    [0, 0, 255], [255, 0, 0], [255, 170, 0], [255, 255, 0], [255, 85, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
    [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [85, 0, 255],
    [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]
]
BACKGROUND_MODES = ["Original Image", "Black BG"]

# Global variables
HOME_PATH = os.path.realpath("./")
WORKING_FOLDER_PATH = os.path.realpath("./")
IMAGE_NAME_LIST = []
IMAGE_NAME_NOW = "image_1.jpg"
POSE_ID_NOW = "pose1"
INIT_IMAGE_SIZE = [512, 512]

# Common functions
def check_image_extension(file_name, extension):
    if extension.lower() in [".jpg", ".jpeg"]:
        return file_name.lower().endswith((".jpg", ".jpeg"))
    else:
        return file_name.endswith(extension)

def set_image_name_list():
    list = [f for f in os.listdir(WORKING_FOLDER_PATH) if check_image_extension(f, ".jpg") or check_image_extension(f, ".png")]
    IMAGE_NAME_LIST.clear()
    IMAGE_NAME_LIST.extend(list) 