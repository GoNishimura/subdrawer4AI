import tkinter as tk
import json
import math
import os
import copy
from PIL import Image, ImageTk, ImageDraw
import config


class CanvasArea(tk.Canvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.width = 512
        self.height = 512
        self.configure(width=self.width, height=self.height, bg="black")
        self.image_2_show = None
        self.hovered_keypoint = None
        self.saving_canvas = None
        self.pose_data = {}
        self.keypoint_radius = 6
        self.keypoint_area_radius = 9
        self.line_width = 6
        self.text_size = 12
        self.background_mode = config.BACKGROUND_MODES[0]
        self.bind("<Motion>", self.on_canvas_move)
        self.bind("<B1-Motion>", self.on_canvas_drag)
        self.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.load_pose()
        self.draw_skeleton()

    def get_pose_data_path(self, saving_path=False):
        path = os.path.join(config.WORKING_FOLDER_PATH, "pose_data.json")
        if saving_path or os.path.isfile(path): return path
        return os.path.join(config.HOME_PATH, "initial_pose.json")
    
    def get_generated_images_path(self):
        return os.path.join(config.WORKING_FOLDER_PATH, "generated_images")
    
    def get_resized_image(self, file_name):
        path = os.path.join(config.WORKING_FOLDER_PATH, file_name)
        if os.path.isfile(path):
            with Image.open(path) as loaded:
                new_width = loaded.width * self.height // loaded.height
                if new_width >= 1: return loaded.resize((new_width, self.height))
        else:
            return None

    def get_pose_data(self):
        try:
            path = self.get_pose_data_path()
            with open(path) as file:
                return json.load(file)
        except FileNotFoundError:
            raise Exception("{} doesn't exist in the folder.".format(path))
        except json.JSONDecodeError:
            # Handle the case when the pose data file is not a valid JSON file
            raise Exception("Invalid JSON file. Please check the file.")

    def load_pose(self):
        try:
            self.pose_data = self.get_pose_data()
        except:
            raise
        else:
            config.set_image_name_list()
            if len(config.IMAGE_NAME_LIST) >= 1 and "image_1.jpg" in self.pose_data:
                keypoints = self.pose_data.pop("image_1.jpg")
                self.pose_data[config.IMAGE_NAME_LIST[0]] = keypoints

    def get_keypoints(self):
        return self.pose_data[config.IMAGE_NAME_NOW][config.POSE_ID_NOW]

    def rgb_to_hex(self, arr):
        return '#{:02x}{:02x}{:02x}'.format(arr[0], arr[1], arr[2])

    def draw_skeleton(self):
        self.delete("lines", "circles")
        saving_canvas_exists = self.saving_canvas is not None
        if saving_canvas_exists:
            self.saving_canvas.rectangle((0, 0, self.width, self.height), fill="black")

        keypoints = self.get_keypoints()
        # Draw lines
        for index, (start, end) in enumerate(config.CONNECTIONS_LIST):
            if start in keypoints and end in keypoints:
                start_x, start_y = keypoints[start]
                end_x, end_y = keypoints[end]
                self.create_line(start_x, start_y, end_x, end_y, width=self.line_width,
                                fill=self.rgb_to_hex(config.KEYPOINT_COLOR[index]), tags="lines")
                if saving_canvas_exists:
                    self.saving_canvas.line(keypoints[start] + keypoints[end], width=self.line_width,
                                            fill=self.rgb_to_hex(config.KEYPOINT_COLOR[index]))
        # Draw circles
        for index, coordinates in enumerate(keypoints.values()):
            x, y = coordinates
            self.create_oval(x - self.keypoint_radius, y - self.keypoint_radius,
                                x + self.keypoint_radius, y + self.keypoint_radius, 
                                fill=self.rgb_to_hex(config.KEYPOINT_COLOR[index]), width=0, tags="circles")
            if saving_canvas_exists:
                self.saving_canvas.ellipse([x - self.keypoint_radius, y - self.keypoint_radius,
                                            x + self.keypoint_radius, y + self.keypoint_radius], width=0,
                                            fill=self.rgb_to_hex(config.KEYPOINT_COLOR[index]))
                
    def draw_keypoint_names(self, just_delete=False):
        self.delete("names")
        if just_delete: return
        for index, (keypoint, coordinates) in enumerate(self.get_keypoints().items()):
            self.create_text(coordinates[0], coordinates[1] - self.text_size, text=keypoint.replace("_", " "), 
                             tags="names", font=("", self.text_size),
                             fill=self.rgb_to_hex(config.KEYPOINT_COLOR[index]))

    def resize_skeleton(self, width_rate, height_rate):
        for keypoint, coordinates in self.get_keypoints().items():
            self.pose_data[config.IMAGE_NAME_NOW][config.POSE_ID_NOW][keypoint] = [
                coordinates[0] * width_rate, coordinates[1] * height_rate
            ]
    
    def set_image_and_pose_now(self, set_image=True):
        self.delete("image")
        
        # Load image and put it on the canvas if it exists
        resized_image = self.get_resized_image(config.IMAGE_NAME_NOW)
        if resized_image is not None and set_image and self.background_mode == "Original Image":
            self.image_2_show = ImageTk.PhotoImage(resized_image)
            # Need this 2 for showing properly.
            self.create_image(2, 2, 
                              image=self.image_2_show, anchor=tk.NW, tags="image")
            self.resize_canvas(resized_image.width, resized_image.height)
        
        # Make a new pose data for the image if it doesn't exist
        if config.IMAGE_NAME_NOW not in self.pose_data:
            self.pose_data[config.IMAGE_NAME_NOW] = copy.deepcopy(
                list(self.pose_data.values())[-1])
    
        self.draw_skeleton()

    def save_as_image(self):
        generated_images_dir = self.get_generated_images_path()
        os.makedirs(generated_images_dir, exist_ok=True)
        generated_image_path = os.path.join(generated_images_dir, config.IMAGE_NAME_NOW)
        file_mode = "RGB" if config.check_image_extension(config.IMAGE_NAME_NOW, ".jpg") else "P"
        saving_image = Image.new(file_mode, (self.width, self.height), "black")
        # When you need pose drawn images
        # original_image = self.get_resized_image(config.IMAGE_NAME_NOW)
        # saving_image.paste(original_image)
        self.saving_canvas = ImageDraw.Draw(saving_image)
        self.draw_skeleton()
        saving_image.save(generated_image_path)
        
    def save_pose_data(self):
        try:
            with open(self.get_pose_data_path(saving_path=True), "w") as file:
                json.dump(self.pose_data, file, indent=4)
        except:
            raise

    def is_pose_data_saved(self):
        saved_or_initial_data = self.get_pose_data()
        return saved_or_initial_data == self.pose_data

    def on_canvas_move(self, event):
        hovered_on = False
        for keypoint, coordinates in self.get_keypoints().items():
            if math.sqrt(
                (event.x - coordinates[0]) ** 2 + (event.y - coordinates[1]) ** 2) <= self.keypoint_area_radius:
                self.hovered_keypoint = keypoint
                hovered_on = True
                self.draw_keypoint_names()
                break
        if not hovered_on: 
            self.hovered_keypoint = None
            self.draw_keypoint_names(just_delete=True)

    def on_canvas_drag(self, event):
        if self.hovered_keypoint:
            self.get_keypoints()[self.hovered_keypoint] = [event.x, event.y]
            self.draw_skeleton()
            self.draw_keypoint_names()

    def on_canvas_release(self, event):
        self.hovered_keypoint = None
        self.draw_keypoint_names(just_delete=True)
    
    def toggle_keypoint(self, keypoint):
        pose_keypoints = self.get_keypoints()
        if keypoint in pose_keypoints:
            del pose_keypoints[keypoint]
        else:
            pose_keypoints[keypoint] = [self.width, 0]
        self.draw_skeleton()

    def resize_canvas(self, width, height):
        self.resize_skeleton(width / self.width, height / self.height)
        self.width = width
        self.height = height
        self.configure(width=self.width, height=self.height)
        self.master.width_slider.set(self.width)