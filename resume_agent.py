import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")

@dataclass
class ResumeData:
    """Data structure to hold resume information"""
    personal_info: Dict
    summary: str
    experiences: List[Dict]
    skills: List[str]
    education: List[Dict]
    raw_text: str

@dataclass
class JobDescription:
    """Data structure for job descriptions"""
    title: str
    company: str
    description: str
    requirements: List[str]
    keywords: List[str]

class Agent(ABC):
    """Base agent class"""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)
    
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

class SummaryAgent(Agent):
    """Agent responsible for creating compelling professional summaries"""
    
    def execute(self, resume_data: ResumeData, job_desc: Optional[JobDescription] = None) -> str:
        context = f"""
        Personal Info: {resume_data.personal_info}
        Experience: {resume_data.experiences}
        Skills: {resume_data.skills}
        Education: {resume_data.education}
        """
        
        job_context = ""
        if job_desc:
            job_context = f"""
            Target Job: {job_desc.title} at {job_desc.company}
            Job Requirements: {job_desc.requirements}
            """
        
        prompt = f"""
        Create a compelling professional summary (2-3 sentences) based on this resume information:
        {context}
        
        {job_context}
        
        Guidelines:
        - Highlight unique value proposition
        - Use action-oriented language
        - Focus on achievements and impact
        - Keep it concise and engaging
        - If job description provided, align with role requirements
        
        Return only the professional summary text.
        """
        
        return self.generate_response(prompt)

class ExperienceMatchingAgent(Agent):
    """Agent for matching experiences to job descriptions"""
    
    def execute(self, resume_data: ResumeData, job_desc: JobDescription) -> List[Dict]:
        experiences_text = json.dumps(resume_data.experiences, indent=2)
        
        prompt = f"""
        Analyze these work experiences and rank them by relevance to the target job:
        
        EXPERIENCES:
        {experiences_text}
        
        TARGET JOB:
        Title: {job_desc.title}
        Company: {job_desc.company}
        Description: {job_desc.description}
        Requirements: {job_desc.requirements}
        
        For each experience, provide:
        1. Relevance score (1-10)
        2. Key matching points
        3. Suggested improvements for better alignment
        4. Recommended order for resume
        
        Return as JSON format:
        {{
            "ranked_experiences": [
                {{
                    "original_experience": {{...}},
                    "relevance_score": 8,
                    "matching_points": ["point1", "point2"],
                    "suggested_improvements": ["improvement1", "improvement2"],
                    "recommended_position": 1
                }}
            ]
        }}
        """
        
        response = self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse experience matching results"}

class KeywordOptimizationAgent(Agent):
    """Agent for optimizing ATS keywords"""
    
    def execute(self, resume_data: ResumeData, job_desc: JobDescription) -> Dict:
        prompt = f"""
        Analyze the resume and job description to optimize ATS keywords:
        
        RESUME CONTENT:
        Summary: {resume_data.summary}
        Skills: {resume_data.skills}
        Experiences: {json.dumps(resume_data.experiences)}
        
        JOB DESCRIPTION:
        {job_desc.description}
        Requirements: {job_desc.requirements}
        
        Provide:
        1. Missing critical keywords from job description
        2. Keyword density analysis
        3. Suggested keyword placements
        4. Industry-specific terms to include
        5. ATS optimization score (1-100)
        
        Return as JSON:
        {{
            "missing_keywords": ["keyword1", "keyword2"],
            "current_keyword_density": {{"keyword": "frequency"}},
            "suggested_placements": [
                {{
                    "keyword": "Python",
                    "sections": ["skills", "experience"],
                    "context": "Add to technical skills section"
                }}
            ],
            "industry_terms": ["term1", "term2"],
            "ats_score": 75,
            "recommendations": ["rec1", "rec2"]
        }}
        """
        
        response = self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse keyword optimization results"}

