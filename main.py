# ImageWatermarker Project
# Christina Rost
# February 2024

import tkinter as tk
from functools import partial
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk


OFFSET = 100
NAME_WATERMARK = 'watermark'
NAME_PHOTO = 'photo'


def save_image(watermarked_image, output_path):
    save_path = filedialog.asksaveasfilename(
        initialdir=output_path,
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")])
    watermarked_image.save(save_path)


class WatermarkApp(tk.Tk):
    description = "Select a picture and a watermark to combine.\n\n"\
                  "The watermark will be added to the bottom right corner of the picture.\n" \
                  "Use PNG file with transparent background and matching foreground color as watermark. \n" \
                  "the picture will be saved as a copy to prevent any data loss"

    def __init__(self):
        super().__init__()

        self.description_label = None
        self.combine_button = None
        self.canvas = None
        self.save_button = None
        self.icon_button = None
        self.photo_button = None
        self.watermark_label = None
        self.watermark_photo_image = None
        self.photo_label_text = None
        self.photo_label = None
        self.watermark = None
        self.photo = None
        self.photo_image = None
        self.title("Watermark App")
        self.geometry("600x600")

        self.create_widgets()


    def create_widgets(self):
        # Placeholder for the picture
        self.photo = Image.new("RGB", (400, 300), "white")
        self.photo_image = ImageTk.PhotoImage(self.photo)
        self.photo_label = tk.Label(self, image=self.photo_image)
        self.photo_label.pack()

        self.description_label = tk.Label(self, text=self.description)
        self.description_label.pack()


        # Buttons
        self.photo_button = tk.Button(
            self,
            text="Select Photo",
            command=partial(self.select_image, NAME_PHOTO)
        )
        self.photo_button.pack()

        self.icon_button = tk.Button(
            self,
            text="Select Watermark",
            command=partial(self.select_image, NAME_WATERMARK)
        )
        self.icon_button.pack()

        self.save_button = tk.Button(self, text="Save as copy", command=self.combine)
        self.save_button.pack()

        # Canvas for displaying the photo with the watermark
        self.canvas = tk.Canvas(self, width=400, height=600)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)


    def select_image(self, name: str):
        photo_path = "/Users/cr/Pictures/!READY_4Web/Aurora"
        watermark_path = "/Users/cr/Pictures/unterschrift"
        open_at = photo_path if name == NAME_PHOTO else watermark_path

        types = [("PNG files", "*.png")] if name == NAME_WATERMARK \
            else [("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("GIF files", "*.gif"), ("Bitmap files", "*.bmp")]
        try:
            file_path = filedialog.askopenfilename(
                initialdir=open_at,
                filetypes=types
            )
            print(file_path)
            if file_path:
                setattr(self, name+"_path", file_path)
        except Exception as e:
            print(f"Error selecting {name}: {e}")
        finally:
            self.display_image(name)

    def display_image(self, name):
        file_path = getattr(self, name + "_path", None)
        size = (400, 300) if name == NAME_PHOTO else (40, 30)
        if file_path:
            print("displaying photo")
            photo = Image.open(file_path)
            photo = photo.resize(size, Image.BICUBIC)
            if name == "watermark":
                x = 400 - 40 - 10
                y = 300 - 30 - 10
                self.photo.paste(photo, (x, y))
            else:
                self.photo = photo

            self.photo_image = ImageTk.PhotoImage(self.photo)
            try:
                self.photo_label.config(image=self.photo_image)
            except Exception as e:
                print(f"Error displaying {name}:\n{e.with_traceback()}")
            self.photo_label.photo_image = self.photo_image




    def combine(self):
        print("combinin pictures")
        print(f"watermark path: {self.watermark_path}" )
        photo = Image.open(self.photo_path)
        watermark = Image.open(self.watermark_path)


        mwidth = int(photo.width * 0.05)
        ratio = watermark.width / watermark.height

        height = int(mwidth) * int(ratio)
        watermark = watermark.resize((mwidth, height))

        print("shape watermark")
        print(watermark.size)
        print("shape image")
        print(photo.size)

        # Convert watermark to RGB if it's single-layered
        if watermark.mode != "RGB":
            watermark = watermark.convert("RGB")

        path_file, extension = self.photo_path.split(".")
        output_path = f"{path_file}_watermarked.{extension}"

        photo_array = np.array(photo.getdata(), dtype=np.uint8).reshape(photo.size[1], photo.size[0], 3)
        try:
            watermark_array = np.array(watermark.getdata(), dtype=np.uint8).reshape(watermark.size[1],
                                                                                    watermark.size[0], 3)
        except ValueError:
            watermark_array = np.array(watermark.getdata(), dtype=np.uint8).reshape(watermark.size[1],
                                                                                    watermark.size[0])




        # Calculate position to place watermark (e.g., bottom-right corner)
        x1 = photo_array.shape[1] - watermark_array.shape[1] - OFFSET
        y1 = photo_array.shape[0] - watermark_array.shape[0] - OFFSET

        x2 = x1 + mwidth
        y2 = y1 + height

        print("offsets x, y:")
        print(f"{x1}, {y1}")

        # Blend watermark with photo
        photo_array[y1:y2, x1:x2, :] += watermark_array

        # Convert back to PIL image
        watermarked_image = Image.fromarray(photo_array)

        save_image(watermarked_image, output_path)




    def on_drag_start(self, event):
        self.drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_motion(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas.move(self.drag_data["item"], delta_x, delta_y)
        self.watermark_x += delta_x
        self.watermark_y += delta_y
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y


if __name__ == "__main__":
    app = WatermarkApp()
    app.mainloop()

