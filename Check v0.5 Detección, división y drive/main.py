from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter

import numpy as np
import cv2
import pytesseract
from driveconnection import *



pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detectar_examenes(imagen):


    imagen_rec = imagen[90:347, 104:1570]

    gris = cv2.cvtColor(imagen_rec, cv2.COLOR_BGR2GRAY)
    binaria = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 5)
    texto = pytesseract.image_to_string(binaria)

    palabras_clave = ["salesianos", "san", "juan", "bosco", "colegio", "valencia"]
    c = 0
    for palabra in palabras_clave:
        if palabra in texto.lower():
            c += 1
    # 3 palabras clave funcionan
    if c > 2:
        return True
    return False


def dividir_pdf(ruta_pdf):
    with open(ruta_pdf, 'rb') as pdf:
        lectura_pdf = PdfReader(pdf)
        n_pages = len(lectura_pdf.pages)


        n_examen = 1
        started = False

        writer = PdfWriter()

        pdfimages = convert_from_path(ruta_pdf, poppler_path=r"C:\Users\d2574\PycharmProjects\Check\poppler-utils")

        driveupload = int(input("Save on disk = 0, Upload to drive = 1: "))

        for i in range(n_pages):

            image = np.asarray(pdfimages[i])
            if(detectar_examenes(image) and started):

                nombre_archivo = f"Alumno nº{n_examen}.pdf"
                n_examen += 1

                if(driveupload):
                    upload_pdf(writer, nombre_archivo)
                else:
                    with open(nombre_archivo, 'wb') as nuevo_pdf:
                        writer.write(nuevo_pdf)

                writer = PdfWriter()

            if(i == 0):
                started = True

            writer.add_page(lectura_pdf.pages[i])


        nombre_archivo = f"Alumno nº{n_examen}.pdf"
        if (driveupload):
            upload_pdf(writer, nombre_archivo)
        else:
            with open(nombre_archivo, 'wb') as nuevo_pdf:
                writer.write(nuevo_pdf)


ruta_pdf = r"Examenes.pdf"
dividir_pdf(ruta_pdf)

