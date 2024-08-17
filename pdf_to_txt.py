"""Handle conversions from .pdf to text format."""

import pdftotext
from io import StringIO


def pdf_to_txt(script_path, destination_dir="test_files/test_txt"):
    """.pdf to .txt file"""
    movie = "_".join(script_path.split("/")[-1].split(".")[:-1])
    with open(script_path, "rb") as f:
        pdf = pdftotext.PDF(f, physical=True)

    with open(f'{destination_dir}/{movie}.txt', 'w', encoding='utf-8') as f:
        for page in pdf:
            for line in page.split('\n'):
                f.write(line)
                f.write("\n\n")


def pdf_to_text_buffer(pdf):
    """.pdf to text in buffer"""
    buffer = StringIO()
    for page in pdf:
        for line in page.split("\n"):
            buffer.write(line)
            buffer.write("\n\n")
    buffer.seek(0)
    return buffer


def txt_to_text_buffer(txt):
    """.txt file to text in buffer"""
    with open(txt, "r", encoding="utf-8") as f:
        script = f.read()
    buffer = StringIO(script)
    buffer.seek(0)
    return buffer

