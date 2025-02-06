import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import ezdxf

# Update this path to where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path accordingly


def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    return images


def ocr_images(images):
    texts = []

    for img in images:
        text = pytesseract.image_to_string(img)
        texts.append(text)

    return texts


def extract_text_from_pdf(pdf_path):
    images = pdf_to_images(pdf_path)
    texts = ocr_images(images)
    return texts


def extract_data_from_dxf(dxf_path):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    data = []

    for entity in msp:
        if entity.dxftype() == 'LINE':
            start_point = entity.dxf.start
            end_point = entity.dxf.end
            data.append({
                'type': 'LINE',
                'start_x': start_point.x,
                'start_y': start_point.y,
                'end_x': end_point.x,
                'end_y': end_point.y
            })
        elif entity.dxftype() == 'CIRCLE':
            center = entity.dxf.center
            radius = entity.dxf.radius
            data.append({
                'type': 'CIRCLE',
                'center_x': center.x,
                'center_y': center.y,
                'radius': radius
            })

    return data
