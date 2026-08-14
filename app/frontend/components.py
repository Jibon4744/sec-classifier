import gradio as gr

def get_header():
    """Generates a premium, sunflower-themed header block."""
    return gr.HTML("""
    <div style="
        background: linear-gradient(135deg, #FFB300 0%, #F57C00 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(245, 124, 0, 0.15);
    ">
        <h1 style="
            font-family: 'Outfit', 'Inter', sans-serif;
            font-size: 3rem;
            margin: 0;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">🌻 SEC</h1>
        <p style="
            font-family: 'Inter', sans-serif;
            font-size: 1.25rem;
            margin: 0.5rem 0 0 0;
            font-weight: 400;
            opacity: 0.95;
        ">Sunflower Ensemble Classifier & Agronomic Analyzer</p>
    </div>
    """)

def format_disease_card(class_name: str, confidence: float, info: dict) -> str:
    """Formats disease diagnosis results as an HTML card."""
    severity = info.get("severity", "N/A").lower()
    
    # Determine severity badge style
    if "high" in severity:
        badge_color = "background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2;"
    elif "moderate" in severity:
        badge_color = "background-color: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2;"
    else:
        badge_color = "background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;"

    return f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        font-family: 'Inter', sans-serif;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; font-size: 1.4rem; color: #2c3e50; font-weight: 700;">{class_name}</h3>
            <span style="font-size: 1rem; font-weight: 600; color: #7f8c8d;">Conf: {confidence * 100:.2f}%</span>
        </div>
        <div style="margin-bottom: 0.8rem;">
            <strong style="color: #34495e;">Severity:</strong>
            <span style="
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-left: 5px;
                {badge_color}
            ">{info.get("severity", "N/A")}</span>
        </div>
        <div style="margin-bottom: 0.8rem; line-height: 1.5;">
            <strong style="color: #34495e;">Cause:</strong> 
            <span style="color: #555;">{info.get("cause", "N/A")}</span>
        </div>
        <div style="line-height: 1.5;">
            <strong style="color: #34495e;">Treatment Plan:</strong> 
            <span style="color: #555;">{info.get("treatment", "N/A")}</span>
        </div>
    </div>
    """

def format_stage_card(class_name: str, confidence: float, info: dict) -> str:
    """Formats growth stage classification results as an HTML card."""
    verify_note = info.get("verify_note", "")
    verify_html = ""
    if verify_note:
        verify_html = f"""
        <div style="
            margin-top: 1rem;
            padding: 0.8rem;
            background-color: #fff9c4;
            border-left: 4px solid #fbc02d;
            border-radius: 4px;
            color: #f57f17;
            font-size: 0.9rem;
            line-height: 1.4;
        ">
            {verify_note}
        </div>
        """

    return f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        font-family: 'Inter', sans-serif;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; font-size: 1.4rem; color: #2c3e50; font-weight: 700;">{class_name}</h3>
            <span style="font-size: 1rem; font-weight: 600; color: #7f8c8d;">Conf: {confidence * 100:.2f}%</span>
        </div>
        <div style="margin-bottom: 0.8rem;">
            <strong style="color: #34495e;">Harvest Est:</strong>
            <span style="
                padding: 3px 8px;
                background-color: #e0f7fa;
                color: #006064;
                border: 1px solid #b2ebf2;
                border-radius: 4px;
                font-size: 0.85rem;
                font-weight: 600;
                margin-left: 5px;
            ">{info.get("typical_days_to_harvest", "N/A")}</span>
        </div>
        <div style="line-height: 1.5;">
            <strong style="color: #34495e;">Description:</strong> 
            <span style="color: #555;">{info.get("description", "N/A")}</span>
        </div>
        {verify_html}
    </div>
    """

def format_combined_report(leaf_class: str, flower_class: str, analysis: dict) -> str:
    """Formats the combined LLM analysis as a premium report card."""
    rating = analysis.get("reliability_rating", "N/A").upper()
    
    # Rating color mappings
    if "DISTORTED" in rating:
        badge_style = "background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2;"
        card_border = "border-top: 6px solid #e53935;"
    elif "LOW" in rating:
        badge_style = "background-color: #fff3e0; color: #e65100; border: 1px solid #ffe0b2;"
        card_border = "border-top: 6px solid #fb8c00;"
    elif "MEDIUM" in rating:
        badge_style = "background-color: #fffde7; color: #f57f17; border: 1px solid #fff9c4;"
        card_border = "border-top: 6px solid #fbc02d;"
    else:
        badge_style = "background-color: #e8f5e9; color: #1b5e20; border: 1px solid #c8e6c9;"
        card_border = "border-top: 6px solid #43a047;"

    recommendations = analysis.get("actionable_recommendations", [])
    if isinstance(recommendations, str):
        recommendations = [recommendations]
        
    recs_list_html = "".join([f"<li style='margin-bottom: 0.5rem; color: #4f5d73;'>{rec}</li>" for rec in recommendations])

    return f"""
    <div style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        font-family: 'Inter', sans-serif;
        {card_border}
    ">
        <h2 style="margin-top: 0; color: #1a202c; font-weight: 800; font-size: 1.7rem; border-bottom: 1px solid #edf2f7; padding-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
            <span>Virtual Agronomist Report</span>
            <span style="
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: 700;
                {badge_style}
            ">{rating}</span>
        </h2>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: #2d3748; font-size: 1.1rem; font-weight: 700;">Scientific Pathology Rationale</h4>
            <p style="color: #4a5568; line-height: 1.6; margin: 0; text-align: justify;">{analysis.get("scientific_rationale", "N/A")}</p>
        </div>
        
        <div style="margin-bottom: 1.5rem; padding: 1rem; background-color: #f7fafc; border-radius: 8px; border-left: 4px solid #4a5568;">
            <h4 style="margin: 0 0 0.3rem 0; color: #2d3748; font-size: 1.1rem; font-weight: 700;">Harvest Strategy Implications</h4>
            <p style="color: #4a5568; line-height: 1.5; margin: 0;">{analysis.get("harvest_implications", "N/A")}</p>
        </div>
        
        <div>
            <h4 style="margin: 0 0 0.5rem 0; color: #2d3748; font-size: 1.1rem; font-weight: 700;">Actionable Recommendations</h4>
            <ul style="margin: 0; padding-left: 1.2rem; line-height: 1.6;">
                {recs_list_html}
            </ul>
        </div>
    </div>
    """
