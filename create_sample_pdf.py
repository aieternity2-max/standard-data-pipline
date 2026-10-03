from reportlab.pdfgen import canvas


output_file = "tests/fixtures/sample.pdf"

pdf = canvas.Canvas(output_file)

pdf.setTitle("Customer Data Report")

pdf.drawString(
    100,
    750,
    "Customer Data Report"
)

pdf.drawString(
    100,
    700,
    "Customer 101: Alice"
)

pdf.drawString(
    100,
    675,
    "Customer 102: Bob"
)

pdf.drawString(
    100,
    650,
    "Customer 103: Charlie"
)

pdf.drawString(
    100,
    600,
    "All customers have completed their registration."
)

pdf.save()

print("sample.pdf created successfully")