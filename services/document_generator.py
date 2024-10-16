import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from config import UPLOAD_FOLDER
import os

logger = logging.getLogger(__name__)

def generate_document(content):
    output_path = os.path.join(UPLOAD_FOLDER, "solved_assignment.pdf")
    logger.debug(f"Generating document at: {output_path}")
    
    if not content:
        logger.error("Content is empty. Cannot generate document.")
        return None

    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Question', fontSize=12, spaceAfter=6, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='QuestionInfo', fontSize=10, spaceAfter=6, fontName='Helvetica-Oblique'))
        styles.add(ParagraphStyle(name='Answer', fontSize=11, leftIndent=20, spaceAfter=12))
        styles.add(ParagraphStyle(name='Separator', fontSize=11))

        story = []

        for paragraph in content.split('\n'):
            if paragraph.startswith("Question"):
                story.append(Paragraph(paragraph, styles['Question']))
            elif paragraph.startswith("Marks:"):
                story.append(Paragraph(paragraph, styles['QuestionInfo']))
            elif paragraph.startswith("Answer:"):
                story.append(Paragraph(paragraph, styles['Answer']))
            elif paragraph.startswith("-"):
                story.append(Paragraph(paragraph, styles['Separator']))
                story.append(Spacer(1, 0.2 * inch))
            else:
                story.append(Paragraph(paragraph, styles['Normal']))

        logger.debug(f"Number of elements in story: {len(story)}")

        doc.build(story)
        logger.debug(f"Document built successfully. File size: {os.path.getsize(output_path)} bytes")

        return output_path
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}", exc_info=True)
        return None
    
def generate_cover_letter(name, company, position, skills):
    """
    Generate a professional cover letter based on provided information
    
    Args:
        name (str): Applicant's name
        company (str): Company name
        position (str): Position being applied for
        skills (str): Comma-separated list of top skills
    
    Returns:
        str: Generated cover letter text
    """
    try:
        # Format current date
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Format skills as bullet points
        skills_list = [skill.strip() for skill in skills.split(',')]
        formatted_skills = '\n'.join([f"• {skill}" for skill in skills_list])
        
        cover_letter_template = f"""
{current_date}

Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company}. As a professional with expertise in the following areas:

{formatted_skills}

I am confident in my ability to contribute significantly to your team and help drive {company}'s continued success.

Throughout my career, I have developed and refined these skills through hands-on experience and continuous learning. I am particularly drawn to {company}'s commitment to innovation and excellence in the industry, and I believe my background aligns perfectly with your needs.

I would welcome the opportunity to discuss how my skills and experiences can benefit {company}. Thank you for considering my application.

Best regards,
{name}
"""
        return cover_letter_template.strip()
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}", exc_info=True)
        return "Error generating cover letter. Please try again."
