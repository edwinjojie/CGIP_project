# OCR Application

A robust desktop application for Optical Character Recognition (OCR) built with Python. This tool allows you to extract text from images and PDF files with a user-friendly graphical interface.

## Features

- **Image OCR**: Extract text from various image formats (JPG, PNG, BMP, TIFF, etc.).
- **PDF Support**: Process PDF files to extract text.
  - Smart detection: Extracts native text if available.
  - Fallback OCR: Renders PDF pages as images for OCR if native text is missing.
- **Configurable OCR Settings**:
  - **Language**: Support for multiple languages (eng, deu, fra, spa, ita).
  - **PSM (Page Segmentation Mode)**: Adjust how Tesseract treats the page structure.
  - **OEM (OCR Engine Mode)**: Choose the OCR engine mode.
- **Export Options**: Save extracted text as `.txt`, `.json`, or `.md` (Markdown).
- **Clipboard Integration**: Quickly copy extracted text to the clipboard.
- **Persistent Settings**: Your configuration preferences are saved automatically.

## Prerequisites

### 1. Python Dependencies
You need to install the required Python libraries. You can install them using pip:

```bash
pip install opencv-python pytesseract Pillow pymupdf
```

*Note: `tkinter` is usually included with standard Python installations.*

### 2. Tesseract-OCR Engine
This application requires the Tesseract-OCR engine to be installed on your system.

- **Windows**: Download and install the Tesseract installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
- **Linux**: Install via package manager (e.g., `sudo apt-get install tesseract-ocr`).
- **macOS**: Install via Homebrew (`brew install tesseract`).

**Important**: After installation, make sure to set the correct path to the `tesseract.exe` file within the application settings if it's not in the default location (`C:\Program Files\Tesseract-OCR\tesseract.exe`).

## Usage

1.  **Run the Application**:
    ```bash
    python ocr.py
    ```

2.  **Load a File**:
    - Click **File > Open...** or the **Browse File** button.
    - Select an image or PDF file.

3.  **View Results**:
    - The application will process the file and display the extracted text in the main text area.
    - A preview of the image or PDF page will be shown on the left (or top depending on layout).

4.  **Export/Save**:
    - Use the **Save Text**, **Export JSON**, or **Export Markdown** buttons to save your results.

5.  **Settings**:
    - Adjust OCR parameters (Language, PSM, OEM) using the dropdowns in the settings panel.
    - Change the Tesseract executable path via **Settings > Set Tesseract Path**.

## Configuration

The application saves your preferences in a `settings.json` file in the same directory. This includes:
- Selected Language
- PSM and OEM modes
- Render scale for PDF processing
- Path to the Tesseract executable

## License

This project is licensed under the terms specified in the `LICENSE` file.
