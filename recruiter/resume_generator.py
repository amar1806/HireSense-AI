# ============================================
# IMPORT REQUIRED LIBRARIES
# ============================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ============================================
# FUNCTION: GENERATE RESUME IMPROVEMENTS
# (Used for suggestions in dashboard)
# ============================================

def generate_resume_improvements(gaps):

    improvements = []

    for skill in gaps:

        if skill == "python":
            improvements.append("Add Python projects (automation, APIs, ML)")

        elif skill == "machine learning":
            improvements.append("Include ML projects using Scikit-learn")

        elif skill == "sql":
            improvements.append("Add database experience using MySQL/PostgreSQL")

        elif skill == "django":
            improvements.append("Develop web apps using Django framework")

        else:
            improvements.append(f"Gain practical experience in {skill}")

    return improvements


# ============================================
# FUNCTION: GENERATE PROFESSIONAL RESUME PDF (TEMPLATED)
# ============================================

def generate_resume_pdf(data, file_path, template="modern"):
    """Generate a premium resume PDF using a selected template.

    data = {
        "name": str,
        "email": str,
        "skills": str,
        "experience": str,
        "role": str,
    }

    template: one of ["modern", "classic"]
    """

    # ----------------------------------------
    # CREATE DOCUMENT
    # ----------------------------------------

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    # ----------------------------------------
    # LOAD STYLES
    # ----------------------------------------

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # Template tweaks
    if template == "classic":
        title_style.fontName = "Times-Bold"
        heading_style.fontName = "Times-Bold"
        normal_style.fontName = "Times-Roman"
    else:
        title_style.fontName = "Helvetica-Bold"
        heading_style.fontName = "Helvetica-Bold"
        normal_style.fontName = "Helvetica"

    # Add a subtle color bar in modern template
    elements = []
    if template == "modern":
        from reportlab.platypus import Flowable

        class ColoredBar(Flowable):
            def __init__(self, width, height=12, color=(0.0, 0.75, 0.9)):
                Flowable.__init__(self)
                self.width = width
                self.height = height
                self.color = color

            def draw(self):
                self.canv.setFillColorRGB(*self.color)
                self.canv.rect(0, 0, self.width, self.height, stroke=0, fill=1)

        elements.append(ColoredBar(450, height=12))
        elements.append(Spacer(1, 10))

    # ============================================
    # HEADER SECTION (NAME + CONTACT)
    # ============================================

    elements.append(Paragraph(data.get("name", ""), title_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(data.get("email", ""), normal_style))
    elements.append(Spacer(1, 16))

    # ============================================
    # PROFESSIONAL SUMMARY
    # ============================================

    summary = f"""
    Motivated {data.get('role', 'Software Engineer')} with strong problem-solving skills,
    experience in modern technologies, and ability to build scalable applications.
    """

    elements.append(Paragraph("Professional Summary", heading_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(summary, normal_style))
    elements.append(Spacer(1, 16))

    # ============================================
    # SKILLS SECTION
    # ============================================

    elements.append(Paragraph("Skills", heading_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(data.get("skills", ""), normal_style))
    elements.append(Spacer(1, 16))

    # ============================================
    # EXPERIENCE SECTION
    # ============================================

    elements.append(Paragraph("Experience", heading_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(data.get("experience", ""), normal_style))
    elements.append(Spacer(1, 16))

    # ============================================
    # PROJECTS SECTION (AUTO-GENERATED)
    # ============================================

    elements.append(Paragraph("Projects", heading_style))
    elements.append(Spacer(1, 8))

    project_text = """
    • AI Resume Analyzer – Developed a machine learning-based system to analyze resumes and calculate ATS scores.<br/>
    • FarmLink AI – Built a predictive model for agricultural price estimation using ML algorithms.
    """

    elements.append(Paragraph(project_text, normal_style))
    elements.append(Spacer(1, 16))

    # ============================================
    # EDUCATION SECTION
    # ============================================

    elements.append(Paragraph("Education", heading_style))
    elements.append(Spacer(1, 8))

    education_text = """
    B.Tech in Computer Science<br/>
    Relevant Coursework: Data Structures, Machine Learning, Web Development
    """

    elements.append(Paragraph(education_text, normal_style))

    # ----------------------------------------
    # BUILD PDF
    # ----------------------------------------

    doc.build(elements)

    return file_path
