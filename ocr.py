import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import pytesseract
from PIL import Image, ImageTk

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Application")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        # Custom font
        self.custom_font = ("Segoe UI", 12)

        # Create a main frame
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        self.title_label = tk.Label(
            self.main_frame,
            text="OCR Application",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f0f0"
        )
        self.title_label.pack(pady=10)

        # Browse Image Button
        self.browse_button = tk.Button(
            self.main_frame,
            text="Browse Image",
            command=self.browse_image,
            font=self.custom_font,
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5
        )
        self.browse_button.pack(pady=10)

        # Image Display Area
        self.image_label = tk.Label(self.main_frame, bg="#f0f0f0")
        self.image_label.pack(pady=10)

        # Extracted Text Area with Scrollbar
        self.text_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=self.custom_font,
            bg="white",
            fg="black",
            height=10,
            width=60
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # Save Text Button
        self.save_button = tk.Button(
            self.main_frame,
            text="Save Text",
            command=self.save_text,
            font=self.custom_font,
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.save_button.pack(pady=10)

        # Status Bar
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            fg="#555555",
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=5)

    def browse_image(self):
        # Open a file dialog to select an image
        file_path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )

        if file_path:
            # Update status bar
            self.status_bar.config(text="Processing image...")

            # Perform OCR on the selected image
            extracted_text = self.perform_ocr(file_path)

            # Display the image
            self.display_image(file_path)

            # Display the extracted text
            self.text_widget.delete(1.0, tk.END)  # Clear previous text
            self.text_widget.insert(tk.END, extracted_text if extracted_text else "No text found")

            # Enable the "Save Text" button
            self.save_button.config(state=tk.NORMAL)

            # Update status bar
            self.status_bar.config(text="Image processed successfully")

    def perform_ocr(self, image_path):
        try:
            # Load the image using OpenCV
            image = cv2.imread(image_path)

            # Check if the image was loaded successfully
            if image is None:
                messagebox.showerror("Error", "Unable to load the image. Please check the file path.")
                return None

            # Convert the image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Perform OCR using Tesseract
            text = pytesseract.image_to_string(gray_image)

            return text
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return None

    def display_image(self, image_path):
        # Open the image using Pillow
        image = Image.open(image_path)
        image.thumbnail((400, 400))  # Resize the image to fit in the GUI

        # Convert the image to a format Tkinter can display
        tk_image = ImageTk.PhotoImage(image)

        # Update the image label
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image  # Keep a reference to avoid garbage collection

    def save_text(self):
        # Get the extracted text from the text widget
        text = self.text_widget.get(1.0, tk.END).strip()

        # Check if there is any text to save
        if text and text != "No text found":
            # Open a file dialog to save the text
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt")]
            )

            if file_path:
                # Save the text to the selected file
                with open(file_path, "w") as file:
                    file.write(text)
                messagebox.showinfo("Success", "Text saved successfully!")
                self.status_bar.config(text="Text saved successfully")
        else:
            messagebox.showwarning("No Text", "No text to save.")
            self.status_bar.config(text="No text to save")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()