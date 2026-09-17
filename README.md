Smart Study Heatmap - Team 3

Project Overview
A productivity tracker that transforms your daily study hours into a beautiful GitHub-style heatmap. Visualize your consistency, track streaks, and stay motivated every day. Built for students to track, analyze and excel in studies.

Features
- Home Dashboard with Daily Goal, Total Hours, Current Streak, Heatmap 2026
- Add Study with Live Timer, Subject wise tracking, Date selection
- Analytics with Daily, Weekly, Monthly analysis and charts
- Exam Mode to Create custom exams, Add questions, Take exams
- Grand Test with Performance analysis and graphs

Tech Stack
Frontend: Streamlit
Backend: Python
Database: SQLite3
Libraries: Pandas, Matplotlib, streamlit-autorefresh

Setup and Run Commands
1. Clone the repo
git clone https://github.com/Karthik-Kambham/smart-study-heatmap.git
2. Install dependencies
pip install -r requirements.txt
3. Run the app
streamlit run app.py

Environment Variables
No external environment variables required. Uses local SQLite database.

Database Notes
Database Name: study.db
5 Tables:
1. users - user details
2. study_logs - daily study hours and subjects
3. exams - exam details
4. exam_questions - questions for each exam
5. exam_results - user exam results and scores

Team Members and Contributions
Karthik Kambham - Lead Developer - Home, Heatmap, Timer Logic
Shivaprasad - Analytics and Records Module
Benaraji - Exam Mode and Grand Test Module
Ganesh - PPT, Demo Video and Documentation

Live Demo
To be deployed on Streamlit Cloud
