import os
import json
from datetime import datetime
from pathlib import Path
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

METADATA_PATH = Path(__file__).parent.parent / "models" / "model_metadata.json"

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

    # Load model metadata if available
    metadata = {}
    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, "r") as f:
                metadata = json.load(f)
        except Exception:
            pass

    pdf_filename = f"rehab_report_{assessment_id}.pdf"
    pdf_path = REPORT_DIR / pdf_filename

    if not REPORTLAB_AVAILABLE:
        with open(pdf_path, "w") as f:
            f.write(f"STROKE REHABILITATION ANALYSIS REPORT\n")
            f.write(f"Patient Name: {patient['name']}\n")
            f.write(f"Session: {assessment['session_number']}\n")
            f.write(f"AI Prediction: {assessment.get('predictions', {}).get('impairment_level')} (Confidence: {assessment.get('predictions', {}).get('confidence')}%)\n")
            f.write(f"Disclaimer: Research decision-support only. Final treatment decisions should be made by qualified healthcare professionals.\n")
        return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")

    try:
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Color Theme (#2563EB primary, #14B8A6 secondary)
        primary_color = HexColor("#2563EB")
        secondary_color = HexColor("#14B8A6")
        dark_neutral = HexColor("#1F2937")
        light_neutral = HexColor("#F9FAFB")
        border_color = HexColor("#E5E7EB")
        
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=primary_color,
            spaceAfter=12
        )
        
        section_style = ParagraphStyle(
            'ReportSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            textColor=secondary_color,
            spaceBefore=12,
            spaceAfter=8
        )

        label_style = ParagraphStyle(
            'ReportLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.0,
            textColor=dark_neutral
        )
        
        value_style = ParagraphStyle(
            'ReportValue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.0,
            textColor=dark_neutral
        )
        
        disclaimer_style = ParagraphStyle(
            'ReportDisclaimer',
            parent=styles['Italic'],
            fontName='Helvetica-Oblique',
            fontSize=8.0,
            textColor=colors.red,
            alignment=1, # Center
            spaceBefore=18
        )

        story = []
        
        # 1. Header banner
        story.append(Paragraph("QUANTITATIVE MOVEMENT & GAIT ANALYSIS REPORT", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Stroke Rehabilitation AI Decision-Support System", value_style))
        story.append(Spacer(1, 8))
        
        # Divider Line
        divider = Table([[""]], colWidths=[530], rowHeights=[2])
        divider.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider)
        story.append(Spacer(1, 10))

        # 2. Patient Demographics (User-Entered)
        story.append(Paragraph("1. Clinician-Entered Patient Information", section_style))
        patient_data = [
            [Paragraph("Patient ID:", label_style), Paragraph(patient["patient_id"], value_style),
             Paragraph("Stroke Classification:", label_style), Paragraph(patient["stroke_type"], value_style)],
            [Paragraph("Name:", label_style), Paragraph(patient["name"], value_style),
             Paragraph("Observed Deficit Side:", label_style), Paragraph(patient["affected_side"], value_style)],
            [Paragraph("Age / Gender:", label_style), Paragraph(f"{patient['age']} / {patient['gender']}", value_style),
             Paragraph("Onset Date:", label_style), Paragraph(patient["stroke_date"], value_style)],
        ]
        patient_table = Table(patient_data, colWidths=[110, 150, 110, 160])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_neutral),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 10))

        # Video Quality Information
        vq = assessment.get("video_quality")
        if vq and isinstance(vq, dict):
            vq_data = [
                [Paragraph("Video Tracking Grade:", label_style), Paragraph(f"<b>{vq.get('category', 'N/A')}</b> (Pose Rate: {vq.get('score', 0)}%)", value_style),
                 Paragraph("Frame Telemetry:", label_style), Paragraph(f"{vq.get('tracked_frames', 0)} / {vq.get('total_frames', 0)} frames ({vq.get('fps', 0)} FPS)", value_style)]
            ]
            vq_table = Table(vq_data, colWidths=[120, 140, 110, 160])
            vq_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), HexColor("#F0FDF4")),
                ('GRID', (0,0), (-1,-1), 0.5, HexColor("#BBF7D0")),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(vq_table)
            story.append(Spacer(1, 10))

        # 3. AI Predictive Assessment
        story.append(Paragraph("2. StrokeRehab ML Pattern Classification", section_style))
        pred = assessment.get("predictions") or {}
        imp_level = pred.get("impairment_level", "Not reliably measurable")
        
        status_color = HexColor("#2563EB")
        if "Healthy" in imp_level:
            status_color = HexColor("#10B981")
        elif "Restricted" in imp_level:
            status_color = HexColor("#F59E0B")
        elif "Unstable" in imp_level:
            status_color = HexColor("#EF4444")

        level_style = ParagraphStyle(
            'ImpLevel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=status_color
        )
        
        conf_val = pred.get("confidence")
        conf_str = f"{conf_val:.1f}%" if conf_val is not None else "N/A"

        ai_data = [
            [Paragraph("Classifier Algorithm:", label_style), Paragraph(pred.get("model_used", "Random Forest"), value_style)],
            [Paragraph("Training Dataset:", label_style), Paragraph(f"{metadata.get('dataset_name', 'StrokeRehab Dataset')} (71 Participants: 51 Stroke, 20 Control)", value_style)],
            [Paragraph("Validation Protocol:", label_style), Paragraph(f"{metadata.get('validation_protocol', '5-Fold Subject-Independent StratifiedGroupKFold')}", value_style)],
            [Paragraph("Predicted Movement Class:", label_style), Paragraph(f"{imp_level}", level_style)],
            [Paragraph("Model Confidence:", label_style), Paragraph(conf_str, value_style)]
        ]
        
        probs = pred.get("prediction_probabilities")
        if probs and isinstance(probs, dict):
            prob_str = ", ".join([f"{k}: {v}%" for k, v in probs.items()])
            ai_data.append([Paragraph("Probability Breakdown P(c):", label_style), Paragraph(prob_str, value_style)])

        ai_table = Table(ai_data, colWidths=[150, 380])
        ai_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (0,-1), light_neutral),
            ('PADDING', (0,0), (-1,-1), 4),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(ai_table)
        story.append(Spacer(1, 10))

        # 4. Clinical Validation Scales
        story.append(Paragraph("3. Clinician-Entered Validation Scales", section_style))
        scores = assessment.get("clinical_scores") or {}
        scores_data = [
            [Paragraph("Clinical Scale", label_style), Paragraph("Entered Score", label_style), Paragraph("Validation Range", label_style)],
            [Paragraph("Fugl-Meyer Assessment (FMA)", value_style), Paragraph(str(scores.get("fma_score", 0)), value_style), Paragraph("0 - 226 (Motor Recovery)", value_style)],
            [Paragraph("Berg Balance Scale (BBS)", value_style), Paragraph(str(scores.get("bbs_score", 0)), value_style), Paragraph("0 - 56 (Standing Balance)", value_style)],
            [Paragraph("Functional Ambulation Categories (FAC)", value_style), Paragraph(str(scores.get("fac_score", 0)), value_style), Paragraph("0 - 5 (Walking Independence)", value_style)],
            [Paragraph("Timed Up and Go (TUG)", value_style), Paragraph(f"{scores.get('tug_score', 0.0)} s", value_style), Paragraph("< 10s (Normal Functional Mobility)", value_style)],
            [Paragraph("Normalized Composite Clinical Score", label_style), Paragraph(f"{scores.get('overall_clinical_score', 0.0)}%", label_style), Paragraph("0 - 100%", label_style)]
        ]
        scores_table = Table(scores_data, colWidths=[230, 150, 150])
        scores_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,0), light_neutral),
            ('BACKGROUND', (0,-1), (-1,-1), HexColor("#EFF6FF")),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (1,0), (2,-1), 'CENTER'),
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 10))

        # 5. Extracted Gait & Range of Motion Metrics
        story.append(Paragraph("4. Objective Video-Derived Biomechanical Kinematic Parameters", section_style))
        feats = assessment.get("extracted_features") or {}
        angles = feats.get("angles") or {}
        gait = feats.get("gait") or {}
        
        speed_idx = gait.get("walking_speed_index") or gait.get("walking_speed_ms")
        stride_idx = gait.get("stride_length_index") or gait.get("stride_length_m")
        width_idx = gait.get("step_width_index") or gait.get("step_width_m")
        symmetry_val = gait.get("step_symmetry_ratio")
        cadence_val = gait.get("cadence_steps_min")
        
        knee_val = angles.get("knee_angle_deg")
        hip_val = angles.get("hip_angle_deg")
        elbow_val = angles.get("elbow_angle_deg")
        shoulder_val = angles.get("shoulder_angle_deg")
        balance_val = feats.get("balance_stability_score")

        fmt_val = lambda v, unit="": f"{v:.2f}{unit}" if isinstance(v, (int, float)) else "Not reliably measurable"

        metrics_data = [
            [Paragraph("Biomechanical Parameter", label_style), Paragraph("Extracted Value", label_style), Paragraph("Clinical Interpretation", label_style)],
            [Paragraph("Relative Walking Speed Index", value_style), Paragraph(fmt_val(speed_idx), value_style), Paragraph("Gait progression velocity relative proxy", value_style)],
            [Paragraph("Relative Stride Length Index", value_style), Paragraph(fmt_val(stride_idx), value_style), Paragraph("Step stride length relative proxy", value_style)],
            [Paragraph("Step Cadence", value_style), Paragraph(fmt_val(cadence_val, " steps/min"), value_style), Paragraph("Temporal stepping frequency", value_style)],
            [Paragraph("Step Symmetry Ratio", value_style), Paragraph(fmt_val(symmetry_val), value_style), Paragraph("Bilateral temporal ratio (1.0 = symmetric)", value_style)],
            [Paragraph("Pose Stability Index", value_style), Paragraph(fmt_val(balance_val, "%"), value_style), Paragraph("Pose-derived trunk sway stability proxy", value_style)],
            [Paragraph("Peak Knee Flexion Angle", value_style), Paragraph(fmt_val(knee_val, "°"), value_style), Paragraph("180° minus interior knee joint angle", value_style)],
            [Paragraph("Hip Range of Motion", value_style), Paragraph(fmt_val(hip_val, "°"), value_style), Paragraph("Sagittal hip excursion angle", value_style)],
            [Paragraph("Elbow Flexion Angle", value_style), Paragraph(fmt_val(elbow_val, "°"), value_style), Paragraph("Upper-limb flexor tone indicator", value_style)],
            [Paragraph("Shoulder Swing Range", value_style), Paragraph(fmt_val(shoulder_val, "°"), value_style), Paragraph("Arm swing dynamics during walking", value_style)]
        ]
        metrics_table = Table(metrics_data, colWidths=[180, 120, 230])
        metrics_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,0), light_neutral),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 10))

        # 6. Analysis-Based Rehabilitation Considerations
        story.append(Paragraph("5. Analysis-Based Rehabilitation Considerations", section_style))
        prescribed_exs = assessment.get("prescribed_exercises", [])
        if prescribed_exs:
            ex_table_data = [
                [Paragraph("Targeted Exercise", label_style), 
                 Paragraph("Category", label_style), 
                 Paragraph("Dosage & Intensity", label_style), 
                 Paragraph("Biomechanical Rationale", label_style)]
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
                    continue
                bullet_style = ParagraphStyle(
                    'BulletRec', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=dark_neutral,
                    leftIndent=15, firstLineIndent=-10, spaceAfter=3
                )
                story.append(Paragraph(f"• {rec}", bullet_style))
            story.append(Spacer(1, 10))
            
        story.append(Paragraph("Clinician Session Notes:", label_style))
        story.append(Paragraph(assessment.get("therapist_notes") or "No manual clinician notes logged.", value_style))

        # 7. Signature & Disclaimer
        story.append(Spacer(1, 15))
        
        sig_data = [
            [Paragraph("_____________________________<br/>Assessing Physiotherapist", label_style),
             Paragraph("_____________________________<br/>Consulting Physician", label_style)]
        ]
        sig_table = Table(sig_data, colWidths=[265, 265])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(sig_table)
        
        # Medical Disclaimer
        story.append(Paragraph("RESEARCH & DECISION-SUPPORT DISCLAIMER: RehabShield provides AI-assisted movement analysis for research and rehabilitation support. Results are not a medical diagnosis and should be interpreted by a qualified healthcare professional.", disclaimer_style))

        # Build PDF
        doc.build(story)
        
    except Exception as e:
        print(f"Error compiling ReportLab PDF: {e}")
        with open(pdf_path, "w") as f:
            f.write(f"STROKE REHABILITATION ANALYSIS REPORT - Error generating pdf: {e}\n")
            f.write(f"Patient Name: {patient['name']}\n")
            f.write(f"Session: {assessment['session_number']}\n")

    return FileResponse(pdf_path, filename=pdf_filename, media_type="application/pdf")
