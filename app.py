import streamlit as st
import os
from datetime import datetime, timedelta
import tempfile
from utils import (
    extract_text_from_file,
    analyze_submission,
    generate_pdf_report,
    get_evaluation_result
)
from db_utils import init_db, add_submission, get_all_submissions, delete_submission
import pandas as pd
import re
import random
import time
import csv

# Page config
st.set_page_config(
    page_title="SkillShareVerify™",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .floating-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
        40% {transform: translateY(-20px);}
        60% {transform: translateY(-10px);}
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""
if 'page' not in st.session_state:
    st.session_state.page = 'main'

# Title and Logo
st.image('skillshare.jpeg', width=450, caption="SkillShareVerify™")
st.title("SkillShareVerify™")
st.markdown("### Assignment Verification System")
st.markdown("##### By Rohit Krishnan")

# Header
st.markdown("""
<div style='position: absolute; top: 10px; right: 10px; text-align: right; font-size: 0.7em;'>
    <h4.5>Created by <strong>Rohit Krishnan</strong></h4.5>
    <p>
        🔗 
        <a href="https://www.linkedin.com/in/rohit-krishnan-320a5375?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" target="_blank">LinkedIn</a> | 
        <a href="https://www.instagram.com/prof_rohit_/" target="_blank">Instagram</a> | 
        <a href="mailto:rohitkrishnanm@gmail.com">Email</a> | 
        <a href="https://rohitkrishnan.co.in" target="_blank">Website</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Step 1: Student Info Form
if not st.session_state.submitted:
    with st.form("student_info"):
        st.markdown("### Step 1: Student Information")
        student_name = st.text_input("Student Name", key="name_input")
        
        if st.form_submit_button("Login"):
            if student_name:
                st.session_state.student_name = student_name
                st.session_state.submitted = True
                st.rerun()
            else:
                st.error("Please fill in all required fields.")

# Main content after student info submission
if st.session_state.submitted:
    st.markdown(f"## Welcome, {st.session_state.student_name}")
    st.markdown("### SkillShare Assignment Verification application by Rohit Krishnan")
    
    # Step 2: Assignment Question Input
    st.markdown("### Step 2: Assignment Question")
    question_input_method = st.radio(
        "Choose input method:",
        ["Upload File", "Direct Text Input"]
    )
    
    question_text = ""
    if question_input_method == "Upload File":
        question_file = st.file_uploader(
            "Upload Assignment Question",
            type=['pdf', 'docx', 'txt'],
            key="question_upload"
        )
        if question_file:
            if question_file.size > 5_000_000:
                st.warning("File too large! Please upload a file smaller than 5MB.")
                question_file = None
            elif question_file.type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
                st.warning("Invalid file type!")
                question_file = None
            else:
                question_text = extract_text_from_file(question_file)
    else:
        question_text = st.text_area(
            "Enter Assignment Question",
            height=200,
            key="question_text"
        )
    
    # Step 3: Supporting Documents
    st.markdown("### Step 3: Supporting Documents (Optional)")
    supporting_docs = st.file_uploader(
        "📎 Upload Supporting Documents",
        type=['xlsx', 'csv', 'pdf', 'doc', 'docx', 'txt', 'png', 'jpeg', 'jpg'],
        accept_multiple_files=True,
        key="supporting_docs"
    )
    valid_supporting_docs = []
    for doc in supporting_docs:
        if doc.size > 5_000_000:
            st.warning(f"{doc.name} is too large! Skipping.")
            continue
        if doc.type not in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/csv",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
            "image/png",
            "image/jpeg"
        ]:
            st.warning(f"{doc.name} is not a supported file type! Skipping.")
            continue
        valid_supporting_docs.append(doc)
    
    # Step 4: Final Submission
    st.markdown("### Step 4: Final Output (Required)")
    final_output = st.file_uploader(
        "📤 Upload Final Output",
        type=['ipynb', 'py', 'pdf'],
        key="final_output"
    )
    if final_output:
        if final_output.size > 5_000_000:
            st.warning("Final output file too large! Please upload a file smaller than 5MB.")
            final_output = None
        elif final_output.type not in [
            "application/pdf",
            "application/x-ipynb+json",
            "application/octet-stream",  # Accepts .ipynb uploads
            "text/x-python"
        ]:
            st.warning("Invalid final output file type!")
            final_output = None

    # CAPTCHA before submit
    if 'captcha_a' not in st.session_state:
        st.session_state.captcha_a = random.randint(1, 10)
    if 'captcha_b' not in st.session_state:
        st.session_state.captcha_b = random.randint(1, 10)
    st.markdown('#### CAPTCHA:')
    st.write(f"What is {st.session_state.captcha_a} + {st.session_state.captcha_b}?")
    captcha_answer = st.text_input("Enter your answer:", key="captcha_input")

    # Submit button
    if st.button("Submit Assignment", disabled=st.session_state.get('evaluated', False), key="submit_button", help="Submit your assignment"):
        if not question_text:
            st.error("Please provide the assignment question.")
        elif not final_output:
            st.error("Please upload your final output.")
        elif not captcha_answer or not captcha_answer.isdigit() or int(captcha_answer) != (st.session_state.captcha_a + st.session_state.captcha_b):
            st.error("CAPTCHA incorrect. Please try again.")
            st.session_state.captcha_a = random.randint(1, 10)
            st.session_state.captcha_b = random.randint(1, 10)
        else:
            with st.spinner("🧠 Analyzing..."):
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress.progress(i + 1)
                # Extract final output text
                final_output_text = extract_text_from_file(final_output)
                
                # PDF + Code Checker Integration
                if final_output.type == "application/x-ipynb+json":
                    import nbformat
                    nb = nbformat.reads(final_output_text, as_version=4)
                    has_def = any("def " in cell.source for cell in nb.cells if cell.cell_type == "code")
                    has_import = any("import " in cell.source for cell in nb.cells if cell.cell_type == "code")
                    has_output = any(cell.outputs for cell in nb.cells if cell.cell_type == "code")
                    st.markdown("### 📊 Notebook Analysis")
                    st.write(f"Contains function definitions: {has_def}")
                    st.write(f"Contains imports: {has_import}")
                    st.write(f"Contains output cells: {has_output}")
                elif final_output.type == "text/x-python":
                    import ast
                    try:
                        tree = ast.parse(final_output_text)
                        has_def = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
                        has_import = any(isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
                        st.markdown("### 📊 Python File Analysis")
                        st.write(f"Contains function definitions: {has_def}")
                        st.write(f"Contains imports: {has_import}")
                    except Exception as e:
                        st.error(f"Error analyzing Python file: {e}")
                
                # Extract supporting docs text
                supporting_docs_text = ""
                for doc in valid_supporting_docs:
                    supporting_docs_text += extract_text_from_file(doc) + "\n\n"
                
                # Get GPT analysis
                analysis = analyze_submission(
                    question_text,
                    supporting_docs_text,
                    final_output_text
                )
                
                try:
                    # Try to extract from TOTAL SCORE first, then SCORE, allowing for /10 or whitespace after the number
                    match = re.search(r"TOTAL SCORE:\s*([0-9]+(?:\.[0-9]+)?)\s*/?10?", analysis, re.IGNORECASE)
                    if not match:
                        match = re.search(r"SCORE:\s*([0-9]+(?:\.[0-9]+)?)\s*/?10?", analysis, re.IGNORECASE)
                    if match:
                        score = float(match.group(1))
                    else:
                        score = 0
                except Exception:
                    score = 0
                
                evaluation_result = get_evaluation_result(score)
                
                # Generate PDF report
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    generate_pdf_report(
                        st.session_state.student_name,
                        '',  # Institution removed
                        question_text[:200] + "...",  # Summary
                        analysis,
                        score,
                        tmp.name
                    )
                    tmp.close()  # Ensure the file is closed
                    
                    # Read the PDF file
                    with open(tmp.name, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    # Delete the temporary file
                    try:
                        os.unlink(tmp.name)
                    except PermissionError:
                        st.warning("Could not delete temporary file. It will be cleaned up automatically.")
                    
                    # Display results
                    st.markdown("### Analysis Results")
                    with st.expander("View Full Analysis", expanded=True):
                        st.markdown(analysis)
                    
                    st.markdown(f"### Score: {score:.1f}/10")
                    st.markdown(f"### Result: {evaluation_result}")
                    
                    # Stylish Result Feedback Display
                    if score >= 6:
                        st.success("✅ **Pass!** Your work meets the expected criteria.")
                    elif 4 <= score < 6:
                        st.warning("⚠️ **Can Improve.** Please review the suggestions for improvement.")
                    else:
                        st.error("❌ **Rework Required.** Please revise your submission carefully.")
                    
                    # Download PDF button
                    st.download_button(
                        "Download PDF Report",
                        pdf_bytes,
                        file_name=f"SkillShareVerify_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                
                add_submission(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    st.session_state.student_name,
                    '',  # Institution removed
                    question_text[:200] + "...",
                    score,
                    evaluation_result
                )
                
                st.success("Submission logged locally!")
                st.session_state.evaluated = True
                st.success("Analysis complete! You can download your report above.")

    # Go back to Main Menu button
    if st.button("Go back to Main Menu"):
        st.session_state.page = 'main'
        st.session_state.submitted = False
        st.rerun()

def show_trainer_dashboard():
    if st.button("⬅️ Back to Main Page"):
        st.session_state.page = 'main'
        st.rerun()
    rows = get_all_submissions()
    if not rows:
        st.info("No student submissions yet.")
        return
    df = pd.DataFrame(rows, columns=[
        "ID", "Timestamp", "Student Name", "Institution", "Question Summary", "Score", "Evaluation Result"
    ])
    df.insert(0, "SL No", range(1, len(df) + 1))
    st.markdown("## 📊 Student Submissions Dashboard")

    # --- Analytics ---
    st.markdown("### 📈 Submission Analytics")
    # Submissions over time (by date)
    df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
    submissions_by_date = df.groupby('Date').size()
    st.bar_chart(submissions_by_date, use_container_width=True)

    # Pass/Rework breakdown
    result_counts = df['Evaluation Result'].value_counts()
    st.bar_chart(result_counts, use_container_width=True)

    # Display table with delete buttons
    for i, row in df.iterrows():
        cols = st.columns([1, 2, 2, 3, 1, 2, 2, 1])
        cols[0].write(row["SL No"])
        cols[1].write(row["Student Name"])
        cols[2].write(row["Question Summary"])
        cols[3].write(row["Score"])
        cols[4].write(row["Evaluation Result"])
        cols[5].write(row["Timestamp"])
        if cols[6].button("Delete", key=f"delete_{row['ID']}"):
            delete_submission(row["ID"])
            remove_submission_from_csv(row["ID"])
            st.rerun()
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name='student_submissions.csv',
        mime='text/csv'
    )

    # Student Leaderboard
    st.markdown("### 🏆 Student Leaderboard (Current Week)")
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    leaderboard_df = df[pd.to_datetime(df['Timestamp']).dt.date >= pd.to_datetime(one_week_ago).date()]
    leaderboard_df = leaderboard_df.sort_values('Score', ascending=False)
    st.dataframe(leaderboard_df[['Student Name', 'Score', 'Evaluation Result']], use_container_width=True)

# Trainer-only section in sidebar
with st.sidebar:
    st.markdown("### Instructions Manual")
    with st.expander("ℹ️ Instructions for Submission"):
        st.markdown("""
### 📌 General Instructions
Please follow the steps below to correctly submit your assignment for evaluation.

---

### 👤 Step 1: Student Details
- Enter your **Full Name**
- Select your **Institution location** (BIA Kottayam or BIA Trivandrum)

---

### 📘 Step 2: Assignment Question
You have two options to provide your assignment question:
1. Upload a file (`.pdf`, `.docx`, `.txt`)
2. Or type/paste the question in the provided text box

---

### 📎 Step 3: Supporting Documents (Optional)
- You may attach any extra files that support your work (e.g., datasets, notes, screenshots)
- Accepted formats: `.csv`, `.xlsx`, `.pdf`, `.doc`, `.docx`, `.txt`, `.png`, `.jpeg`, `.jpg`

---

### 📤 Step 4: Final Submission (Required)
- Upload your final assignment outcome for evaluation
- Accepted formats: `.ipynb`, `.py`, `.pdf`
- You may only submit **once per session**

---

### 🧠 Evaluation Criteria (Powered by AI)
Your submission will be analyzed based on:
- Relevance to the assignment question
- Structure and logic of your answer or code
- Use of supporting materials (if provided)

The AI will:
- Assign a **score out of 10**
- Classify the result as:
  - ✅ **Pass** (Score ≥ 6)
  - ⚠️ **Can Improve** (Score 4–5)
  - ❌ **Rework Required** (Score < 4)
- Provide a downloadable feedback report

---

### 📥 After Submission
- Your result will be stored internally
- You will receive a **PDF report**
- Resubmission is **not allowed in the same session**

If you encounter any issues, please contact **Rohit Krishnan**.

---
""")
    with st.form("trainer_login"):
        trainer_password = st.text_input("Trainer Password", type="password")
        login_btn = st.form_submit_button("Login", help="Login to access trainer dashboard")
    if login_btn and trainer_password == st.secrets["trainer"]["password"]:
        st.session_state.page = 'trainer_dashboard'
        st.rerun()

# Trainer Dashboard as a separate page
if st.session_state.page == 'trainer_dashboard':
    show_trainer_dashboard()
    st.stop()

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 50px;'>
    <p>Created by <strong>Rohit Krishnan</strong></p>
    <p>
        🔗 
        <a href="https://www.linkedin.com/in/rohit-krishnan-320a5375?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app" target="_blank">LinkedIn</a> | 
        <a href="https://www.instagram.com/prof_rohit_/" target="_blank">Instagram</a> | 
        <a href="mailto:rohitkrishnanm@gmail.com">Email</a> | 
        <a href="https://rohitkrishnan.co.in" target="_blank">Website</a>
    </p>
</div>
""", unsafe_allow_html=True)

init_db() 

CSV_DIR = 'submission_records'
CSV_PATH = os.path.join(CSV_DIR, 'submissions.csv')
os.makedirs(CSV_DIR, exist_ok=True)

CSV_FIELDS = ["ID", "Timestamp", "Student Name", "Institution", "Question Summary", "Score", "Evaluation Result"]

def append_submission_to_csv(row):
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def remove_submission_from_csv(submission_id):
    if not os.path.isfile(CSV_PATH):
        return
    rows = []
    with open(CSV_PATH, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if str(row["ID"]) != str(submission_id):
                rows.append(row)
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows) 
                
