import os
import PyPDF2
import docx
from datetime import datetime
from openai import OpenAI  # ✅ required import

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch
import streamlit as st
import re

client = OpenAI(api_key=st.secrets["openai"]["api_key"])


def extract_text_from_file(file):
    """Extract text from various file types."""
    if file is None:
        return ""
    
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    elif file_extension in ['doc', 'docx']:
        doc = docx.Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    
    elif file_extension == 'txt':
        return file.getvalue().decode('utf-8')
    
    return ""

def analyze_submission(question, supporting_docs, final_output):
    """Analyze submission using GPT-4.1-nano."""
    prompt = f"""
    You are Rohit Krishnan, a Business and Technology Strategist and an experienced Senior instructor at Boston Institute of Analytics. Analyze the following assignment submission with an encouraging and supporting tone and provide detailed feedback.

    Question:
    {question}
    
    Supporting Documents:
    {supporting_docs}
    
    Final Output:
    {final_output}
    
    Evaluate the submission based on these criteria (Total 10 marks):
    1. Code Quality and Structure (5 marks)
    2. Problem-Solving Approach (2 marks)
    3. Documentation and Comments (2 marks)
    4. Best Practices (1 mark)

    Provide feedback in this format:

    STRENGTHS:
    [Write a short paragraph summarizing the main strengths.]

    AREAS FOR IMPROVEMENT:
    [Write a short paragraph summarizing the main areas for improvement.]

    SCORE BREAKDOWN:
    Code Quality: [score]/5 – [brief explanation]
    Problem-Solving: [score]/2 – [brief explanation]
    Documentation: [score]/2 – [brief explanation]
    Best Practices: [score]/1 – [brief explanation]

    TOTAL SCORE: [total score]/10

    FINAL VERDICT:
    [Write a short paragraph with the final verdict and encouragement.]

    Please strictly follow this format so that each score breakdown line is present and detailed.
    """
    
    response = client.chat.completions.create(
    model="gpt-4.1-nano",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
    )

    
    return response.choices[0].message.content

def clean_bullets(text):
    # Remove markdown and extra symbols, split on dash, and clean
    items = [re.sub(r'[\-*•]+', '', s).replace('**', '').strip() for s in text.split(' - ') if s.strip()]
    return [item for item in items if item]

def clean_markdown(text):
    # Remove markdown symbols and extra whitespace
    return re.sub(r'[\-*•]+', '', text).replace('**', '').replace('###', '').strip()

def extract_score_details(score_breakdown_text):
    # Split on newlines for each criterion
    rows = []
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    for line in score_breakdown_text.splitlines():
        line = line.replace('**', '').strip()
        if line and ':' in line and not line.startswith('-') and not line.startswith('*'):
            parts = line.split(':', 1)
            crit = parts[0].strip()
            rest = parts[1].strip()
            # Split score and explanation if possible
            match = re.match(r'([0-9]+(?:\.[0-9]+)?\s*/\s*[0-9]+)\s*[–-]?\s*(.*)', rest)
            if match:
                score = match.group(1).replace(' ', '')
                explanation = match.group(2).strip()
            else:
                score = rest.split()[0] if rest.split() else rest
                explanation = ' '.join(rest.split()[1:]) if len(rest.split()) > 1 else ''
            # Use Paragraph for explanation to allow wrapping
            rows.append([crit, Paragraph(f"{score} – {explanation}", styles['BodyText']) if explanation else score])
    return rows

def parse_assignment_summary(summary):
    # Try to extract known fields and return as (label, value) pairs
    fields = [
        ("Assignment Title", r"Assignment\s*:?\s*([^■\n]+)", None),
        ("Institution", r"Institution\s*:?\s*([^■\n]+)", None),
        ("Trainer", r"Trainer\s*:?\s*([^■\n]+)", None),
        ("Due Date", r"Due Date\s*:?\s*([^■\n]+)", None),
        ("Submission Format", r"Submission Format\s*:?\s*([^■\n]+)", None),
    ]
    results = []
    for label, pattern, _ in fields:
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            results.append((label, match.group(1).strip()))
    return results

