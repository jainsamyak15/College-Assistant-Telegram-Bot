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