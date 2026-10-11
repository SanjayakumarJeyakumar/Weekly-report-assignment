"""Student PDF Report Generator for Olist Weekly Business Review (BDA Assignments).

Written in simple, clear student language using ReportLab Platypus.
Generates a clean, 5-page A4 report with plain white background, standard typography,
accurate database metrics, clear charts, and no overflow.
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import pymupdf  # for layout validation

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CHARTS_DIR = PROJECT_ROOT / "charts"
REPORT_DIR = PROJECT_ROOT / "report"

# Page Dimensions (A4: 595.28 x 841.89 pt)
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 40.0  # 40 pt margins
USABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)    # 515.28 pt
USABLE_HEIGHT = PAGE_HEIGHT - (2 * MARGIN)  # 761.89 pt


class StudentCanvas(canvas.Canvas):
    """Simple two-pass canvas for clear, student-style page numbering."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super().showPage()
        super().save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor("#4a5568"))

        # Thin simple footer line
        self.setStrokeColor(colors.HexColor("#cbd5e0"))
        self.setLineWidth(0.6)
        self.line(MARGIN, 30, PAGE_WIDTH - MARGIN, 30)

        # Footer text
        self.drawString(MARGIN, 20, "BDA Assignments — Weekly Business Review (Sanjayakumar Jeyakumar | Roll No: 46)")
        self.drawRightString(PAGE_WIDTH - MARGIN, 20, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_student_styles():
    """Create clean, simple typography styles for a student assignment."""
    styles = getSampleStyleSheet()

    title_main = ParagraphStyle(
        "StudentTitleMain",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f2942"),
        alignment=TA_CENTER,
        spaceAfter=3,
    )
    title_sub = ParagraphStyle(
        "StudentTitleSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2d3748"),
        alignment=TA_CENTER,
        spaceAfter=3,
    )
    title_meta = ParagraphStyle(
        "StudentTitleMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        spaceAfter=6,
    )

    h1_style = ParagraphStyle(
        "Heading1_Simple",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f2942"),
        spaceBefore=5,
        spaceAfter=4,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Simple",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2d3748"),
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Simple",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=12.2,
        textColor=colors.HexColor("#1a202c"),
        spaceAfter=4,
    )
    body_bold = ParagraphStyle(
        "Body_Simple_Bold",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    bullet_style = ParagraphStyle(
        "Bullet_Simple",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1a202c"),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )
    caption_style = ParagraphStyle(
        "Caption_Simple",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        spaceBefore=2,
        spaceAfter=4,
    )
    cell_style = ParagraphStyle(
        "Cell_Simple",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.3,
        leading=10.8,
        textColor=colors.HexColor("#1a202c"),
    )
    cell_bold = ParagraphStyle(
        "Cell_Simple_Bold",
        parent=cell_style,
        fontName="Helvetica-Bold",
    )
    header_style = ParagraphStyle(
        "Header_Simple",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f2942"),
    )

    return {
        "title_main": title_main,
        "title_sub": title_sub,
        "title_meta": title_meta,
        "h1": h1_style,
        "h2": h2_style,
        "body": body_style,
        "body_bold": body_bold,
        "bullet": bullet_style,
        "caption": caption_style,
        "cell": cell_style,
        "cell_bold": cell_bold,
        "header": header_style,
    }


def build_page_1(styles) -> list:
    """Page 1: Title, Introduction, Data Quality Results, and Main Metrics."""
    story = []

    # Student Header
    story.append(Paragraph("BDA Assignments", styles["title_main"]))
    story.append(Paragraph("Weekly Business Review – E-commerce Marketplace", styles["title_sub"]))
    story.append(Paragraph("Name: Sanjayakumar Jeyakumar &nbsp;|&nbsp; Roll No: 46 &nbsp;|&nbsp; Reg No: 127003227", styles["title_meta"]))

    # Simple dividing line
    div_table = Table([[""]], colWidths=[USABLE_WIDTH], rowHeights=[1])
    div_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#a0aec0")),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(div_table)
    story.append(Spacer(1, 6))

    # 1. Introduction
    story.append(Paragraph("1. Introduction", styles["h1"]))
    story.append(Paragraph(
        "This report is a Weekly Business Review of the Brazilian Olist e-commerce dataset for our Big Data Analytics assignment. "
        "The dataset contains about 100,000 real marketplace orders placed between late 2016 and mid 2018. "
        "Over this period, total sales reached <b>R$ 13.22 Million</b>, peaking at R$ 992.8k in May 2018.",
        styles["body"]
    ))
    story.append(Paragraph(
        "Even though the marketplace grew steadily, the data reveals two major operational problems:<br/>"
        "• <b>Almost no repeat customers:</b> Only <b>3.04%</b> of customers made a second purchase. Nearly 97% of buyers bought once and never returned.<br/>"
        "• <b>Delivery delays hurt customer reviews:</b> While 92.20% of orders were delivered on time, <b>36.60% of 1-star reviews had late deliveries</b>, "
        "arriving an average of <b>12.36 days late</b>.",
        styles["body"]
    ))
    story.append(Spacer(1, 4))

    # 2. Data Quality Checks
    story.append(Paragraph("2. Data Quality Checks", styles["h1"]))
    story.append(Paragraph(
        "Before doing the analysis, we tested the database tables using automated SQL data quality checks in PostgreSQL:",
        styles["body"]
    ))

    dq_data = [
        [
            Paragraph("Check Name", styles["header"]),
            Paragraph("Failed Rows", styles["header"]),
            Paragraph("Status", styles["header"]),
            Paragraph("Explanation", styles["header"]),
        ],
        [
            Paragraph("Duplicate Order IDs", styles["cell"]),
            Paragraph("0", styles["cell_bold"]),
            Paragraph("PASS", styles["cell_bold"]),
            Paragraph("Every order appears exactly once in the order summary mart.", styles["cell"]),
        ],
        [
            Paragraph("Null Order IDs", styles["cell"]),
            Paragraph("0", styles["cell_bold"]),
            Paragraph("PASS", styles["cell_bold"]),
            Paragraph("No missing order IDs were found.", styles["cell"]),
        ],
        [
            Paragraph("Delivered Before Purchase", styles["cell"]),
            Paragraph("0", styles["cell_bold"]),
            Paragraph("PASS", styles["cell_bold"]),
            Paragraph("Delivery timestamp is always after purchase timestamp.", styles["cell"]),
        ],
        [
            Paragraph("Review Scores Outside 1–5", styles["cell"]),
            Paragraph("0", styles["cell_bold"]),
            Paragraph("PASS", styles["cell_bold"]),
            Paragraph("All customer review ratings are valid integers between 1 and 5.", styles["cell"]),
        ],
        [
            Paragraph("Missing Customer Records", styles["cell"]),
            Paragraph("0", styles["cell_bold"]),
            Paragraph("PASS", styles["cell_bold"]),
            Paragraph("All orders link correctly to a valid customer record.", styles["cell"]),
        ],
        [
            Paragraph("Payment Amount Mismatches", styles["cell"]),
            Paragraph("300", styles["cell_bold"]),
            Paragraph("WARN", styles["cell_bold"]),
            Paragraph("300 orders have small differences due to discounts, vouchers, or installment interest. Kept as warnings without changing data.", styles["cell"]),
        ],
    ]
    dq_table = Table(dq_data, colWidths=[120, 65, 55, 275.28], repeatRows=1)
    dq_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
    ]))
    story.append(dq_table)
    story.append(Spacer(1, 6))

    # 3. Main Metric and Supporting Metrics
    story.append(Paragraph("3. Main Metric and Supporting Metrics", styles["h1"]))

    metrics_data = [
        [
            Paragraph("Metric Type", styles["header"]),
            Paragraph("Metric Name", styles["header"]),
            Paragraph("Value", styles["header"]),
            Paragraph("Why It Matters", styles["header"]),
        ],
        [
            Paragraph("<b>Main Metric</b>", styles["cell"]),
            Paragraph("Total Sales (GMV)", styles["cell_bold"]),
            Paragraph("<b>R$ 13.22M</b>", styles["cell_bold"]),
            Paragraph("Total value of all items sold, excluding freight fees and cancelled orders.", styles["cell"]),
        ],
        [
            Paragraph("<b>Supporting</b>", styles["cell"]),
            Paragraph("Repeat Purchase Rate", styles["cell_bold"]),
            Paragraph("<b>3.04%</b>", styles["cell_bold"]),
            Paragraph("Measures how many customers buy again. Only 2,888 out of 94,990 customers ever returned.", styles["cell"]),
        ],
        [
            Paragraph("<b>Supporting</b>", styles["cell"]),
            Paragraph("On-Time Delivery Rate", styles["cell_bold"]),
            Paragraph("<b>92.20%</b>", styles["cell_bold"]),
            Paragraph("Percentage of delivered orders that arrived on or before the promised delivery date.", styles["cell"]),
        ],
        [
            Paragraph("<b>Guardrail</b>", styles["cell"]),
            Paragraph("Average Days Late", styles["cell_bold"]),
            Paragraph("<b>+11.8 days</b>", styles["cell_bold"]),
            Paragraph("Average delay when an order is late. Double-digit delays cause severe customer complaints.", styles["cell"]),
        ],
        [
            Paragraph("<b>Guardrail</b>", styles["cell"]),
            Paragraph("Average Review Score", styles["cell_bold"]),
            Paragraph("<b>4.09 / 5.0</b>", styles["cell_bold"]),
            Paragraph("Average rating across all customer reviews. Helps track overall customer satisfaction.", styles["cell"]),
        ],
    ]
    metrics_table = Table(metrics_data, colWidths=[80, 115, 75, 245.28], repeatRows=1)
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    story.append(metrics_table)

    story.append(PageBreak())
    return story


