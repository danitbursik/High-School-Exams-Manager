from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter

import numpy as np
import cv2
import pytesseract
from driveconnection import *

import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detectar_examenes(imagen, check_tema : bool):

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
        if (check_tema):
            return cutting_strings('TEMA', '\n', texto, 1)
        return True
    return False

def cutting_strings(start_mark, end_mark, text, include_start_mark):
    start_idx = text.find(start_mark)
    end_idx = text.find(end_mark, start_idx)
    if(include_start_mark):
        return text[start_idx : end_idx]
    else:
        return text[start_idx + len(start_mark) : end_idx]



def dividir_pdf(ruta_pdf, folder_name):
    with open(ruta_pdf, 'rb') as pdf:
        lectura_pdf = PdfReader(pdf)
        n_pages = len(lectura_pdf.pages)
        pdfimages = convert_from_path(ruta_pdf, poppler_path=r"C:\Users\d2574\PycharmProjects\Check\poppler-utils")
        writer = PdfWriter()
        #drive or disk
        driveupload = 1

        if(driveupload):
            drive_cutting_pdf(pdfimages, n_pages, writer, lectura_pdf, folder_name)
        else:
            ondisk_cutting_pdf(pdfimages, n_pages, writer, lectura_pdf)




#cutting pdf for drive func
def drive_cutting_pdf(pdfimages, n_pages, writer, lectura_pdf, folder_name):

    started = False
    n_examen = 1
    service = service_building()

    writer.add_page(lectura_pdf.pages[0])

    parent_folder = search_folder(folder_name, service)
    folder_name = detectar_examenes(np.asarray(pdfimages[0]), 1)
    if(parent_folder):
        folder = create_folder(folder_name, parent_folder, service)
    else:
        folder = create_folder(folder_name, "", service)

    for i in range(1, n_pages):

        image = np.asarray(pdfimages[i])

        if(detectar_examenes(image, 0)):
            nombre_archivo = f"Alumno nº{n_examen}.pdf"
            n_examen += 1
            upload_pdf(writer, nombre_archivo, service, folder)
            writer = PdfWriter()

        writer.add_page(lectura_pdf.pages[i])

    nombre_archivo = f"Alumno nº{n_examen}.pdf"
    upload_pdf(writer, nombre_archivo, service, folder)

#cutting pdf to save it on disk func
def ondisk_cutting_pdf(pdfimages, n_pages, writer, lectura_pdf):

    started = False
    n_examen = 1

    for i in range(n_pages):

        image = np.asarray(pdfimages[i])
        if not started:
            started = True
        elif (detectar_examenes(image, 0) and started):

            nombre_archivo = f"Alumno nº{n_examen}.pdf"
            n_examen += 1
            with open(nombre_archivo, 'wb') as nuevo_pdf:
                writer.write(nuevo_pdf)

            writer = PdfWriter()
        writer.add_page(lectura_pdf.pages[i])

    nombre_archivo = f"Alumno nº{n_examen}.pdf"

    with open(nombre_archivo, 'wb') as nuevo_pdf:
        writer.write(nuevo_pdf)

inicio = datetime.datetime.now()
ruta_pdf = r"Examenes.pdf"
dividir_pdf(ruta_pdf, "1 BACH MAT")
print(datetime.datetime.now() - inicio)
