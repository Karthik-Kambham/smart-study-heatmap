import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import time

st.set_page_config(page_title="Study Heat Map", layout="wide", page_icon="🔥")

def init_db():
    conn = sqlite3.connect('study.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS studies 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, subject TEXT, topic TEXT, 
                  hours REAL, date TEXT, timestamp TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)""")
    c.execute("INSERT OR IGNORE INTO users VALUES ('Karthik', '1234')")
    conn.commit()
    return conn

conn = init_db()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = "Karthik"
    st.session_state.start_time = None

if not st.session_state.logged_in:
    st.title("🔥 Study Heat Map - Login")
    u = st.text_input("Username", "Karthik")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        if cur.fetchone():
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Wrong! Use Karthik / 1234")
    st.stop()

with st.sidebar:
    st.title("🔥 Study Heat Map")
    st.write(f"Welcome {st.session_state.username}")
    st.divider()
    goal = st.number_input("Annual Goal (Hours)", value=490)
    st.divider()
    menu = st.radio("Go to", ["🏠 Home", "➕ Add Study", "📄 Records", "🔥 Heatmap", "📊 Analysis", "📝 Exam Mode", "🏆 Grand Test"])
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

if "Home" in menu:
    st.title("Welcome to Study Tracker")
    df = pd.read_sql(f"SELECT * FROM studies WHERE username='{st.session_state.username}'", conn)
    if not df.empty:
        total = df['hours'].sum()
        st.metric("Total Hours", f"{total:.2f} / {goal} hrs")
        st.progress(min(total/goal, 1.0))
    else:
        st.info("No study data yet. Go to Add Study!")

elif "Add Study" in menu:
    st.title("Add Study Session")
    subject = st.selectbox("Subject", ["Python", "Maths", "DSA", "DBMS", "OS", "Networking"])
    topic = st.text_input("Topic", "Loops")
    if st.button("▶️ Start Session"):
        st.session_state.start_time = time.time()
        st.success("Started!")
    if st.button("⏹️ End & Save"):
        if st.session_state.start_time:
            hrs = max((time.time() - st.session_state.start_time) / 3600, 0.01)
            st.session_state.start_time = None
        else:
            hrs = st.number_input("Hours", 0.01, 10.0, 0.5)
        cur = conn.cursor()
        cur.execute("INSERT INTO studies VALUES (NULL,?,?,?,?,?,?)",
                    (st.session_state.username, subject, topic, hrs, str(date.today()), str(datetime.now())))
        conn.commit()
        st.success(f"Saved {hrs:.3f} hrs")

elif "Records" in menu:
    st.title("Study Records")
    df = pd.read_sql(f"SELECT * FROM studies WHERE username='{st.session_state.username}' ORDER BY id DESC", conn)
    st.dataframe(df, use_container_width=True)

elif "Heatmap" in menu:
    st.title("Study Heatmap")
    df = pd.read_sql(f"SELECT * FROM studies WHERE username='{st.session_state.username}'", conn)
    if df.empty:
        st.info("No data yet!")
    else:
        # NO GAP VERSION - Charts attached
        daily = df.groupby('date')['hours'].sum().reset_index()
        fig = px.density_heatmap(daily, x='date', y='hours', z='hours', title="Daily Study")
        fig.update_layout(height=300, margin=dict(t=30, b=30, l=50, r=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # Gap div tesesa - ippudu gap radu!
        
        sub_df = df.groupby('subject')['hours'].sum().reset_index()
        fig2 = px.bar(sub_df, x='subject', y='hours', color='subject', title="Subject Hours")
        fig2.update_layout(height=300, margin=dict(t=30, b=30, l=50, r=20), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

elif "Analysis" in menu:
    st.title(f"Analysis - {datetime.now().strftime('%B %Y')}")
    df = pd.read_sql(f"SELECT * FROM studies WHERE username='{st.session_state.username}'", conn)
    if df.empty:
        st.info("No study data yet")
    else:
        fig = px.pie(df, values='hours', names='subject', title="Time Distribution")
        fig.update_layout(height=300, margin=dict(t=30, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

else:
    st.title(menu)
    st.write("Coming soon...")
