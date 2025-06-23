# SkillShareVerify™ 🎓
### AI-Powered Assignment Evaluation System for SkillShare Students  
**Developed by [Rohit Krishnan](https://rohitkrishnan.co.in)**

---

## 📌 Overview

**SkillShareVerify™** is a Streamlit-based smart submission and analysis app designed for the **SKILLSHARE**. It allows students to upload assignments, receive instant feedback powered by **OpenAI GPT**, and download a personalized report.

This system is built to automate:
- Assignment submission validation
- GPT-driven content analysis
- Intelligent grading and classification (Pass / Rework / Can Improve)
- Trainer analytics and admin control

---

## 🚀 Features

### 🎓 Student Features
- Upload assignment question (file or text)
- Optional upload of supporting documents
- Upload final answer (PDF, `.ipynb`, `.py`)
- Get **AI-generated feedback, score (0–10)**, and result classification
- Download **PDF report** with analysis

### 🧠 AI Evaluation
- Uses **OpenAI GPT** to analyze:
  - Relevance to question
  - Technical correctness
  - Structure and clarity
- Automatically scores submission out of 10
- Classifies as:
  - ✅ Pass (Score ≥ 6)
  - ⚠️ Can Improve (Score 4–5)
  - ❌ Rework (Score < 4)

### 🔐 Trainer Dashboard
- Trainer login (via password)
- View all student submissions
- Visualize trends (weekly charts, result stats)
- Leaderboard view
- Delete records, download CSV



## 🌟 Features

- **Student Authentication**: Secure login system for students
- **Multi-format Support**: Accepts various file formats for assignments and supporting documents
- **AI-Powered Analysis**: Intelligent evaluation of submissions
- **PDF Report Generation**: Detailed feedback reports in PDF format
- **Trainer Dashboard**: Comprehensive analytics and submission management
- **Real-time Analytics**: Visual representation of submission statistics
- **Student Leaderboard**: Weekly performance tracking
- **Secure CAPTCHA**: Prevents automated submissions

## 🛠️ Technologies Used

- Python 3.x
- Streamlit
- Pandas
- SQLite (for local storage)
- PDF Generation Libraries
- Natural Language Processing (for analysis)

## 📋 Prerequisites

- Python 3.x
- pip (Python package installer)
- Git

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skillshareverify.git
cd skillshareverify
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## 💻 Usage

1. **Student Login**
   - Enter your full name
   - Select your institution location

2. **Assignment Submission**
   - Upload or input assignment question
   - Add supporting documents (optional)
   - Upload final output
   - Complete CAPTCHA verification
   - Submit for evaluation

3. **Trainer Access**
   - Use trainer credentials to access dashboard
   - View submission analytics
   - Download submission reports
   - Manage student submissions

## 🔒 Security

- Secure password protection for trainer access
- CAPTCHA verification for submissions
- File size and type validation
- Secure session management

## 📊 Features for Trainers

- Real-time submission tracking
- Performance analytics
- Student leaderboard
- Export functionality
- Submission management tools

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Rohit Krishnan**
- LinkedIn: [Rohit Krishnan](https://www.linkedin.com/in/rohit-krishnan-320a5375)
- Instagram: [@prof_rohit_](https://www.instagram.com/prof_rohit_/)
- Email: rohitkrishnanm@gmail.com
- Website: [rohitkrishnan.co.in](https://rohitkrishnan.co.in)

## 🙏 Acknowledgments

- SkillShare (Business Intelligence Academy)
- Streamlit community
- All contributors and users of the system

## 📞 Support

For support, please contact Rohit Krishnan at rohitkrishnanm@gmail.com 
