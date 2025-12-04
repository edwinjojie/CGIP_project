import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import cv2
import pytesseract
from PIL import Image, ImageTk
import fitz
import os
import time
import json

# Default path to the Tesseract executable (can be changed in Settings)
DEFAULT_TESS_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Application")
        self.root.geometry("850x600")
        self.root.configure(bg="#f7f7f9")

        # Theme
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Fonts
        self.custom_font = ("Segoe UI", 12)

        # State
        self.last_result = None
        self.settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')
        self.settings = self.load_settings()
        pytesseract.pytesseract.tesseract_cmd = self.settings.get('tesseract_path', DEFAULT_TESS_PATH)

        # Menu bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.browse_file)
        file_menu.add_command(label="Save Text", command=self.save_text)
        file_menu.add_separator()
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_command(label="Export Markdown", command=self.export_markdown)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Set Tesseract Path", command=self.set_tesseract_path)
        settings_menu.add_command(label="Save Settings", command=self.save_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "OCR Application with PDF support"))
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)

        # Main Frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        self.title_label = ttk.Label(
            self.main_frame,
            text="OCR Application",
            font=("Segoe UI", 20, "bold")
        )
        self.title_label.pack(pady=5)

        # Settings Panel
        settings_frame = ttk.Frame(self.main_frame)
        settings_frame.pack(fill=tk.X, pady=8)

        ttk.Label(settings_frame, text="Language:", font=self.custom_font).pack(side=tk.LEFT, padx=(0, 6))
        self.lang_var = tk.StringVar(value=self.settings.get('lang', 'eng'))
        self.lang_select = ttk.Combobox(settings_frame, textvariable=self.lang_var, state="readonly", width=8)
        self.lang_select["values"] = ["eng", "deu", "fra", "spa", "ita"]
        self.lang_select.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(settings_frame, text="PSM:", font=self.custom_font).pack(side=tk.LEFT, padx=(0, 6))
        self.psm_var = tk.StringVar(value=str(self.settings.get('psm', '6')))
        self.psm_select = ttk.Combobox(settings_frame, textvariable=self.psm_var, state="readonly", width=6)
        self.psm_select["values"] = ["3", "6", "11", "12"]
        self.psm_select.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(settings_frame, text="OEM:", font=self.custom_font).pack(side=tk.LEFT, padx=(0, 6))
        self.oem_var = tk.StringVar(value=str(self.settings.get('oem', '3')))
        self.oem_select = ttk.Combobox(settings_frame, textvariable=self.oem_var, state="readonly", width=6)
        self.oem_select["values"] = ["0", "1", "2", "3"]
        self.oem_select.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(settings_frame, text="Render Scale:", font=self.custom_font).pack(side=tk.LEFT, padx=(0, 6))
        self.scale_var = tk.StringVar(value=str(self.settings.get('render_scale', 2.0)))
        self.scale_entry = ttk.Entry(settings_frame, textvariable=self.scale_var, width=6)
        self.scale_entry.pack(side=tk.LEFT)

        # Toolbar
        toolbar = ttk.Frame(self.main_frame)
        toolbar.pack(fill=tk.X, pady=8)

        self.browse_button = ttk.Button(toolbar, text="Browse File", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=(0, 8))

        self.copy_button = ttk.Button(toolbar, text="Copy Text", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 8))

        self.save_button = ttk.Button(toolbar, text="Save Text", command=self.save_text, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=(0, 8))

        self.export_json_button = ttk.Button(toolbar, text="Export JSON", command=self.export_json, state=tk.DISABLED)
        self.export_json_button.pack(side=tk.LEFT, padx=(0, 8))

        self.export_md_button = ttk.Button(toolbar, text="Export Markdown", command=self.export_markdown, state=tk.DISABLED)
        self.export_md_button.pack(side=tk.LEFT)

        # Preview Area
        self.image_label = ttk.Label(self.main_frame)
        self.image_label.pack(pady=10)

        # Text Area
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            font=self.custom_font,
            bg="white",
            fg="black"
        )
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)

        # Progress Bar
        self.progress = ttk.Progressbar(self.main_frame, mode="determinate", maximum=100)
        self.progress.pack(fill=tk.X, pady=6)

        # Status Bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", font=("Segoe UI", 10))
        self.status_bar.pack(fill=tk.X, pady=4)

        # Persist settings when changed
        self.lang_select.bind("<<ComboboxSelected>>", lambda e: self.save_settings())
        self.psm_select.bind("<<ComboboxSelected>>", lambda e: self.save_settings())
        self.oem_select.bind("<<ComboboxSelected>>", lambda e: self.save_settings())
        self.scale_entry.bind("<FocusOut>", lambda e: self.save_settings())

    def load_settings(self):
        defaults = {
            'lang': 'eng',
            'psm': '6',
            'oem': '3',
            'render_scale': 2.0,
            'tesseract_path': DEFAULT_TESS_PATH,
        }
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    defaults.update(data or {})
        except Exception:
            pass
        return defaults

    def save_settings(self):
        try:
            self.settings['lang'] = self.lang_var.get()
            self.settings['psm'] = self.psm_var.get()
            self.settings['oem'] = self.oem_var.get()
            try:
                self.settings['render_scale'] = float(self.scale_var.get())
            except Exception:
                self.settings['render_scale'] = 2.0
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def set_tesseract_path(self):
        path = filedialog.askopenfilename(
            title="Select tesseract.exe",
            filetypes=[("Executable", "tesseract.exe"), ("All Files", "*.*")]
        )
        if path:
            self.settings['tesseract_path'] = path
            pytesseract.pytesseract.tesseract_cmd = path
            self.save_settings()
            messagebox.showinfo("Settings", "Tesseract path updated.")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Image or PDF",
            filetypes=[("Image/PDF Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.pdf")]
        )
        if not file_path:
            return

        self.status_bar.config(text="Processing...")
        self.progress["value"] = 0
        self.root.update_idletasks()

        start_total = time.perf_counter()
        ext = os.path.splitext(file_path)[1].lower()
        text_output = None
        pages_meta = []
        mode = ""

        if ext == ".pdf":
            self.display_pdf_preview(file_path)
            text_output, pages_meta, mode = self.perform_ocr_pdf(file_path)
        else:
            self.display_image(file_path)
            text_output, pages_meta = self.perform_ocr_image(file_path)
            mode = "image_ocr"

        end_total = time.perf_counter()
        total_ms = int((end_total - start_total) * 1000)

        if text_output is None:
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, "No text found")
            self.status_bar.config(text="Processing failed")
            return

        # Build last_result
        self.last_result = {
            "file_name": os.path.basename(file_path),
            "num_pages": len(pages_meta) if pages_meta else 1,
            "render_scale": self.settings.get('render_scale', 2.0),
            "language": self.lang_var.get(),
            "psm": int(self.psm_var.get()),
            "oem": int(self.oem_var.get()),
            "mode": mode,
            "total_time_ms": total_ms,
            "pages": pages_meta,
        }

        # Display extracted text
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text_output)

        # Enable actions
        self.save_button.config(state=tk.NORMAL)
        self.copy_button.config(state=tk.NORMAL)
        self.export_json_button.config(state=tk.NORMAL)
        self.export_md_button.config(state=tk.NORMAL)

        self.progress["value"] = 100
        self.status_bar.config(text=f"Processed in {total_ms/1000:.2f}s")
        self.root.update_idletasks()

    def get_tesseract_config(self):
        return f"--psm {self.psm_var.get()} --oem {self.oem_var.get()}"

    def perform_ocr_image(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                messagebox.showerror("Error", "Unable to load the image. Please check the file path.")
                return None, []
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            start_ocr = time.perf_counter()
            text = pytesseract.image_to_string(
                gray_image,
                lang=self.lang_var.get(),
                config=self.get_tesseract_config()
            )
            end_ocr = time.perf_counter()
            ocr_ms = int((end_ocr - start_ocr) * 1000)
            page_meta = [{
                "page_number": 1,
                "native_text_used": False,
                "render_time_ms": 0,
                "ocr_time_ms": ocr_ms,
                "text_length": len(text or ""),
            }]
            return text, page_meta
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return None, []

    def perform_ocr_pdf(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            page_texts = []
            pages_meta = []
            total_pages = len(doc)
            mode = "smart_pdf"
            scale = self.settings.get('render_scale', 2.0)
            for i, page in enumerate(doc):
                start_render = time.perf_counter()
                native = (page.get_text("text") or "").strip()
                render_ms = 0
                ocr_ms = 0
                native_used = False
                text = ""
                if native:
                    native_used = True
                    text = native
                else:
                    matrix = fitz.Matrix(scale, scale)
                    pix = page.get_pixmap(matrix=matrix, alpha=False)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    end_render = time.perf_counter()
                    render_ms = int((end_render - start_render) * 1000)

                    start_ocr = time.perf_counter()
                    text = pytesseract.image_to_string(
                        img,
                        lang=self.lang_var.get(),
                        config=self.get_tesseract_config()
                    )
                    end_ocr = time.perf_counter()
                    ocr_ms = int((end_ocr - start_ocr) * 1000)

                if native_used:
                    end_render = time.perf_counter()
                    render_ms = int((end_render - start_render) * 1000)

                page_texts.append(text.strip())
                pages_meta.append({
                    "page_number": i + 1,
                    "native_text_used": native_used,
                    "render_time_ms": render_ms,
                    "ocr_time_ms": ocr_ms,
                    "text_length": len(text or ""),
                })

                pct = int(((i + 1) / max(total_pages, 1)) * 100)
                self.progress["value"] = pct
                self.root.update_idletasks()

            doc.close()

            # Combined text with page separators
            combined = []
            for idx, t in enumerate(page_texts, start=1):
                combined.append(f"--- Page {idx} ---\n{t}\n")
            return "\n".join(combined).strip(), pages_meta, mode
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process PDF: {e}")
            return None, [], "pdf_error"

    def display_image(self, image_path):
        image = Image.open(image_path)
        image.thumbnail((500, 500))
        tk_image = ImageTk.PhotoImage(image)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

    def display_pdf_preview(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                doc.close()
                return
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(self.settings.get('render_scale', 2.0), self.settings.get('render_scale', 2.0)), alpha=False)
            doc.close()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((500, 500))
            tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image
        except Exception:
            pass

    def save_text(self):
        text = self.text_widget.get(1.0, tk.END).strip()
        if not text or text == "No text found":
            messagebox.showwarning("No Text", "No text to save.")
            self.status_bar.config(text="No text to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Success", "Text saved successfully!")
            self.status_bar.config(text="Text saved successfully")

    def export_json(self):
        if not self.last_result:
            messagebox.showwarning("No Data", "Nothing to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.last_result, f, indent=2)
            self.status_bar.config(text="JSON exported")

    def export_markdown(self):
        if not self.last_result:
            messagebox.showwarning("No Data", "Nothing to export.")
            return
        r = self.last_result
        lines = []
        lines.append(f"# OCR Report: {r['file_name']}")
        lines.append("")
        lines.append(f"- Pages: {r['num_pages']}")
        lines.append(f"- Language: {r['language']}")
        lines.append(f"- PSM: {r['psm']}")
        lines.append(f"- OEM: {r['oem']}")
        lines.append(f"- Mode: {r['mode']}")
        lines.append(f"- Render scale: {r['render_scale']}")
        lines.append(f"- Total time: {r['total_time_ms'] / 1000:.2f}s")
        lines.append("")
        # Include per-page sections
        text = self.text_widget.get(1.0, tk.END).strip()
        per_page_texts = text.split("--- Page ") if r['mode'] != 'image_ocr' else [text]
        if r['mode'] == 'image_ocr':
            lines.append(f"## Page 1 (OCR {r['pages'][0]['ocr_time_ms']}ms)")
            lines.append(text)
        else:
            # Reconstruct with metadata
            for p in r['pages']:
                idx = p['page_number']
                header = f"## Page {idx}"
                if p['native_text_used']:
                    header += " (native text)"
                else:
                    header += f" (render {p['render_time_ms']}ms, OCR {p['ocr_time_ms']}ms)"
                lines.append(header)
                # Find corresponding text by simple delimiter match
                # per_page_texts[0] may be preamble from split; safer to get from last_result? For simplicity, extract from text_widget by delimiter
                # We'll search for the section
                start_marker = f"--- Page {idx} ---"
                section = ""
                if start_marker in text:
                    start = text.find(start_marker)
                    end_marker = f"--- Page {idx+1} ---"
                    end = text.find(end_marker, start + len(start_marker))
                    section = text[start + len(start_marker): end if end != -1 else None].strip()
                lines.append(section)
        md = "\n".join(lines)
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md)
            self.status_bar.config(text="Markdown exported")

    def copy_to_clipboard(self):
        text = self.text_widget.get(1.0, tk.END).strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_bar.config(text="Text copied to clipboard")


if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()