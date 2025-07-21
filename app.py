import streamlit as st
import PyPDF2
from docx import Document
import openai
from openai import OpenAI
import os

# Initialize the OpenAI client with the API key from Streamlit's secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def validate_resume(file):
    """
    Validates if the uploaded file is a resume.
    """
    if file is not None:
        # Check file extension
        file_extension = os.path.splitext(file.name)[1].lower()
        if file_extension not in [".pdf", ".docx"]:
            st.error("Invalid file format. Please upload a PDF or DOCX file.")
            return None, None

        # Extract text from the file
        text = ""
        if file_extension == ".pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            except Exception as e:
                st.error(f"Error reading PDF file: {e}")
                return None, None
        elif file_extension == ".docx":
            try:
                doc = Document(file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception as e:
                st.error(f"Error reading DOCX file: {e}")
                return None, None

        # Basic validation (check for keywords)
        resume_keywords = ["resume", "curriculum vitae", "experience", "education", "skills"]
        if any(keyword in text.lower() for keyword in resume_keywords):
            return text, file.name
        else:
            st.warning("The uploaded file does not appear to be a resume.")
            return None, None
    return None, None

def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("Interview Question Generator")

    # File uploader
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

    if uploaded_file:
        resume_text, file_name = validate_resume(uploaded_file)
        if resume_text:
            st.success(f"Successfully uploaded and validated resume: {file_name}")

            # --- New structured selection logic ---
            exam_display_to_value = {
                "MBA Roles (for B-School aspirants)": "MBA Entrance Exams",
                "Engineering Roles": "Engineering & Science",
                "Banking/Government/SSC Roles": "Government/Bank/SSC Exams",
                "Law & Management UG Roles": "Law and IPM",
                "Medical": "Medical",
                "International Exam Roles": "International Exams",
                "Foundation Level (High School)": "Foundation/School Level",
            }

            structured_sub_categories = {
                "MBA Roles (for B-School aspirants)": [
                    "CAT Aspirant", "MAH-MBA/MMS-CET Aspirant", "XAT Aspirant",
                    "CMAT Aspirant", "MAT Aspirant", "GMAT Aspirant"
                ],
                "Engineering Roles": ["JEE Aspirant", "GATE Aspirant"],
                "Banking/Government/SSC Roles": [
                    "Bank PO/Clerk Aspirant", "SSC CGL Aspirant", "Campus Recruitment Training (CRT) Aspirant"
                ],
                "Law & Management UG Roles": ["CLAT Aspirant", "IPM (IIM) Aspirant"],
                "Medical": ["NEET Aspirant"],
                "International Exam Roles": ["GRE Aspirant", "GMAT Aspirant"],
                "Foundation Level (High School)": ["IIT Foundation Aspirant"],
            }

            # Exam selection
            exam_options_display = list(exam_display_to_value.keys())
            selected_exam_display = st.selectbox("Choose an exam:", exam_options_display)

            # SubCategory selection based on exam
            sub_category_options_display = structured_sub_categories[selected_exam_display]
            selected_sub_category_display = st.selectbox("Choose a sub-category:", sub_category_options_display)

            if st.button("Generate Questions"):
                # Generate questions using OpenAI
                prompt = f"""
You are an expert interviewer preparing questions for a '{selected_sub_category_display}' aspirant.
A candidate has submitted the following resume for evaluation:

--- RESUME START ---
{resume_text}
--- RESUME END ---

Your task is to generate 10 insightful interview questions. These questions should be directly based on the candidate's resume (their projects, experiences, and skills) but framed within the context of the '{selected_exam_display}' exam. The goal is to assess how well the candidate can apply their practical experience to the theoretical concepts and problem-solving skills required for this exam.

Generate the questions now.
"""

                st.write("### Generated Questions")
                try:
                    response = client.completions.create(
                        model="gpt-3.5-turbo-instruct",
                        prompt=prompt,
                        max_tokens=500
                    )
                    st.write(response.choices[0].text.strip())
                except Exception as e:
                    st.error(f"Error generating questions from OpenAI: {e}")

if __name__ == "__main__":
    main() 