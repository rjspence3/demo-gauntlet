from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Slide 1
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "Project Phoenix: Cloud Migration Strategy")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Objective: Migrate legacy on-premise infrastructure to AWS.")
    c.drawString(100, 630, "Key Benefits: Scalability, Cost Reduction, Security.")
    c.showPage()

    # Slide 2
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "Cost Analysis")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Current Spend: $1.2M/year")
    c.drawString(100, 630, "Projected Spend: $800k/year")
    c.drawString(100, 610, "ROI: 18 months")
    c.showPage()

    # Slide 3
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "Security & Compliance")
    c.setFont("Helvetica", 12)
    c.drawString(100, 650, "Compliance: SOC2, HIPAA")
    c.drawString(100, 630, "Security: Zero Trust Architecture, IAM integration.")
    c.showPage()

    c.save()

if __name__ == "__main__":
    create_pdf("sample_deck.pdf")
