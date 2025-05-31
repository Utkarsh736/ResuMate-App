import gradio as gr
import json
from datetime import datetime
import os
import tempfile

# Import the resume agent (assuming the previous code is saved as resume_agent.py)
from resume_agent import ResumeAgent, get_sample_resume, get_sample_job_description

class GradioResumeApp:
    """Gradio interface for the Resume Optimization Agent"""
    
    def __init__(self):
        self.agent = ResumeAgent()
        self.sample_resume = get_sample_resume()
        self.sample_job_desc = get_sample_job_description()
    
    def process_resume(self, resume_file, resume_text, job_file, job_text, api_key):
        """Process resume optimization request"""
        
        # Validate API key
        if not api_key or api_key.strip() == "":
            return self._create_error_output("❌ Please provide a valid Gemini API key")
        
        # Set API key
        import google.generativeai as genai
        try:
            genai.configure(api_key=api_key.strip())
        except Exception as e:
            return self._create_error_output(f"❌ Invalid API key: {str(e)}")
        
        # Get resume content
        resume_content = self._get_content(resume_file, resume_text, self.sample_resume, "resume")
        if not resume_content:
            return self._create_error_output("❌ No resume content provided")
        
        # Get job description content
        job_content = self._get_content(job_file, job_text, self.sample_job_desc, "job description")
        
        try:
            # Process optimization
            results = self.agent.optimize_resume(resume_content, job_content)
            
            # Format results for display
            return self._format_results(results)
            
        except Exception as e:
            return self._create_error_output(f"❌ Error during optimization: {str(e)}")
    
    def _get_content(self, file, text, sample, content_type):
        """Extract content from file or text input"""
        if file is not None:
            try:
                content = file.decode('utf-8') if isinstance(file, bytes) else file.read()
                return content
            except Exception as e:
                print(f"Error reading {content_type} file: {str(e)}")
        
        if text and text.strip():
            return text.strip()
        
        return sample
    
    def _create_error_output(self, error_message):
        """Create error output tuple"""
        return (
            error_message,  # summary
            "",  # experience_analysis
            "",  # keyword_analysis
            "",  # design_suggestions
            "",  # editing_suggestions
            ""   # full_results
        )
    
    def _format_results(self, results):
        """Format optimization results for Gradio display"""
        
        # New Summary
        new_summary = results.get("new_summary", "No summary generated")
        
        # Experience Analysis
        experience_analysis = ""
        if "experience_matching" in results:
            exp_data = results["experience_matching"]
            if isinstance(exp_data, dict) and "ranked_experiences" in exp_data:
                experience_analysis = "📊 **Experience Relevance Analysis:**\n\n"
                for i, exp in enumerate(exp_data["ranked_experiences"][:3], 1):
                    if isinstance(exp, dict):
                        score = exp.get("relevance_score", "N/A")
                        points = exp.get("matching_points", [])
                        experience_analysis += f"**Experience {i}:** Score {score}/10\n"
                        experience_analysis += f"Key matches: {', '.join(points[:3])}\n\n"
            else:
                experience_analysis = "Experience analysis completed"
        
        # Keyword Analysis
        keyword_analysis = ""
        if "keyword_optimization" in results:
            kw_data = results["keyword_optimization"]
            if isinstance(kw_data, dict):
                ats_score = kw_data.get("ats_score", "N/A")
                missing_kw = kw_data.get("missing_keywords", [])
                keyword_analysis = f"🎯 **ATS Optimization Score:** {ats_score}/100\n\n"
                if missing_kw:
                    keyword_analysis += f"**Missing Keywords:** {', '.join(missing_kw[:10])}\n\n"
                
                recommendations = kw_data.get("recommendations", [])
                if recommendations:
                    keyword_analysis += "**Recommendations:**\n"
                    for rec in recommendations[:3]:
                        keyword_analysis += f"• {rec}\n"
            else:
                keyword_analysis = "Keyword optimization completed"
        
        # Design Suggestions
        design_suggestions = ""
        if "design_suggestions" in results:
            design_data = results["design_suggestions"]
            if isinstance(design_data, dict):
                template = design_data.get("recommended_template", "Standard")
                layout_tips = design_data.get("layout_suggestions", [])
                design_suggestions = f"🎨 **Recommended Template:** {template}\n\n"
                if layout_tips:
                    design_suggestions += "**Layout Suggestions:**\n"
                    for tip in layout_tips[:5]:
                        design_suggestions += f"• {tip}\n"
            else:
                design_suggestions = "Design suggestions generated"
        
        # Editing Suggestions
        editing_suggestions = ""
        if "editing_suggestions" in results:
            edit_data = results["editing_suggestions"]
            if isinstance(edit_data, dict):
                score = edit_data.get("overall_score", "N/A")
                feedback = edit_data.get("summary_feedback", "")
                editing_suggestions = f"✏️ **Overall Quality Score:** {score}/100\n\n"
                if feedback:
                    editing_suggestions += f"**Feedback:** {feedback}\n\n"
                
                grammar_errors = edit_data.get("grammar_errors", [])
                if grammar_errors:
                    editing_suggestions += "**Grammar Improvements:**\n"
                    for error in grammar_errors[:3]:
                        if isinstance(error, dict):
                            original = error.get("original", "")
                            corrected = error.get("corrected", "")
                            editing_suggestions += f"• '{original}' → '{corrected}'\n"
            else:
                editing_suggestions = "Editing analysis completed"
        
        # Full Results (JSON)
        full_results = json.dumps(results, indent=2, default=str)
        
        return (
            new_summary,
            experience_analysis,
            keyword_analysis,
            design_suggestions,
            editing_suggestions,
            full_results
        )
    
    def create_interface(self):
        """Create and return Gradio interface"""
        
        with gr.Blocks(
            title="AI Resume Optimizer",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .main-header {
                text-align: center;
                margin-bottom: 30px;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div class="main-header">
                <h1>🚀 AI Resume Optimization Agent</h1>
                <p>Upload your resume and job description to get AI-powered optimization suggestions</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("<h2>📄 Input</h2>")
                    
                    # API Key input
                    api_key = gr.Textbox(
                        label="🔑 Gemini API Key",
                        placeholder="Enter your Gemini API key here...",
                        type="password",
                        info="Get your free API key from Google AI Studio"
                    )
                    
                    # Resume input
                    with gr.Tab("Resume Upload"):
                        resume_file = gr.File(
                            label="Upload Resume (PDF/TXT/DOCX)",
                            file_types=[".pdf", ".txt", ".docx"]
                        )
                    
                    with gr.Tab("Resume Text"):
                        resume_text = gr.Textbox(
                            label="Paste Resume Text",
                            placeholder="Paste your resume content here...",
                            lines=8,
                            value=self.sample_resume
                        )
                    
                    # Job description input
                    with gr.Tab("Job Description Upload"):
                        job_file = gr.File(
                            label="Upload Job Description",
                            file_types=[".pdf", ".txt", ".docx"]
                        )
                    
                    with gr.Tab("Job Description Text"):
                        job_text = gr.Textbox(
                            label="Paste Job Description",
                            placeholder="Paste job description here...",
                            lines=6,
                            value=self.sample_job_desc
                        )
                    
                    # Optimize button
                    optimize_btn = gr.Button(
                        "🚀 Optimize Resume",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=1):
                    gr.HTML("<h2>📊 Results</h2>")
                    
                    with gr.Tab("✨ New Summary"):
                        summary_output = gr.Textbox(
                            label="Optimized Professional Summary",
                            lines=4,
                            interactive=False
                        )
                    
                    with gr.Tab("📈 Experience Analysis"):
                        experience_output = gr.Markdown(
                            label="Experience Relevance Analysis"
                        )
                    
                    with gr.Tab("🎯 Keywords & ATS"):
                        keyword_output = gr.Markdown(
                            label="Keyword Optimization & ATS Score"
                        )
                    
                    with gr.Tab("🎨 Design Tips"):
                        design_output = gr.Markdown(
                            label="Design & Formatting Suggestions"
                        )
                    
                    with gr.Tab("✏️ Editing Tips"):
                        editing_output = gr.Markdown(
                            label="Grammar & Content Improvements"
                        )
                    
                    with gr.Tab("📋 Full Report"):
                        full_output = gr.Code(
                            label="Complete Analysis (JSON)",
                            language="json"
                        )
            
            # Event handlers
            optimize_btn.click(
                fn=self.process_resume,
                inputs=[resume_file, resume_text, job_file, job_text, api_key],
                outputs=[
                    summary_output,
                    experience_output,
                    keyword_output,
                    design_output,
                    editing_output,
                    full_output
                ]
            )
            
            # Example section
            with gr.Row():
                gr.HTML("""
                <div style="margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 10px;">
                    <h3>💡 Quick Start Guide:</h3>
                    <ol>
                        <li>Get your free Gemini API key from <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a></li>
                        <li>Upload your resume or use the sample provided</li>
                        <li>Add a job description you're targeting (optional)</li>
                        <li>Click "Optimize Resume" to get AI-powered suggestions</li>
                    </ol>
                    <p><strong>Features:</strong> Professional Summary Generation • Experience Matching • ATS Optimization • Design Suggestions • Grammar & Style Improvements</p>
                </div>
                """)
        
        return interface

def main():
    """Launch the Gradio app"""
    app = GradioResumeApp()
    interface = app.create_interface()
    
    # Launch the app
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=True,  # Create public link
        debug=True
    )

if __name__ == "__main__":
    main()