class DesignAgent(Agent):
    """Agent for design and formatting suggestions"""
    
    def execute(self, resume_data: ResumeData, job_desc: Optional[JobDescription] = None) -> Dict:
        industry = job_desc.title.split()[0] if job_desc else "General"
        
        prompt = f"""
        Suggest design and formatting improvements for a {industry} professional's resume:
        
        CURRENT RESUME STRUCTURE:
        - Personal Info: {len(resume_data.personal_info)} fields
        - Experiences: {len(resume_data.experiences)} positions
        - Skills: {len(resume_data.skills)} skills listed
        - Education: {len(resume_data.education)} entries
        
        Consider:
        1. Industry standards for {industry}
        2. ATS-friendly formatting
        3. Visual hierarchy and readability
        4. Professional appearance
        5. Length optimization
        
        Return JSON with:
        {{
            "recommended_template": "template_name",
            "layout_suggestions": ["suggestion1", "suggestion2"],
            "formatting_rules": ["rule1", "rule2"],
            "color_scheme": "color_description",
            "typography": "font_recommendations",
            "sections_order": ["section1", "section2", "section3"],
            "design_tips": ["tip1", "tip2"]
        }}
        """
        
        response = self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse design suggestions"}

class EditingAgent(Agent):
    """Agent for grammar, punctuation, and content improvement"""
    
    def execute(self, text: str) -> Dict:
        prompt = f"""
        Analyze this resume text for improvements:
        
        TEXT TO REVIEW:
        {text}
        
        Check for:
        1. Grammar and punctuation errors
        2. Clarity and conciseness
        3. Action verb usage
        4. Quantifiable achievements
        5. Professional tone
        6. Consistency in formatting
        
        Return JSON:
        {{
            "grammar_errors": [
                {{
                    "original": "original text",
                    "corrected": "corrected text",
                    "explanation": "reason for change"
                }}
            ],
            "clarity_improvements": [
                {{
                    "original": "original text",
                    "improved": "improved text",
                    "reason": "why it's better"
                }}
            ],
            "action_verb_suggestions": ["verb1", "verb2"],
            "quantification_opportunities": ["opportunity1", "opportunity2"],
            "overall_score": 85,
            "summary_feedback": "Overall assessment"
        }}
        """
        
        response = self.generate_response(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse editing suggestions"}

class ResumeAgent:
    """Main orchestrating agent that coordinates all sub-agents"""
    
    def __init__(self):
        self.summary_agent = SummaryAgent()
        self.experience_agent = ExperienceMatchingAgent()
        self.keyword_agent = KeywordOptimizationAgent()
        self.design_agent = DesignAgent()
        self.editing_agent = EditingAgent()
    
    def parse_resume(self, resume_text: str) -> ResumeData:
        """Simple resume parsing - can be enhanced with proper NLP"""
        # This is a simplified parser - in production, you'd use more sophisticated parsing
        lines = resume_text.split('\n')
        
        # Extract basic sections (this is a simplified implementation)
        personal_info = {"name": "John Doe", "email": "john@email.com"}  # Placeholder
        summary = ""
        experiences = []
        skills = []
        education = []
        
        # Simple pattern matching (enhance as needed)
        current_section = None
        for line in lines:
            line = line.strip()
            if re.match(r'(summary|profile|objective)', line.lower()):
                current_section = 'summary'
            elif re.match(r'(experience|work|employment)', line.lower()):
                current_section = 'experience'
            elif re.match(r'(skills|technical)', line.lower()):
                current_section = 'skills'
            elif re.match(r'(education|academic)', line.lower()):
                current_section = 'education'
            elif line and current_section:
                if current_section == 'summary':
                    summary += line + " "
                elif current_section == 'skills':
                    skills.extend([skill.strip() for skill in line.split(',')])
        
        return ResumeData(
            personal_info=personal_info,
            summary=summary.strip(),
            experiences=experiences,
            skills=skills,
            education=education,
            raw_text=resume_text
        )
    
    def optimize_resume(self, resume_text: str, job_description: Optional[str] = None) -> Dict:
        """Main method to optimize resume using all agents"""
        
        # Parse resume
        resume_data = self.parse_resume(resume_text)
        
        # Parse job description if provided
        job_desc = None
        if job_description:
            job_desc = JobDescription(
                title="Target Position",
                company="Target Company",
                description=job_description,
                requirements=[req.strip() for req in job_description.split('.') if req.strip()],
                keywords=[]
            )
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "original_resume": resume_data.__dict__,
        }
        
        # Generate new summary
        print("🔄 Generating compelling summary...")
        results["new_summary"] = self.summary_agent.execute(resume_data, job_desc)
        
        # Match experiences to job
        if job_desc:
            print("🔄 Analyzing experience relevance...")
            results["experience_matching"] = self.experience_agent.execute(resume_data, job_desc)
            
            print("🔄 Optimizing keywords for ATS...")
            results["keyword_optimization"] = self.keyword_agent.execute(resume_data, job_desc)
        
        # Design suggestions
        print("🔄 Generating design recommendations...")
        results["design_suggestions"] = self.design_agent.execute(resume_data, job_desc)
        
        # Edit and improve
        print("🔄 Analyzing content for improvements...")
        results["editing_suggestions"] = self.editing_agent.execute(resume_text)
        
        return results

