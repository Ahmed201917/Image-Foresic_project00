import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import tensorflow as tf
import os

def convert_to_ela_image(path, quality):
    """Convert image to ELA"""
    temp_filename = 'temp_file_name.jpg'
    try:
        with Image.open(path) as image:
            image = image.convert('RGB')
            image.save(temp_filename, 'JPEG', quality=quality)
            
            with Image.open(temp_filename) as temp_image:
                ela_image = ImageChops.difference(image, temp_image)
                
                extrema = ela_image.getextrema()
                max_diff = max([ex[1] for ex in extrema])
                max_diff = max(1, max_diff)
                scale = 255.0 / max_diff
                
                ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
                return ela_image
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

class ForgeryDetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Forgery Detection")
        self.img_path = None
        self.model = None
        
        try:
            self.model = tf.keras.models.load_model('final_forgery_detection_model.h5')
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            messagebox.showerror("Error", "Could not load the model!")
            
        # Create main frame
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True, fill='both')
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.frame, text="Image Forgery Detection", 
                              font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Button to select image
        self.btn_select = tk.Button(self.frame, text="Select Image", 
                                  command=self.select_image,
                                  width=20,
                                  font=('Helvetica', 10))
        self.btn_select.pack(pady=10)
        
        # Label to display the selected image
        self.img_label = tk.Label(self.frame)
        self.img_label.pack(pady=10)
        
        # Button to detect forgery
        self.btn_detect = tk.Button(self.frame, text="Detect Forgery",
                                  command=self.detect_forgery,
                                  width=20,
                                  font=('Helvetica', 10))
        self.btn_detect.pack(pady=10)
        
        # Label to display result
        self.result_label = tk.Label(self.frame, text="", 
                                   font=('Helvetica', 12))
        self.result_label.pack(pady=10)
        
    def select_image(self):
        self.img_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*")
            ]
        )
        
        if self.img_path:
            # Display the selected image
            img = Image.open(self.img_path)
            # Resize image for display while maintaining aspect ratio
            display_size = (300, 300)
            img.thumbnail(display_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk
            # Clear previous result
            self.result_label.config(text="")
            
    def detect_forgery(self):
        if not self.img_path:
            messagebox.showerror("Error", "Please select an image first!")
            return
        
        if self.model is None:
            messagebox.showerror("Error", "Model not loaded!")
            return
        
        try:
            # Process image
            ela_img = convert_to_ela_image(self.img_path, 90)
            ela_img = ela_img.resize((128, 128))
            ela_array = np.array(ela_img) / 255.0
            ela_array = np.expand_dims(ela_array, axis=0)
            
            # Make prediction
            prediction = self.model.predict(ela_array, verbose=0)
            authentic_prob = prediction[0][1] * 100
            tampered_prob = prediction[0][0] * 100
            
            # Determine result
            if authentic_prob > tampered_prob:
                result = "AUTHENTIC"
                confidence = authentic_prob
                color = "green"
            else:
                result = "TAMPERED"
                confidence = tampered_prob
                color = "red"
            
            # Display result
            result_text = f"Result: {result}\nConfidence: {confidence:.2f}%"
            self.result_label.config(text=result_text, fg=color)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during detection: {str(e)}")

def main():
    root = tk.Tk()
    app = ForgeryDetectionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()