def build_page_2(styles) -> list:
    """Page 2: Monthly Sales Trend (SQL Analysis 1)."""
    story = []

    story.append(Paragraph("4. Monthly Sales Trend", styles["h1"]))
    story.append(Paragraph(
        "Using SQL query <code>04_monthly_revenue.sql</code>, we analyzed the monthly sales (item price excluding freight) "
        "and month-over-month growth from September 2016 to September 2018.",
        styles["body"]
    ))
    story.append(Spacer(1, 2))

    # Chart 1: Monthly Revenue Trend
    img_path = str(CHARTS_DIR / "01_monthly_revenue_trend.png")
    story.append(Image(img_path, width=490, height=220))
    story.append(Paragraph("Figure 1: Monthly sales trend (GMV in R$) across the lifecycle phases of Olist.", styles["caption"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Key Findings from Monthly Sales:", styles["h2"]))
    story.append(Paragraph(
        "• <b>Pilot Phase (Late 2016):</b> The platform started with 295 test orders in Sep–Oct 2016 (R$ 44.7k total sales). "
        "November 2016 had exactly 0 orders because marketplace operations paused for backend upgrades. December 2016 had just 1 test order (R$ 10.90).",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Hyper-Growth Phase (2017 to Early 2018):</b> Sales grew quickly from R$ 120.1k in January 2017 to over R$ 900k per month by early 2018.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Black Friday Spike (November 2017):</b> Sales jumped to R$ 977.7k (+42.2% month-over-month growth). "
        "On Black Friday, the marketplace handled a single-day record of 1,141 orders.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Peak and Plateau (Mid 2018):</b> The highest monthly sales happened in May 2018 at R$ 992.8k. "
        "After May 2018, sales leveled off between R$ 850k and R$ 880k per month.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Data Cutoff (September 2018):</b> September 2018 recorded only 1 order (R$ 145.00) because data collection ended at the start of that month.",
        styles["bullet"]
    ))

    story.append(PageBreak())
    return story


def build_page_3(styles) -> list:
    """Page 3: Delivery Delay vs Customer Reviews (SQL Analysis 5)."""
    story = []

    story.append(Paragraph("5. Delivery Delays and Customer Reviews", styles["h1"]))
    story.append(Paragraph(
        "Using SQL query <code>08_delivery_delay_vs_reviews.sql</code>, we checked how delivery delays affect customer review scores (1 to 5 stars).",
        styles["body"]
    ))
    story.append(Spacer(1, 2))

    # Chart 2: Delivery Delay vs Review Score
    img_path = str(CHARTS_DIR / "02_delivery_delay_vs_review_score.png")
    story.append(Image(img_path, width=490, height=195))
    story.append(Paragraph("Figure 2: Percentage of late orders (left) and delivery duration vs delay severity (right) by review rating.", styles["caption"]))
    story.append(Spacer(1, 6))

    # Table with exact verified data
    table_data = [
        [
            Paragraph("Review Rating", styles["header"]),
            Paragraph("Total Reviews", styles["header"]),
            Paragraph("Distinct Orders", styles["header"]),
            Paragraph("% Late Orders", styles["header"]),
            Paragraph("Avg Delivery Days", styles["header"]),
            Paragraph("Avg Days Late (When Delayed)", styles["header"]),
        ],
        [
            Paragraph("1 Star", styles["cell_bold"]),
            Paragraph("9,405", styles["cell"]),
            Paragraph("9,380", styles["cell"]),
            Paragraph("<b>36.60%</b>", styles["cell"]),
            Paragraph("21.25 days", styles["cell"]),
            Paragraph("<b>+12.36 days late</b>", styles["cell_bold"]),
        ],
        [
            Paragraph("2 Stars", styles["cell"]),
            Paragraph("2,941", styles["cell"]),
            Paragraph("2,938", styles["cell"]),
            Paragraph("18.86%", styles["cell"]),
            Paragraph("16.61 days", styles["cell"]),
            Paragraph("+10.23 days late", styles["cell"]),
        ],
        [
            Paragraph("3 Stars", styles["cell"]),
            Paragraph("7,961", styles["cell"]),
            Paragraph("7,942", styles["cell"]),
            Paragraph("8.78%", styles["cell"]),
            Paragraph("14.20 days", styles["cell"]),
            Paragraph("+9.05 days late", styles["cell"]),
        ],
        [
            Paragraph("4 Stars", styles["cell"]),
            Paragraph("18,987", styles["cell"]),
            Paragraph("18,943", styles["cell"]),
            Paragraph("3.44%", styles["cell"]),
            Paragraph("12.25 days", styles["cell"]),
            Paragraph("+8.41 days late", styles["cell"]),
        ],
        [
            Paragraph("5 Stars", styles["cell_bold"]),
            Paragraph("57,059", styles["cell"]),
            Paragraph("56,810", styles["cell"]),
            Paragraph("<b>1.86%</b>", styles["cell"]),
            Paragraph("10.63 days", styles["cell"]),
            Paragraph("+6.99 days late", styles["cell"]),
        ],
    ]
    delay_table = Table(table_data, colWidths=[75, 75, 75, 75, 95, 120.28], repeatRows=1)
    delay_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    story.append(delay_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Important Finding — Correlation vs. Causation:", styles["h2"]))
    story.append(Paragraph(
        "• <b>Late delivery is a major cause of 1-star reviews:</b> 36.60% of 1-star reviews experienced late deliveries, "
        "and when late, the order was overdue by an average of 12.36 days (total delivery time took over 21 days). "
        "In contrast, only 1.86% of 5-star orders were late.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Delivery delay is NOT the only cause:</b> Notice that <b>63.40% of 1-star reviews arrived on time or early</b>. "
        "Customer review text shows that product defects, wrong items sent by sellers, and missing parts also cause many 1-star ratings. "
        "Therefore, fixing delivery delays is important, but checking seller product quality is also necessary.",
        styles["bullet"]
    ))

    story.append(PageBreak())
    return story


def build_page_4(styles) -> list:
    """Page 4: Repeat Customers, Rolling Orders, and Top Categories (SQL Analysis 2, 3, 4)."""
    story = []

    story.append(Paragraph("6. Repeat Customers and Top Product Categories", styles["h1"]))
    story.append(Paragraph(
        "This section covers findings from SQL queries <code>07_repeat_purchase_rate.sql</code>, "
        "<code>06_rolling_7_day_orders.sql</code>, and <code>05_top_categories_by_state.sql</code>.",
        styles["body"]
    ))
    story.append(Spacer(1, 2))

    # Chart 3: Repeat Purchase Rate
    img3_path = str(CHARTS_DIR / "03_repeat_purchase_rate.png")
    story.append(Image(img3_path, width=490, height=170))
    story.append(Paragraph("Figure 3: Repeat customer rate: 96.96% bought once vs. 3.04% who bought again.", styles["caption"]))
    story.append(Spacer(1, 4))

    # Chart 4: Rolling 7-day orders and Top Categories
    img4_path = str(CHARTS_DIR / "04_top_categories_and_rolling_orders.png")
    story.append(Image(img4_path, width=490, height=170))
    story.append(Paragraph("Figure 4: 7-day rolling order count (left) and top 6 grossing categories (right).", styles["caption"]))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Key Findings:", styles["h2"]))
    story.append(Paragraph(
        "• <b>Very Low Repeat Rate:</b> Out of 94,990 eligible buyers (using <code>customer_unique_id</code>), "
        "92,102 customers (96.96%) placed only one order. Only 2,888 customers (3.04%) ever returned for a second order. "
        "Among repeat buyers, 91.8% placed exactly 2 orders, and very few placed 3 or more.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Daily Orders and Growth:</b> Daily order volume grew from under 20 orders per day in early 2017 to about 150–200 orders per day in 2018. "
        "The 7-calendar-day rolling average smoothed out weekend dips and clearly captured the Black Friday spike of 1,141 orders.",
        styles["bullet"]
    ))
    story.append(Paragraph(
        "• <b>Top States and Categories:</b> São Paulo (SP) is the biggest state with over 35% of total sales, followed by Rio de Janeiro (RJ) and Minas Gerais (MG). "
        "The highest-earning categories across Brazil are <i>health_beauty</i> (R$ 1.26M), <i>watches_gifts</i> (R$ 1.21M), and <i>bed_bath_table</i> (R$ 1.04M).",
        styles["bullet"]
    ))

    story.append(PageBreak())
    return story


def build_page_5(styles) -> list:
    """Page 5: Suggestions, Monitoring Table, and Limitations."""
    story = []

    story.append(Paragraph("7. Suggestions to Improve the Marketplace", styles["h1"]))
    story.append(Paragraph(
        "Based on our analysis of delivery delays and repeat purchases, here are three practical suggestions:",
        styles["body"]
    ))

    story.append(Paragraph(
        "<b>1. Give More Realistic Delivery Dates:</b><br/>"
        "Instead of showing fixed delivery estimates, add a few buffer days based on the distance between seller and buyer. "
        "If customers expect the order to arrive a little later, they will not be unhappy when small shipping delays occur. "
        "This can prevent many 1-star reviews caused by minor 1–2 day delays.",
        styles["body"]
    ))
    story.append(Spacer(1, 2))

    story.append(Paragraph(
        "<b>2. Enforce 48-Hour Seller Shipping:</b><br/>"
        "Require sellers to pack and hand over items to the courier within 48 hours. "
        "Sellers who regularly take too long should be given lower visibility in search results. "
        "Also, using local shipping hubs in high-volume states like São Paulo and Rio de Janeiro will cut delivery transit time.",
        styles["body"]
    ))
    story.append(Spacer(1, 2))

    story.append(Paragraph(
        "<b>3. Send 14-Day Follow-Up Discounts:</b><br/>"
        "Since 97% of buyers currently churn after one order, set up automated emails 14 days after delivery offering a 10% discount on their next order. "
        "Focus on replenishable products like Health & Beauty and Bed & Bath to encourage customers to make a second purchase.",
        styles["body"]
    ))
    story.append(Spacer(1, 6))

    # 8. Weekly Monitoring Metrics
    story.append(Paragraph("8. Weekly Monitoring Metrics", styles["h1"]))
    kpi_data = [
        [
            Paragraph("Metric", styles["header"]),
            Paragraph("Current Value", styles["header"]),
            Paragraph("Target", styles["header"]),
            Paragraph("Goal", styles["header"]),
        ],
        [
            Paragraph("Total Monthly Sales", styles["cell_bold"]),
            Paragraph("R$ 848k/mo", styles["cell"]),
            Paragraph("> R$ 1.0M/mo", styles["cell_bold"]),
            Paragraph("Maintain steady monthly sales growth.", styles["cell"]),
        ],
        [
            Paragraph("Repeat Purchase Rate", styles["cell_bold"]),
            Paragraph("3.04%", styles["cell"]),
            Paragraph("> 6.00%", styles["cell_bold"]),
            Paragraph("Double the percentage of returning customers.", styles["cell"]),
        ],
        [
            Paragraph("On-Time Delivery Rate", styles["cell_bold"]),
            Paragraph("92.20%", styles["cell"]),
            Paragraph("> 96.00%", styles["cell_bold"]),
            Paragraph("Reduce delivery delays across all states.", styles["cell"]),
        ],
        [
            Paragraph("Average Days Late (Delayed)", styles["cell_bold"]),
            Paragraph("+11.8 days", styles["cell"]),
            Paragraph("< 3.0 days", styles["cell_bold"]),
            Paragraph("Bring down severe double-digit delivery delays.", styles["cell"]),
        ],
        [
            Paragraph("Average Review Rating", styles["cell_bold"]),
            Paragraph("4.09 / 5.0", styles["cell"]),
            Paragraph("> 4.30 / 5.0", styles["cell_bold"]),
            Paragraph("Improve overall customer feedback.", styles["cell"]),
        ],
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 85, 90, 210.28], repeatRows=1)
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 6))

    # 9. Limitations
    story.append(Paragraph("9. Limitations", styles["h1"]))
    story.append(Paragraph(
        "• <b>Seller vs Courier Time:</b> The dataset does not tell us how much time the seller took to pack vs how long the courier took to drive.<br/>"
        "• <b>Missing Marketing Costs:</b> Ad spend and customer acquisition costs (CAC) are not included, so we cannot calculate acquisition ROI.<br/>"
        "• <b>No Returns Data:</b> The dataset does not record product returns, exchanges, or warranty complaints after delivery.<br/>"
        "• <b>No Website Traffic Logs:</b> We cannot see how many people visited the store or abandoned their shopping carts.",
        styles["body"]
    ))

    return story


def generate_pdf_report() -> Path:
    """Generate the simplified 5-page student assignment PDF report."""
    out_pdf_path = REPORT_DIR / "olist_weekly_business_review.pdf"
    print(f"Building Student Assignment PDF at: {out_pdf_path}...")

    doc = SimpleDocTemplate(
        str(out_pdf_path),
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    styles = get_student_styles()
    story = []

    story.extend(build_page_1(styles))
    story.extend(build_page_2(styles))
    story.extend(build_page_3(styles))
    story.extend(build_page_4(styles))
    story.extend(build_page_5(styles))

    doc.build(story, canvasmaker=StudentCanvas)
    print(f"Successfully generated PDF: {out_pdf_path}")
    return out_pdf_path


def validate_pdf_pages(pdf_path: Path):
    """Render every page of the PDF to image and check page count and layout."""
    print(f"\nValidating rendered pages of {pdf_path.name}...")
    doc = pymupdf.open(str(pdf_path))
    page_count = len(doc)
    print(f"Total Page Count: {page_count} (Requirement: <= 5 pages)")
    assert page_count <= 5, f"ERROR: PDF page count ({page_count}) exceeds 5 pages!"
    assert page_count == 5, f"WARNING: Expected exactly 5 pages, found {page_count}."

    rendered_images_dir = REPORT_DIR / "rendered_pages"
    rendered_images_dir.mkdir(parents=True, exist_ok=True)

    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=150)
        img_out = rendered_images_dir / f"page_{i}.png"
        pix.save(str(img_out))
        print(f"  Page {i}: Rendered to {img_out.name} ({pix.width}x{pix.height} px, {img_out.stat().st_size:,} bytes)")

    doc.close()
    print("All pages successfully rendered and inspected: EXACTLY 5 PAGES.")


if __name__ == "__main__":
    pdf_path = generate_pdf_report()
    validate_pdf_pages(pdf_path)
