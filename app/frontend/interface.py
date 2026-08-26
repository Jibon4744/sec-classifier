import os
import logging
import gradio as gr
from PIL import Image
from app.services.classifier import classifier_service
from app.services.llm_service import llm_service
from app.frontend.components import get_header, format_disease_card, format_stage_card, format_combined_report

logger = logging.getLogger(__name__)

# --- Helper callbacks ---

def diagnose_leaf(image):
    if image is None:
        return "<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Please upload a leaf image first.</div>"
    try:
        class_name, confidence, info = classifier_service.predict_disease(image)
        return format_disease_card(class_name, confidence, info)
    except Exception as e:
        logger.error(f"UI Leaf prediction error: {e}")
        return f"<div style='color: #c62828; padding: 1rem; border: 1px solid #ffcdd2; background-color: #ffebee; border-radius: 8px;'>Error during classification: {e}</div>"

def analyze_growth(image):
    if image is None:
        return "<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Please upload a flower head image first.</div>"
    try:
        class_name, confidence, info = classifier_service.predict_growth_stage(image)
        return format_stage_card(class_name, confidence, info)
    except Exception as e:
        logger.error(f"UI Growth prediction error: {e}")
        return f"<div style='color: #c62828; padding: 1rem; border: 1px solid #ffcdd2; background-color: #ffebee; border-radius: 8px;'>Error during classification: {e}</div>"

def analyze_combined(leaf_image, flower_image):
    if leaf_image is None or flower_image is None:
        return "<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Please upload BOTH a leaf image and a flower head image to run the Combined report.</div>"
    try:
        # Run classifiers
        leaf_class, leaf_conf, leaf_info = classifier_service.predict_disease(leaf_image)
        flower_class, flower_conf, flower_info = classifier_service.predict_growth_stage(flower_image)
        
        # Run LLM analysis
        analysis = llm_service.analyze_combined_specimen(
            disease_name=leaf_class,
            disease_conf=leaf_conf,
            disease_info=leaf_info,
            stage_name=flower_class,
            stage_conf=flower_conf,
            stage_info=flower_info
        )
        return format_combined_report(leaf_class, flower_class, analysis)
    except Exception as e:
        logger.error(f"UI Combined analysis error: {e}")
        return f"<div style='color: #c62828; padding: 1rem; border: 1px solid #ffcdd2; background-color: #ffebee; border-radius: 8px;'>Combined analysis failed: {e}</div>"

# --- Interface Builder ---

def build_interface() -> gr.Blocks:
    # Read custom CSS
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, "assets", "style.css")
    css = ""
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()
        except Exception as e:
            logger.warning(f"Could not load custom css file: {e}")

    with gr.Blocks(css=css, title="Sunflower Ensemble Classifier (SEC)") as demo:
        # Render custom header
        get_header()
        
        with gr.Tabs():
            # Mode 1: Leaf Disease Diagnostic
            with gr.Tab("Mode 1: Leaf Disease"):
                gr.Markdown("<h3 style='color: #2c3e50;'>🍃 Leaf Disease Diagnosis</h3><p style='color: #7f8c8d; margin-top: -10px;'>Upload a leaf image to evaluate foliar health, pathogens, and treatment options.</p>")
                with gr.Row():
                    with gr.Column():
                        leaf_input = gr.Image(type="filepath", label="Upload Leaf Image")
                        leaf_btn = gr.Button("Diagnose Leaf Health", variant="primary", elem_classes=["primary"])
                    with gr.Column():
                        leaf_output = gr.HTML(value="<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Results will be generated after uploading and clicking Diagnose.</div>", label="Diagnosis Report")
                leaf_btn.click(fn=diagnose_leaf, inputs=leaf_input, outputs=leaf_output)
                
            # Mode 2: Flower Growth Stage Analysis
            with gr.Tab("Mode 2: Growth Stage"):
                gr.Markdown("<h3 style='color: #2c3e50;'>🌻 Growth Stage Analysis</h3><p style='color: #7f8c8d; margin-top: -10px;'>Upload an image of a sunflower head to identify the developmental stage and typical harvest windows.</p>")
                with gr.Row():
                    with gr.Column():
                        flower_input = gr.Image(type="filepath", label="Upload Flower Head Image")
                        flower_btn = gr.Button("Analyze Growth Stage", variant="primary", elem_classes=["primary"])
                    with gr.Column():
                        flower_output = gr.HTML(value="<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Results will be generated after uploading and clicking Analyze.</div>", label="Timeline Report")
                flower_btn.click(fn=analyze_growth, inputs=flower_input, outputs=flower_output)
                
            # Mode 3: Combined Analysis
            with gr.Tab("Mode 3: Combined Report"):
                gr.Markdown("<h3 style='color: #2c3e50;'>⚖️ Combined Agronomist Evaluation</h3><p style='color: #7f8c8d; margin-top: -10px;'>Provide both leaf and flower images from the same plant to evaluate if developmental characteristics are distorted by disease.</p>")
                with gr.Row():
                    with gr.Column():
                        comb_leaf_input = gr.Image(type="filepath", label="Upload Leaf Image")
                        comb_flower_input = gr.Image(type="filepath", label="Upload Flower Head Image")
                        comb_btn = gr.Button("Run Combined Assessment", variant="primary", elem_classes=["primary"])
                    with gr.Column():
                        comb_output = gr.HTML(value="<div style='color: #7f8c8d; padding: 1rem; text-align: center;'>Virtual agronomist evaluation will be generated after providing both inputs.</div>", label="Agronomist Report")
                comb_btn.click(
                    fn=analyze_combined,
                    inputs=[comb_leaf_input, comb_flower_input],
                    outputs=comb_output
                )
                
    return demo
