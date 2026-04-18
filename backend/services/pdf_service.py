from fpdf import FPDF
import os
from datetime import datetime


def generate_bill_pdf(farmer, bill_data: dict, month: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(34, 139, 34)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 15, "  Smart Dairy Farming System", fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 14)
    pdf.ln(5)
    pdf.cell(0, 10, "MILK COLLECTION BILL", align="C", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", ln=True)
    pdf.ln(5)

    # Farmer Info
    pdf.set_fill_color(240, 248, 240)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "FARMER DETAILS", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 7, "Farmer Name:")
    pdf.cell(0, 7, farmer.name, ln=True)
    pdf.cell(60, 7, "Email:")
    pdf.cell(0, 7, farmer.email, ln=True)
    pdf.cell(60, 7, "Billing Month:")
    pdf.cell(0, 7, month, ln=True)
    pdf.ln(5)

    # Breakdown Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(240, 248, 240)
    pdf.cell(0, 8, "COLLECTION BREAKDOWN", fill=True, ln=True)
    pdf.ln(2)

    # Table headers
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(200, 230, 200)
    pdf.cell(40, 8, "Date", border=1, fill=True)
    pdf.cell(35, 8, "Liters", border=1, fill=True)
    pdf.cell(35, 8, "Quality", border=1, fill=True)
    pdf.cell(35, 8, "Rate/Liter", border=1, fill=True)
    pdf.cell(35, 8, "Amount", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    for row in bill_data["breakdown"]:
        pdf.cell(40, 7, str(row["date"]), border=1)
        pdf.cell(35, 7, f"{row['liters']:.2f} L", border=1)
        pdf.cell(35, 7, row["quality"], border=1)
        pdf.cell(35, 7, f"Rs. {row['rate']:.2f}", border=1)
        pdf.cell(35, 7, f"Rs. {row['amount']:.2f}", border=1, ln=True)

    # Total
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(34, 139, 34)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 9, "TOTAL LITERS", border=1, fill=True)
    pdf.cell(0, 9, f"{bill_data['total_liters']:.2f} L", border=1, fill=True, ln=True)
    pdf.cell(110, 9, "TOTAL AMOUNT", border=1, fill=True)
    pdf.cell(0, 9, f"Rs. {bill_data['total_amount']:.2f}", border=1, fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "Thank you for your contribution to our dairy farm.", align="C", ln=True)

    # Save file
    os.makedirs("uploads/bills", exist_ok=True)
    filename = f"uploads/bills/bill_{farmer.id}_{month}.pdf"
    pdf.output(filename)
    return filename
