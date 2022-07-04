from fpdf import FPDF
from PyPDF2 import PdfWriter


class PDF(FPDF):
    pass # nothing happens when it is executed.

    def imagex(self):
        self.set_xy(6.0,6.0)
        self.image(sctplt,  link='', type='', w=1586/80, h=1920/80)
        self.set_xy(183.0,6.0)
        self.image(sctplt2,  link='', type='', w=1586/80, h=1920/80)

    def titles(self):
        self.set_xy(0.0,0.0)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(220, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt="Wallet", border=0)

    def imagex(self):
        self.set_xy(183.0,6.0)
        self.image("logo.png",  link='', type='', w=1586/80)
        # self.image(sctplt2,  link='', type='', w=1586/80, h=1920/80)

    def line_1(self):
        self.set_xy(0.0,13.0)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(12, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)

    def line_2(self):
        self.set_xy(0.0,19.0)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(12, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)

    def line_3(self):
        self.set_xy(0.0,19.0)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(12, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt="Your multi-signature wallet enables you to backup your wallet.", border=0)


pdf = PDF(orientation='P', unit='mm', format='A4')
pdf.add_page()

pdf.titles()
pdf.line_1()
pdf.line_2()
pdf.line_3()
pdf.imagex()


pdf.output('test.pdf','F')



# writer = PdfWriter()
# writer.add_blank_page(width=200, height=200)

# data = b"any bytes - typically read from a file"
# writer.add_attachment("logo.png", data)

# with open("test.pdf", "wb") as output_stream:
#     writer.write(output_stream)