def generate_pdf_report(student_name, institution, question_summary, feedback, score, output_path):
    """Generate PDF report."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    story.append(Paragraph("SkillShareVerify™ Report", title_style))

    # Header with timestamp
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # Student Information
    story.append(Paragraph("<b>Student Information</b>", styles['Heading2']))
    story.append(Paragraph(f"<b>Name:</b> {student_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Institution:</b> {institution}", styles['Normal']))
    story.append(Spacer(1, 10))

    # Trainer Information
    story.append(Paragraph("<b>Trainer Information</b>", styles['Heading2']))
    story.append(Paragraph("<b>Name:</b> Rohit Krishnan", styles['Normal']))
    story.append(Paragraph("<b>Role:</b> Senior Trainer of Data Science & AI", styles['Normal']))
    story.append(Spacer(1, 20))

    # Feedback (structured)
    story.append(Paragraph("<b>Feedback</b>", styles['Heading2']))
    strengths = re.findall(r"STRENGTHS:(.*?)(AREAS FOR IMPROVEMENT:|SCORE BREAKDOWN:|TOTAL SCORE:|FINAL VERDICT:)", feedback, re.DOTALL)
    improvements = re.findall(r"AREAS FOR IMPROVEMENT:(.*?)(SCORE BREAKDOWN:|TOTAL SCORE:|FINAL VERDICT:)", feedback, re.DOTALL)
    score_breakdown = re.findall(r"SCORE BREAKDOWN:(.*?)(TOTAL SCORE:|FINAL VERDICT:)", feedback, re.DOTALL)
    total_score = re.findall(r"TOTAL SCORE:(.*?)(FINAL VERDICT:)", feedback, re.DOTALL)
    final_verdict = re.findall(r"FINAL VERDICT:(.*)", feedback, re.DOTALL)

    # Strengths as paragraph
    if strengths:
        strengths_text = clean_markdown(strengths[0][0]).replace(' .', '.').replace('..', '.').strip()
        if strengths_text:
            story.append(Paragraph(f"<b>Strengths:</b> {strengths_text}", styles['BodyText']))
            story.append(Spacer(1, 6))
    # Areas for Improvement as paragraph
    if improvements:
        improvements_text = clean_markdown(improvements[0][0]).replace(' .', '.').replace('..', '.').strip()
        if improvements_text:
            story.append(Paragraph(f"<b>Areas for Improvement:</b> {improvements_text}", styles['BodyText']))
            story.append(Spacer(1, 6))
    # Score Breakdown Table with details
    if score_breakdown:
        story.append(Paragraph("<b>Score Breakdown:</b>", styles['BodyText']))
        table_data = [["Criteria", "Score & Explanation"]]
        table_data += extract_score_details(score_breakdown[0][0])
        col_widths = [2.5*inch, 3.5*inch]
        table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(table)
        story.append(Spacer(1, 6))
    # Total Score
    if total_score:
        story.append(Paragraph(f"<b>Total Score:</b> {clean_markdown(total_score[0][0].strip())}", styles['BodyText']))
        story.append(Spacer(1, 6))
    # Final Verdict as paragraph
    if final_verdict:
        verdict_text = clean_markdown(final_verdict[0]).replace(' .', '.').replace('..', '.').strip()
        if verdict_text:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>Final Verdict:</b> {verdict_text}", styles['BodyText']))
            story.append(Spacer(1, 10))

    # Score
    story.append(Paragraph("<b>Score</b>", styles['Heading2']))
    story.append(Paragraph(f"Score: {score}/10", styles['Normal']))

    # Footer with contact details
    story.append(Spacer(1, 50))
    story.append(Paragraph("Generated via SkillShareVerify™", styles['Normal']))
    story.append(Paragraph("Created by Rohit Krishnan", styles['Normal']))
    story.append(Paragraph("Contact Information:", styles['Normal']))
    story.append(Paragraph("📧 Email: rohitkrishnanm@gmail.com", styles['Normal']))
    story.append(Paragraph("🌐 Website: https://rohitkrishnan.co.in", styles['Normal']))
    story.append(Paragraph("🔗 LinkedIn: https://www.linkedin.com/in/rohit-krishnan-m", styles['Normal']))
    story.append(Paragraph("📸 Instagram: https://www.instagram.com/prof_rohit_/", styles['Normal']))

    doc.build(story)

def get_evaluation_result(score):
    """Get evaluation result based on score."""
    if score >= 6:
        return "✅ Pass"
    elif score >= 4:
        return "⚠️ Can Improve"
    else:
        return "❌ Rework" 
