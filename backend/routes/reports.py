import os
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.db import get_collection
from backend.auth import get_current_user
from backend.config import REPORT_DIR

# Import ReportLab modules
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

router = APIRouter(prefix="/reports", tags=["Report Generation"])

@router.get("/generate/{assessment_id}")
def generate_pdf_report(assessment_id: str, current_user: dict = Depends(get_current_user)) -> Any:
    assessments_coll = get_collection("assessments")
    patients_coll = get_collection("patients")
    
    # 1. Retrieve Assessment and Patient
    assessment = assessments_coll.find_one({"_id": assessment_id})
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    patient = patients_coll.find_one({"patient_id": assessment["patient_id"]})
    if not patient:
        patient = patients_coll.find_one({"_id": assessment["patient_id"]})
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile associated with assessment not found")

    pdf_filename = f"rehab_report_{assessment_id}.pdf"
    pdf_path = REPORT_DIR / pdf_filename

    # If PDF already exists, we can return it directly, or regenerate it
    # We will regenerate it to capture any changes in notes/scores
    if not REPORTLAB_AVAILABLE:
        # Fallback if reportlab fails to import (we write a text file or simple html / dummy file)
        # Create a mock PDF file just to satisfy the response so the app doesn't crash
        with open(pdf_path, "w") as f:
            f.write(f"REHABILITATION ANALYSIS REPORT\n")
            f.write(f"Patient Name: {patient['name']}\n")
            f.write(f"Session: {assessment['session_number']}\n")
            f.write(f"AI Prediction: {assessment['predictions']['impairment_level']} (Confidence: {assessment['predictions']['confidence']})\n")
            f.write(f"Disclaimer: Final treatment decisions should be made by qualified healthcare professionals.\n")
        return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")

    try:
        # Build beautiful PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles using project color theme (#2563EB primary, #14B8A6 secondary)
        primary_color = HexColor("#2563EB")
        secondary_color = HexColor("#14B8A6")
        dark_neutral = HexColor("#1F2937")
        light_neutral = HexColor("#F9FAFB")
        border_color = HexColor("#E5E7EB")
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=primary_color,
            spaceAfter=15
        )
        
        section_style = ParagraphStyle(
            'ReportSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=secondary_color,
            spaceBefore=15,
            spaceAfter=10
        )

        label_style = ParagraphStyle(
            'ReportLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=dark_neutral
        )
        
        value_style = ParagraphStyle(
            'ReportValue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=dark_neutral
        )
        
        disclaimer_style = ParagraphStyle(
            'ReportDisclaimer',
            parent=styles['Italic'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.red,
            alignment=1, # Center
            spaceBefore=25
        )

        story = []
        
        # 1. Header banner
        story.append(Paragraph("STROKE REHABILITATION ANALYSIS REPORT", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Decision Support System", value_style))
        story.append(Spacer(1, 10))
        
        # Divider Line
        divider = Table([[""]], colWidths=[530], rowHeights=[2])
        divider.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider)
        story.append(Spacer(1, 15))

        # 2. Patient Demographics & Profile
        story.append(Paragraph("1. Patient Information", section_style))
        patient_data = [
            [Paragraph("Patient ID:", label_style), Paragraph(patient["patient_id"], value_style),
             Paragraph("Stroke Type:", label_style), Paragraph(patient["stroke_type"], value_style)],
            [Paragraph("Name:", label_style), Paragraph(patient["name"], value_style),
             Paragraph("Affected Side:", label_style), Paragraph(patient["affected_side"], value_style)],
            [Paragraph("Age / Gender:", label_style), Paragraph(f"{patient['age']} / {patient['gender']}", value_style),
             Paragraph("Stroke Date:", label_style), Paragraph(patient["stroke_date"], value_style)],
        ]
        patient_table = Table(patient_data, colWidths=[100, 160, 100, 170])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_neutral),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 15))

        # 3. AI Predictive Assessment
        story.append(Paragraph("2. AI Motor Impairment Assessment", section_style))
        pred = assessment["predictions"]
        
        # Match color based on impairment
        imp_level = pred["impairment_level"]
        color_map = {
            "Normal": HexColor("#10B981"),
            "Mild": HexColor("#3B82F6"),
            "Moderate": HexColor("#F59E0B"),
            "Severe": HexColor("#EF4444"),
            "Very Severe": HexColor("#7F1D1D")
        }
        status_color = color_map.get(imp_level, primary_color)
        
        level_style = ParagraphStyle(
            'ImpLevel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=status_color
        )
        
        ai_data = [
            [Paragraph("Model Classifier:", label_style), Paragraph(pred["model_used"], value_style)],
            [Paragraph("Impairment Severity:", label_style), Paragraph(f"{imp_level}", level_style)],
            [Paragraph("Classifier Confidence:", label_style), Paragraph(f"{int(pred['confidence']*100)}%", value_style)]
        ]
        ai_table = Table(ai_data, colWidths=[150, 380])
        ai_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (0,-1), light_neutral),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(ai_table)
        story.append(Spacer(1, 15))

        # 4. Clinical Validation Scores
        story.append(Paragraph("3. Clinical Assessment Scores", section_style))
        scores = assessment["clinical_scores"]
        scores_data = [
            [Paragraph("Scale", label_style), Paragraph("Score Achieved", label_style), Paragraph("Clinical Range", label_style)],
            [Paragraph("Fugl-Meyer Assessment (FMA)", value_style), Paragraph(str(scores.get("fma_score", 0)), value_style), Paragraph("0 - 226", value_style)],
            [Paragraph("Berg Balance Scale (BBS)", value_style), Paragraph(str(scores.get("bbs_score", 0)), value_style), Paragraph("0 - 56", value_style)],
            [Paragraph("Functional Ambulation Categories (FAC)", value_style), Paragraph(str(scores.get("fac_score", 0)), value_style), Paragraph("0 - 5", value_style)],
            [Paragraph("Timed Up and Go (TUG)", value_style), Paragraph(f"{scores.get('tug_score', 0.0)} s", value_style), Paragraph("< 10s (Normal)", value_style)],
            [Paragraph("Overall Normalized Clinical Score", label_style), Paragraph(f"{scores.get('overall_clinical_score', 0.0)}%", label_style), Paragraph("0 - 100%", label_style)]
        ]
        scores_table = Table(scores_data, colWidths=[230, 150, 150])
        scores_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,0), light_neutral),
            ('BACKGROUND', (0,-1), (-1,-1), HexColor("#EFF6FF")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('ALIGN', (1,0), (2,-1), 'CENTER'),
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 15))

        # 5. Extracted Gait & Range of Motion Metrics
        story.append(Paragraph("4. Computer Vision Key Metrics", section_style))
        feats = assessment["extracted_features"]
        angles = feats["angles"]
        gait = feats["gait"]
        
        metrics_data = [
            [Paragraph("Metric Category", label_style), Paragraph("Value Extracted", label_style), Paragraph("Clinical Relevance", label_style)],
            [Paragraph("Walking Speed", value_style), Paragraph(f"{gait['walking_speed_ms']} m/s", value_style), Paragraph("Indicates spatial mobility level", value_style)],
            [Paragraph("Step Symmetry Ratio", value_style), Paragraph(str(gait['step_symmetry_ratio']), value_style), Paragraph("Close to 1.0 indicates symmetric walk", value_style)],
            [Paragraph("Balance Stability Score", value_style), Paragraph(f"{feats['balance_stability_score']}%", value_style), Paragraph("Center-of-mass sway control", value_style)],
            [Paragraph("Knee Flexion Angle", value_style), Paragraph(f"{angles['knee_angle_deg']}°", value_style), Paragraph("Crucial for limb swing clearance", value_style)],
            [Paragraph("Hip Range of Motion", value_style), Paragraph(f"{angles['hip_angle_deg']}°", value_style), Paragraph("Underpins step stride length", value_style)],
            [Paragraph("Elbow Flexion Angle", value_style), Paragraph(f"{angles['elbow_angle_deg']}°", value_style), Paragraph("Indicates level of upper limb spasticity", value_style)],
            [Paragraph("Shoulder Swing Mobility", value_style), Paragraph(f"{angles['shoulder_angle_deg']}°", value_style), Paragraph("Linked to walking balance/arm swing", value_style)]
        ]
        metrics_table = Table(metrics_data, colWidths=[180, 120, 230])
        metrics_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,0), light_neutral),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 15))

        # 6. Prescribed Rehabilitation Exercises & Recommendations
        story.append(Paragraph("5. Prescribed Home Rehabilitation & Exercise Program", section_style))
        prescribed_exs = assessment.get("prescribed_exercises", [])
        if prescribed_exs:
            ex_table_data = [
                [Paragraph("Prescribed Exercise", label_style), 
                 Paragraph("Category", label_style), 
                 Paragraph("Dosage & Frequency", label_style), 
                 Paragraph("Clinical Rationale", label_style)]
            ]
            for ex in prescribed_exs:
                ex_title_p = Paragraph(f"<b>{ex.get('title', '')}</b><br/><font size=7.5 color='#64748B'>{ex.get('target_deficit', '')}</font>", value_style)
                ex_cat_p = Paragraph(f"{ex.get('category', '')}<br/><font size=7.5 color='#0284C7'>({ex.get('intensity', '')})</font>", value_style)
                ex_dose_p = Paragraph(f"<b>{ex.get('dosage', '')}</b>", value_style)
                ex_rat_p = Paragraph(f"{ex.get('clinical_rationale', '')}", value_style)
                ex_table_data.append([ex_title_p, ex_cat_p, ex_dose_p, ex_rat_p])
                
            ex_table = Table(ex_table_data, colWidths=[150, 85, 115, 180])
            ex_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, border_color),
                ('BACKGROUND', (0,0), (-1,0), light_neutral),
                ('PADDING', (0,0), (-1,-1), 4),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            story.append(ex_table)
            story.append(Spacer(1, 10))
        else:
            for rec in assessment.get("recommendations", []):
                if "healthcare professionals" in rec:
                    continue # Skip disclaimer duplicate here, we put it at bottom
                bullet_style = ParagraphStyle(
                    'BulletRec', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, textColor=dark_neutral,
                    leftIndent=15, firstLineIndent=-10, spaceAfter=4
                )
                story.append(Paragraph(f"• {rec}", bullet_style))
            story.append(Spacer(1, 10))
            
        story.append(Paragraph("Clinical Session Notes:", label_style))
        story.append(Paragraph(assessment.get("therapist_notes") or "No manual clinician notes logged.", value_style))

        # 7. Signature / Disclaimer
        story.append(Spacer(1, 20))
        
        sig_data = [
            [Paragraph("_____________________________<br/>Assessing Physiotherapist", label_style),
             Paragraph("_____________________________<br/>Consulting Doctor", label_style)]
        ]
        sig_table = Table(sig_data, colWidths=[265, 265])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(sig_table)
        
        # Medical Disclaimer
        story.append(Paragraph("Disclaimer: This report is a decision-support tool. Final treatment decisions should be made by qualified healthcare professionals.", disclaimer_style))

        # Build PDF
        doc.build(story)
        
    except Exception as e:
        print(f"Error compiling ReportLab PDF: {e}")
        # fallback to simple file
        with open(pdf_path, "w") as f:
            f.write(f"REHABILITATION ANALYSIS REPORT - Error generating pdf: {e}\n")
            f.write(f"Patient Name: {patient['name']}\n")
            f.write(f"Session: {assessment['session_number']}\n")
            f.write(f"AI Prediction: {assessment['predictions']['impairment_level']} (Confidence: {assessment['predictions']['confidence']})\n")
            f.write(f"Disclaimer: Final treatment decisions should be made by qualified healthcare professionals.\n")

    return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")