# File handling utilities
def read_file(file_path: str) -> str:
    """Read content from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return ""
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return ""

def get_sample_resume() -> str:
    """Return sample resume text"""
    return """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    
    SUMMARY
    Experienced software developer with 5 years in web development and system design.
    
    EXPERIENCE
    Software Developer at TechCorp (2019-2024)
    - Developed web applications using Python and JavaScript
    - Worked with databases and APIs
    - Collaborated with team members on agile projects
    - Maintained code quality and performed code reviews
    
    Senior Developer Intern at StartupXYZ (2018-2019)
    - Built responsive web interfaces using React
    - Integrated third-party APIs and services
    - Participated in daily standups and sprint planning
    
    SKILLS
    Python, JavaScript, React, SQL, Git, Docker, AWS, REST APIs
    
    EDUCATION
    BS Computer Science, University XYZ (2019)
    GPA: 3.7/4.0
    """

def get_sample_job_description() -> str:
    """Return sample job description"""
    return """
    Senior Python Developer position at InnovaTech
    
    We are looking for an experienced Python developer with expertise in Django, 
    REST APIs, database optimization, and cloud technologies. The ideal candidate 
    should have 3+ years of experience, strong problem-solving skills, and 
    experience with AWS or Azure.
    
    Requirements:
    - 3+ years of Python development experience
    - Strong knowledge of Django framework
    - Experience with REST API development
    - Database design and optimization skills
    - Cloud platform experience (AWS/Azure)
    - Git version control
    - Agile development methodology
    - Strong communication skills
    """

# Example usage and testing
def main():
    """Main function with file upload capability"""
    
    print("🚀 AI Resume Optimization Agent")
    print("=" * 50)
    
    # Get resume content
    resume_file = input("📄 Enter resume file path (or press Enter for sample): ").strip()
    if resume_file and resume_file != "":
        resume_text = read_file(resume_file)
        if not resume_text:
            print("📄 Using sample resume instead...")
            resume_text = get_sample_resume()
    else:
        print("📄 Using sample resume...")
        resume_text = get_sample_resume()
    
    # Get job description
    job_file = input("💼 Enter job description file path (or press Enter for sample): ").strip()
    if job_file and job_file != "":
        job_description = read_file(job_file)
        if not job_description:
            print("💼 Using sample job description instead...")
            job_description = get_sample_job_description()
    else:
        print("💼 Using sample job description...")
        job_description = get_sample_job_description()
    
    # Initialize the agent
    agent = ResumeAgent()
    
    print("\n🔄 Starting Resume Optimization...")
    print("=" * 50)
    
    # Optimize resume
    results = agent.optimize_resume(resume_text, job_description)
    
    print("\n✅ Optimization Complete!")
    print("=" * 50)
    
    # Display results
    print(f"\n📝 NEW SUMMARY:")
    print(results.get("new_summary", ""))
    
    if "keyword_optimization" in results:
        keyword_data = results["keyword_optimization"]
        if isinstance(keyword_data, dict) and "ats_score" in keyword_data:
            print(f"\n🎯 ATS SCORE: {keyword_data['ats_score']}/100")
    
    if "design_suggestions" in results:
        design_data = results["design_suggestions"]
        if isinstance(design_data, dict) and "recommended_template" in design_data:
            print(f"\n🎨 RECOMMENDED TEMPLATE: {design_data['recommended_template']}")
    
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"Full results saved with timestamp: {results['timestamp']}")
    
    # Save results to file
    output_file = f"resume_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")
    
    return results

if __name__ == "__main__":
    # Note: Replace "YOUR_GEMINI_API_KEY" with your actual API key
    main()
