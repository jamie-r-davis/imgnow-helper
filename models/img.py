from PIL import Image
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from io import StringIO
from PyPDF2 import PdfFileMerger
import os


def TIFFS2PDF(tiffs, outname):
    print('Compiling {} ({} pages)'.format(outname, len(tiffs)))
    c = Canvas(outname)
    for tiff in tiffs:
        bn = os.path.basename(tiff)
        im = Image.open(tiff)
        if im.width > im.height:
            orientation = 'landscape'  # landscape
            width, height = 11*inch, 8.5*inch
        else:
            orientation = 'portrait'
            width, height = 8.5*inch, 11*inch  #portrait
        print('  Adding {}: {}x{} ({})...'.format(bn, im.width, im.height, orientation))
        im.thumbnail([1400,1400])
        tiff_img = ImageReader(im)

        c.setPageSize((width, height))
        c.drawImage(tiff_img, 0, 0, width, height, preserveAspectRatio=True)
        c.showPage()
    c.save()


def MergePDFs(pdfs, outname):
    print('Compiling {} ({} pages)'.format(outname, len(pdfs)))
    merger = PdfFileMerger()
    for pdf in pdfs:
        bn = os.path.basename(pdf)
        print('  Adding {}...'.format(pdf))
        merger.append(bn, import_bookmarks=False)
    merger.write(outname)
