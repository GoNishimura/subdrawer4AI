import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from tkinter import messagebox
import os
from canvas_area import CanvasArea
import config


class MainPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("subdrawer4AI")
        self.geometry("900x900")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(True, True)
        
        self.canvas_area = CanvasArea(self)
        self.canvas_area.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky=tk.NW)
        
        # Frame for keypoint buttons
        self.keypoint_buttons_frame = tk.LabelFrame(self, text="Add / Remove Keypoints")
        self.keypoint_buttons_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
        # # Add keypoint buttons
        for index, keypoint in enumerate(config.KEYPOINTS_LIST):
            button = tk.Button(
                self.keypoint_buttons_frame,
                text=keypoint.replace("_", " "),
                command=lambda key=keypoint: self.canvas_area.toggle_keypoint(key),
            )
            button.grid(row=index // 2, column=index % 2, padx=5, pady=5, sticky="w")

        # Frame for background mode
        self.background_frame = tk.Frame(self)
        self.background_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        self.background_label = tk.Label(self.background_frame, text="Background mode:")
        self.background_label.pack(side="left")

        self.background_mode_combobox = ttk.Combobox(
            self.background_frame, values=config.BACKGROUND_MODES, state="readonly"
        )
        self.background_mode_combobox.pack(side="left")
        self.background_mode_combobox.set(config.BACKGROUND_MODES[0])
        self.background_mode_combobox.bind("<<ComboboxSelected>>", 
                                           self.handle_background_mode_combobox_change)
        
        # Frame for load and save options
        self.load_save_frame = tk.Frame(self)
        self.load_save_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # # Frame for load options
        self.load_frame = tk.Frame(self.load_save_frame)
        self.load_frame.grid(row=0, column=0, columnspan=2, sticky="w")

        self.load_from_folder_button = tk.Button(self.load_frame, text="Load From Folder", 
                                                 command=self.load_from_folder)
        self.load_from_folder_button.pack(side="left", padx=5)

        self.fixed_label = tk.Label(self.load_frame, text="Selected Folder: ")
        self.fixed_label.pack(side="left", padx=5)

        self.folder_label = tk.Label(self.load_frame, text=config.WORKING_FOLDER_PATH)
        self.folder_label.pack(side="left", padx=5)

        # # Frame for save options
        self.save_frame = tk.Frame(self.load_save_frame)
        self.save_frame.grid(row=1, column=0, columnspan=2, sticky="w")
        self.save_images_poses_button = tk.Button(self.save_frame, text="Save Images & Poses",
                                                  command=self.save_images_poses)
        self.save_images_poses_button.pack(side="left", padx=5)

        self.saved_message = tk.Label(self.save_frame, text="")
        self.saved_message.pack(side="left", padx=5)
        
        # Frame for image listbox
        self.image_listbox_frame = tk.Frame(self)
        self.image_listbox_frame.grid(row=1, column=2, rowspan=2, columnspan=2, padx=10, pady=5, sticky="nsew")
        
        self.key_instructions = tk.Label(self.image_listbox_frame, text="'a': prev / 's': next")
        self.key_instructions.grid(row=0, column=0)

        # # Frame for listbox
        self.listbox_frame = tk.Frame(self.image_listbox_frame)
        self.listbox_frame.grid(row=1, column=0, sticky="nsew")

        self.image_listbox = tk.Listbox(self.listbox_frame, width=30)
        self.image_listbox.pack(side="left", fill="both", expand=True)
        self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)

        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", 
                                       command=self.image_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.config(command=self.image_listbox.yview)
        self.image_listbox.config(yscrollcommand=self.scrollbar.set)

        # Frame for sliders
        self.sliders_frame = tk.Frame(self)
        self.sliders_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        
        # # width slider
        self.width_slider = tk.Scale(self.sliders_frame, from_=1, to=self.winfo_screenwidth(), 
                                      orient="horizontal", length=150, 
                                      label="Image Width:",
                                      command=self.update_canvas_size)
        self.width_slider.set(self.canvas_area.width)
        self.width_slider.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Bind events here after sliders are initialized
        self.bind("<Button-1>", self.on_click)
        self.bind("<KeyPress-s>", self.on_image_select)
        self.bind("<KeyPress-a>", self.on_image_select)

        self.populate_image_listbox()

    def on_click(self, event):
        self.saved_message["text"] = ""

    def force_select_in_image_list(self, index):
        self.image_listbox.select_clear(0, tk.END)
        self.image_listbox.select_set(index)
        config.IMAGE_NAME_NOW = self.image_listbox.get(index)
        self.image_listbox.see(index)
        self.canvas_area.set_image_and_pose_now()

    def populate_image_listbox(self):
        config.set_image_name_list()
        self.image_listbox.delete(0, tk.END)

        for file_name in config.IMAGE_NAME_LIST:
            self.image_listbox.insert(tk.END, file_name)
        
        if len(config.IMAGE_NAME_LIST) == 0:
            # Pseudo array with random strings representing image file names
            config.IMAGE_NAME_LIST = [f"image_{i+1}.jpg" for i in range(24)]
            for image in config.IMAGE_NAME_LIST:
                self.image_listbox.insert(tk.END, image)
        
        # Select the first image as default
        self.force_select_in_image_list(0)

    def on_image_select(self, event):
        selected_index = self.image_listbox.curselection()
        if len(selected_index) == 0: 
            return # when fired by ComboboxSelected
        else:
            selected_index = selected_index[0]
        char = event.char
        shift_distance = -1 if char == "a" else 1 if char == "s" else 0
        final_index = (selected_index + shift_distance) % len(config.IMAGE_NAME_LIST)
        self.force_select_in_image_list(final_index)

    def handle_background_mode_combobox_change(self, event):
        mode = self.background_mode_combobox.get()
        self.canvas_area.background_mode = mode
        index_now = config.IMAGE_NAME_LIST.index(config.IMAGE_NAME_NOW)
        self.force_select_in_image_list(index_now)
    
    def load_from_folder(self):
        path_to_recover = config.WORKING_FOLDER_PATH
        config.WORKING_FOLDER_PATH = filedialog.askdirectory()
        if config.WORKING_FOLDER_PATH == "": # When cancelled
            config.WORKING_FOLDER_PATH = path_to_recover
            return
        self.folder_label["text"] = config.WORKING_FOLDER_PATH

        try:
            self.canvas_area.load_pose()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading pose data:\n{str(e)}")

        self.populate_image_listbox()

    def save_images_poses(self):
        current_image = config.IMAGE_NAME_NOW
        try:
            # Select each image and save the pose as an image
            for image_name in config.IMAGE_NAME_LIST:
                config.IMAGE_NAME_NOW = image_name
                self.canvas_area.set_image_and_pose_now(set_image=False)
                self.canvas_area.update()
                self.canvas_area.save_as_image()

            self.canvas_area.save_pose_data()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving images and poses:\n{str(e)}")
        else:
            self.saved_message["text"] = "Images and poses saved successfully!"
            config.IMAGE_NAME_NOW = current_image
            self.canvas_area.set_image_and_pose_now()

    def update_canvas_size(self, _):
        new_width = self.width_slider.get() if hasattr(self, "width_slider") else self.canvas_area.width
        if new_width != self.canvas_area.width:
            self.canvas_area.resize_canvas(
                new_width, 
                self.canvas_area.height * new_width // self.canvas_area.width)
            self.canvas_area.set_image_and_pose_now()

    def on_closing(self):
        already_saved = self.canvas_area.is_pose_data_saved()
        if already_saved:
            self.destroy()
        else:
            user_confirms = messagebox.askokcancel(
                "You haven't saved your data", 
                "Your latest data isn't saved yet.\nAre you sure you want to close without saving?")
            if user_confirms:
                self.destroy()

if __name__ == "__main__":
    app = MainPage()
    app.mainloop()
