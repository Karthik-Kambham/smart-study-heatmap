import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Smart Study Heat Map", layout="wide", page_icon="🔥")
st.markdown("""
<style>
.stApp { background: #080e1a!important; }
[data-testid="stHeader"]{display:none;}
.main.block-container{padding-top:0.5rem!important; max-width:98%!important;}
.card { background: #141b2d; border: 1px solid #1f2c42; border-radius: 18px; padding: 18px 20px; }
.login-title { color: #3b82f6!important; font-weight: 800; font-size: 20px; margin-bottom: 20px; }
[data-testid="stWidgetLabel"] p { color: #3b82f6!important; font-weight: 700!important; font-size: 13px!important; }
</style>
""", unsafe_allow_html=True)

conn = sqlite3.connect("study.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
c.execute('CREATE TABLE IF NOT EXISTS study_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, study_date TEXT, duration REAL, subject TEXT, topic TEXT, status TEXT DEFAULT "Completed", username TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS exams (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_name TEXT, subject TEXT, username TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS exam_questions (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_id INTEGER, question TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT, correct INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS exam_results (id INTEGER PRIMARY KEY AUTOINCREMENT, exam_id INTEGER, score INTEGER, total INTEGER, date TEXT, username TEXT)')
conn.commit()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"]=False; st.session_state["user"]=""; st.session_state["goal"]=500
    st.session_state["timer_start"]=None; st.session_state["timer_subject"]=""; st.session_state["timer_topic"]=""
    st.session_state["exam_qs"]=[]

if not st.session_state["logged_in"]:
    st.markdown('<div style="text-align:center; margin-top:20px; margin-bottom:30px;"><div style="font-size:60px;">🔥</div><h1 style="color:white; margin:0;">Smart Study Heat Map</h1><p style="color:#3b82f6; font-weight:600; margin-top:6px;">Track • Analyze • Excel • Year 2026</p></div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([0.15, 0.7, 0.15])
    with mid:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown('<div class="login-title">Login</div>', unsafe_allow_html=True)
            u = st.text_input("Username", key="login_u", placeholder="Karthik")
            p = st.text_input("Password", type="password", key="login_p", placeholder="Enter password")
            if st.button("Log In", use_container_width=True, type="primary"):
                if not u: st.warning("Please enter username")
                else:
                    if u.strip().lower() == "karthik":
                        c.execute("INSERT OR IGNORE INTO users (username,password) VALUES (?,?)", ("Karthik","1234567890")); conn.commit()
                        st.session_state["logged_in"]=True; st.session_state["user"]="Karthik"; st.rerun()
                    else:
                        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p)); row=c.fetchone()
                        if row: st.session_state["logged_in"]=True; st.session_state["user"]=u; st.rerun()
                        else: st.error("Account not found! Please Register on the right side")
        with col2:
            st.markdown('<div class="login-title">Register</div>', unsafe_allow_html=True)
            new_u = st.text_input("Username", key="reg_u", placeholder="New Username")
            new_p = st.text_input("Password", type="password", key="reg_p", placeholder="New Password")
            conf_p = st.text_input("Confirm Password", type="password", key="reg_c", placeholder="Confirm Password")
            if st.button("Register", use_container_width=True):
                if not new_u or not new_p: st.warning("Please fill all fields")
                elif new_p!= conf_p: st.error("Passwords do not match")
                else:
                    try:
                        c.execute("INSERT INTO users (username,password) VALUES (?,?)", (new_u,new_p)); conn.commit()
                        st.success(f"{new_u} created successfully! Please login on the left")
                    except: st.error("Username already exists! Please login")
    st.stop()

st.sidebar.markdown(f'<div style="font-size:22px; font-weight:800; color:#3b82f6;">🔥 Study Heat Map</div><div style="color:#0ea5e9;">Welcome {st.session_state["user"]}</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
goal = st.sidebar.number_input("Annual Goal", min_value=10, max_value=10000, value=int(st.session_state["goal"]), step=10)
st.session_state["goal"]=goal
menu=st.sidebar.radio("Go to", ["🏠 Home","➕ Add Study","📋 Records","🔥 Heatmap","📊 Analysis","📝 Exam Mode","🏆 Grand Test"])
if st.sidebar.button("Logout"): st.session_state["logged_in"]=False; st.rerun()

df=pd.read_sql("SELECT * FROM study_logs WHERE username=?", conn, params=(st.session_state["user"],))
if not df.empty: df["study_date"]=pd.to_datetime(df["study_date"], errors='coerce')

if menu=="🏠 Home":
    tot=round(df["duration"].sum(),2) if not df.empty else 0
    pct_float=round(tot/goal*100,1) if goal>0 else 0
    now = datetime.now()
    if not df.empty:
        dates_sorted = sorted(set(df["study_date"].dt.date), reverse=True)
        streak=1; prev=dates_sorted[0]
        for d in dates_sorted[1:]:
            diff=(prev-d).days
            if diff==1 or (diff==2 and prev.weekday()==0): streak+=1; prev=d
            else: break
    else: streak=0
    st.markdown(f"""<div style="background: linear-gradient(135deg, #141b2d 0%, #1e293b 100%); border: 1px solid #2a3a5a; border-radius:20px; padding:22px 24px; display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;"><div style="display:flex; align-items:center; gap:16px;"><div style="background: linear-gradient(135deg, #3b82f6, #06b6d4); width:56px; height:56px; border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:28px;">🔥</div><div><div style="color:white; font-size:26px; font-weight:900;">Smart Study Heat Map</div><div style="color:#94a3b8; font-size:13px;"><span style="color:#3b82f6; font-weight:700;">{goal}h Goal</span> • <span style="color:#2dd4bf;">{pct_float}% completed</span> • Year 2026</div></div></div><div style="background:#0f172a; border:1px solid #334155; border-radius:24px; padding:8px 16px; color:#e2e8f0; font-size:13px; font-weight:600;">📅 {now.strftime('%b %d, %Y')}</div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:14px; margin-bottom:18px;"><div style="background:#141b2d; border-left:4px solid #3b82f6; border-radius:16px; padding:20px; display:flex; gap:16px; align-items:center;"><div style="background: rgba(59,130,246,0.15); width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:26px;">🎯</div><div><div style="color:#64748b; font-size:11px; font-weight:700;">Annual Goal</div><div style="color:white; font-size:28px; font-weight:900;">{goal}h</div><div style="color:#3b82f6; font-size:12px;">{pct_float}% done</div></div></div><div style="background:#141b2d; border-left:4px solid #2dd4bf; border-radius:16px; padding:20px; display:flex; gap:16px; align-items:center;"><div style="background: rgba(45,212,191,0.15); width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:26px;">⏰</div><div><div style="color:#64748b; font-size:11px; font-weight:700;">Total Hours</div><div style="color:white; font-size:28px; font-weight:900;">{tot}h</div><div style="color:#2dd4bf; font-size:12px;">{pct_float}% of goal</div></div></div><div style="background:#141b2d; border-left:4px solid #facc15; border-radius:16px; padding:20px; display:flex; gap:16px; align-items:center;"><div style="background: rgba(250,204,21,0.15); width:52px; height:52px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:26px;">🔥</div><div><div style="color:#64748b; font-size:11px; font-weight:700;">Current Streak</div><div style="color:white; font-size:28px; font-weight:900;">{streak} days</div><div style="color:#facc15; font-size:12px;">Keep going!</div></div></div></div>""", unsafe_allow_html=True)
    daily_map = df.groupby(df["study_date"].dt.date)["duration"].sum().to_dict() if not df.empty else {}
    weeks=[]; cur_week=[None]*6; cur_date=date(2026,1,1)
    while cur_date<=date(2026,12,31):
        wd=cur_date.weekday()
        if wd==6: weeks.append(cur_week); cur_week=[None]*6
        else:
            if wd==0 and cur_week[0] is not None: weeks.append(cur_week); cur_week=[None]*6
            cur_week[wd]=cur_date
        cur_date+=timedelta(days=1)
    if any(cur_week): weeks.append(cur_week)
    days = ["Mon","Tue","Wed","Thu","Fri","Sat"]
    html = f'<div style="background:#0f172a; border:1px solid #1f2c42; padding:18px; border-radius:16px; margin-bottom:14px;"><div style="display:flex; justify-content:space-between; margin-bottom:12px;"><div style="color:white; font-weight:800;">🔥 2026 Study Activity</div><div style="display:flex; gap:4px; align-items:center;"><span style="color:#64748b; font-size:11px;">Less</span><div style="width:12px; height:12px; background:#1e293b; border-radius:3px;"></div><div style="width:12px; height:12px; background:#39d353; border-radius:3px;"></div><span style="color:#64748b; font-size:11px;">More</span></div></div><div style="display:flex; gap:6px;"><div style="display:flex; flex-direction:column; gap:5px;">'
    for d in days: html += f'<div style="width:28px; height:13px; color:#64748b; font-size:10px;">{d}</div>'
    html += '</div><div style="display:flex; gap:4px; overflow-x:auto;">'
    for week in weeks:
        html+='<div style="display:flex; flex-direction:column; gap:5px;">'
        for wd in range(6):
            d=week[wd]
            if d is None: html+='<div style="width:13px; height:13px;"></div>'
            else:
                dur=daily_map.get(d,0)
                if d==now.date(): color="#facc15"
                elif dur==0: color="#1e293b"
                elif dur<1: color="#0e4429"
                elif dur<3: color="#006d32"
                elif dur<5: color="#26a641"
                else: color="#39d353"
                html+=f'<div title="{d} - {dur}h" style="width:13px; height:13px; background:{color}; border-radius:4px;"></div>'
        html+='</div>'
    html+='</div></div></div>'
    st.markdown(html, unsafe_allow_html=True)

elif menu=="➕ Add Study":
    st.markdown('<div class="card"><h2 style="color:white; margin:0;">🔥 Smart Study Heat Map</h2><p style="color:#3b82f6; margin:5px 0 0 0; font-size:13px; font-weight:600;">Track • Analyze • Excel • Timer Mode</p></div>', unsafe_allow_html=True)
    sub = st.text_input("Subject Name", placeholder="Ex: Python"); top = st.text_input("Topic Name", placeholder="Ex: Loops", disabled=st.session_state["timer_start"] is not None)
    if st.session_state["timer_start"] is None:
        if st.button("▶️ Start Session", use_container_width=True, type="primary"):
            if sub: st.session_state["timer_start"]=datetime.now(); st.session_state["timer_subject"]=sub; st.session_state["timer_topic"]=top; st.rerun()
    else:
        st_autorefresh(interval=1000, key="timer"); elapsed=datetime.now()-st.session_state["timer_start"]; s=int(elapsed.total_seconds()); h,r=divmod(s,3600); m,sec=divmod(r,60)
        st.markdown(f'<div class="card" style="text-align:center;"><div style="font-size:48px; color:#2dd4bf; font-weight:800;">{h:02d}:{m:02d}:{sec:02d}</div><div style="color:#94a3b8;">{st.session_state["timer_subject"]} - {st.session_state["timer_topic"]}</div></div>', unsafe_allow_html=True)
        if st.button("⏹️ End & Save", use_container_width=True, type="primary"):
            dur=round((datetime.now()-st.session_state["timer_start"]).total_seconds()/3600,2)
            if dur<0.01: dur=0.01
            c.execute("INSERT INTO study_logs (study_date,duration,subject,topic,status,username) VALUES (?,?,?,?,?,?)",(str(st.session_state["timer_start"].date()),dur,st.session_state["timer_subject"],st.session_state["timer_topic"],"Completed",st.session_state["user"]))
            conn.commit(); st.session_state["timer_start"]=None; st.balloons(); st.rerun()

elif menu=="📋 Records":
    st.markdown('<div class="card"><h2 style="color:white;">📋 Records</h2></div>', unsafe_allow_html=True)
    df_rec = pd.read_sql(f"SELECT id, study_date, duration, subject, topic, status FROM study_logs WHERE username='{st.session_state['user']}' ORDER BY id DESC", conn)
    st.dataframe(df_rec, use_container_width=True, hide_index=True)

elif menu=="🔥 Heatmap":
    if df.empty:
        st.info("No data yet - Add study first")
    else:
        st.markdown('<div class="card"><h2 style="color:white;">🔥 Study Heatmap - 2026</h2><p style="color:#94a3b8; font-size:12px; margin:4px 0 0 0;">Yearly study consistency overview</p></div>', unsafe_allow_html=True)
        daily_map = df.groupby(df["study_date"].dt.date)["duration"].sum().to_dict()
        now=datetime.now(); today=now.date()
        weeks=[]; cur_week=[None]*6; cur_date=date(2026,1,1)
        while cur_date<=date(2026,12,31):
            wd=cur_date.weekday()
            if wd==6: weeks.append(cur_week); cur_week=[None]*6
            else:
                if wd==0 and cur_week[0] is not None: weeks.append(cur_week); cur_week=[None]*6
                cur_week[wd]=cur_date
            cur_date+=timedelta(days=1)
        if any(cur_week): weeks.append(cur_week)
        days=["Mon","Tue","Wed","Thu","Fri","Sat"]
        html=f'<div style="background:#0f172a; border:1px solid #1f2c42; padding:16px; border-radius:16px; margin-top:12px;"><div style="display:flex; justify-content:space-between; margin-bottom:12px;"><div style="color:white; font-weight:700; font-size:14px;">2026 Activity Overview</div><div style="display:flex; gap:6px; align-items:center;"><span style="color:#64748b; font-size:11px;">Less</span><div style="width:12px; height:12px; background:#1e293b; border-radius:3px;"></div><div style="width:12px; height:12px; background:#006d32; border-radius:3px;"></div><div style="width:12px; height:12px; background:#39d353; border-radius:3px;"></div><span style="color:#64748b; font-size:11px;">More</span></div></div><div style="display:flex; gap:6px;"><div style="display:flex; flex-direction:column; gap:5px;">'
        for d in days: html+=f'<div style="width:30px; height:14px; color:#64748b; font-size:11px;">{d}</div>'
        html+='</div><div style="display:flex; gap:4px; overflow-x:auto;">'
        for week in weeks:
            html+='<div style="display:flex; flex-direction:column; gap:5px;">'
            for wd in range(6):
                d=week[wd]
                if d is None: html+='<div style="width:14px; height:14px;"></div>'
                else:
                    dur=daily_map.get(d,0)
                    if d==today: color="#facc15"
                    elif dur==0: color="#1e293b"
                    elif dur<1: color="#0e4429"
                    elif dur<3: color="#006d32"
                    elif dur<5: color="#26a641"
                    else: color="#39d353"
                    html+=f'<div title="{d} - {dur}h" style="width:14px; height:14px; background:{color}; border-radius:3px;"></div>'
            html+='</div>'
        html+='</div></div></div>'
        st.markdown(html, unsafe_allow_html=True)

        # --- FIXED GAP HERE ---
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        st.markdown('<div style="background:#141b2d; border:1px solid #1f2c42; border-radius:18px; padding:12px 18px 2px 18px;">', unsafe_allow_html=True)
        heat = df.groupby(df["study_date"].dt.date)["duration"].sum().sort_index().tail(20)
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(9,2.8))
        fig.patch.set_facecolor("#141b2d"); ax.set_facecolor("#141b2d")
        bars = ax.bar([d.strftime("%b %d") for d in pd.to_datetime(heat.index)], heat.values, color="#3b82f6", width=0.6, edgecolor="#1f2c42")
        max_v = max(heat.values) if len(heat)>0 else 1
        ax.set_ylim(0, max_v*1.4 if max_v>=1 else max_v*2+0.5)
        for bar in bars:
            h=bar.get_height()
            if h>0.001:
                gap = max_v*0.05 if max_v>=1 else 0.08
                ax.text(bar.get_x()+bar.get_width()/2., h+gap, f'{h:.1f}h', ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')
        ax.set_ylabel("Hours", color="white")
        ax.tick_params(colors="white", rotation=25, labelsize=9)
        ax.grid(axis='y', alpha=0.15)
        for spine in ax.spines.values(): spine.set_color("#1f2c42")
        fig.tight_layout(pad=0.5)
        st.pyplot(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu=="📊 Analysis":
    now = datetime.now()
    cur_week = (now.day-1)//7+1
    st.markdown(f'<div class="card"><h2 style="color:white;">📊 Analysis - {now.strftime("%B")} 2026</h2></div>', unsafe_allow_html=True)
    if df.empty:
        st.info("No study data yet - Go to Add Study and start a session")
    else:
        df["week_of_month"] = (df["study_date"].dt.day-1)//7+1
        df["month"] = df["study_date"].dt.month
        df["month_short"] = df["study_date"].dt.strftime("%b")
        tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])
        with tab1:
            today = now.date()
            monday = today - timedelta(days=today.weekday())
            week_dates = [monday + timedelta(days=i) for i in range(6)]
            daily_dict = df.groupby(df["study_date"].dt.date)["duration"].sum().to_dict()
            daily_vals = [float(daily_dict.get(d, 0)) for d in week_dates]
            daily_labels = [d.strftime("%a %d") for d in week_dates]
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(7,3.2))
            fig.patch.set_facecolor("#141b2d"); ax.set_facecolor("#141b2d")
            colors = ["#facc15" if d==today else "#2dd4bf" for d in week_dates]
            bars = ax.bar(daily_labels, daily_vals, color=colors, width=0.5, edgecolor="#1f2c42")
            max_v = max(daily_vals) if max(daily_vals)>0 else 1
            ax.set_ylim(0, max_v*1.8 if max_v>=1 else 1)
            for bar in bars:
                h = bar.get_height()
                if h>0.001: ax.text(bar.get_x()+bar.get_width()/2., h+0.05, f'{h:.1f}h', ha='center', color='white', fontweight='bold', fontsize=9)
            ax.set_ylabel("Hours", color="white"); ax.tick_params(colors="white"); ax.grid(axis='y', alpha=0.15)
            st.pyplot(fig)
        with tab2:
            st.markdown(f'<div style="background:#facc15; color:#000; padding:5px 12px; border-radius:12px; font-weight:800; display:inline-block; margin-bottom:10px;">LIVE: {now.strftime("%B")} Week {cur_week}</div>', unsafe_allow_html=True)
            weekly_dict = df[df["month"]==now.month].groupby("week_of_month")["duration"].sum().to_dict()
            labels=[]; vals=[]; col=[]
            for w in [1,2,3,4,5]:
                labels.append(f"Week {w}")
                vals.append(float(weekly_dict.get(w,0)))
                col.append("#facc15" if w==cur_week else "#3b82f6")
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(7,3))
            fig.patch.set_facecolor("#141b2d"); ax.set_facecolor("#141b2d")
            bars = ax.bar(labels, vals, color=col, width=0.5, edgecolor="#1f2c42")
            max_v = max(vals) if max(vals)>0 else 1
            ax.set_ylim(0, max_v*1.6 if max_v>=1 else 1.5)
            for bar in bars:
                h = bar.get_height()
                if h>0: ax.text(bar.get_x()+bar.get_width()/2., h+0.05, f'{h:.1f}h', ha='center', color='white', fontweight='bold')
            ax.set_ylabel("Hours", color="white"); ax.tick_params(colors="white"); ax.grid(axis='y', alpha=0.15)
            st.pyplot(fig)
        with tab3:
            st.markdown('<div style="background:#8b5cf6; color:white; padding:5px 12px; border-radius:12px; font-weight:700; display:inline-block; margin-bottom:10px;">Full Year 2026 - Monthly Progress</div>', unsafe_allow_html=True)
            monthly = df.groupby("month_short")["duration"].sum()
            order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            full_vals = []
            for m in order:
                full_vals.append(float(monthly.get(m, 0)))
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(9,3.5))
            fig.patch.set_facecolor("#141b2d"); ax.set_facecolor("#141b2d")
            cur_m = now.strftime("%b")
            bar_colors = ["#facc15" if x==cur_m else "#8b5cf6" for x in order]
            bars = ax.bar(order, full_vals, color=bar_colors, width=0.6, edgecolor="#1f2c42")
            max_m = max(full_vals) if max(full_vals)>0 else 1
            ax.set_ylim(0, max_m*1.5 if max_m>=1 else 2)
            for bar in bars:
                h = bar.get_height()
                if h>0.05: ax.text(bar.get_x()+bar.get_width()/2., h+0.1, f'{h:.1f}h', ha='center', color='white', fontsize=9, fontweight='bold')
            ax.set_ylabel("Hours", color="white"); ax.tick_params(colors="white"); ax.grid(axis='y', alpha=0.15)
            st.pyplot(fig)

elif menu=="📝 Exam Mode":
    st.markdown('<div class="card"><h2 style="color:white; margin:0;">📝 Exam Mode</h2><p style="color:#3b82f6; font-size:12px;">Create • Take • Results</p></div>', unsafe_allow_html=True)
    tab_create, tab_take, tab_results = st.tabs(["➕ Create Exam", "▶️ Take Exam", "📊 Results"])
    with tab_create:
        exam_name = st.text_input("Exam Name"); exam_sub = st.text_input("Subject")
        q_text = st.text_area("Question"); c1,c2=st.columns(2)
        with c1: o1=st.text_input("Option 1"); o2=st.text_input("Option 2")
        with c2: o3=st.text_input("Option 3"); o4=st.text_input("Option 4")
        correct = st.selectbox("Correct Option", [1,2,3,4])
        if st.button("Add Question"):
            if q_text and o1:
                st.session_state["exam_qs"].append((q_text,o1,o2,o3,o4,correct)); st.success(f"Added {len(st.session_state['exam_qs'])} Qs")
        if st.session_state["exam_qs"]:
            for i,q in enumerate(st.session_state["exam_qs"]): st.write(f"{i+1}. {q[0]}")
            if st.button("💾 Save Full Exam", type="primary"):
                if exam_name and exam_sub:
                    c.execute("INSERT INTO exams (exam_name, subject, username) VALUES (?,?,?)",(exam_name, exam_sub, st.session_state["user"])); eid=c.lastrowid
                    for q in st.session_state["exam_qs"]: c.execute("INSERT INTO exam_questions (exam_id, question, opt1, opt2, opt3, opt4, correct) VALUES (?,?,?,?,?,?,?)",(eid,q[0],q[1],q[2],q[3],q[4],q[5]))
                    conn.commit(); st.session_state["exam_qs"]=[]; st.balloons(); st.success("Exam Saved!")
    with tab_take:
        exams = pd.read_sql(f"SELECT * FROM exams WHERE username='{st.session_state['user']}'", conn)
        if exams.empty: st.info("No exams - Create first")
        else:
            sel = st.selectbox("Select Exam", exams["exam_name"].tolist())
            if sel:
                eid = exams[exams["exam_name"]==sel].iloc[0]["id"]
                qs = pd.read_sql(f"SELECT * FROM exam_questions WHERE exam_id={eid}", conn)
                for idx,row in qs.iterrows():
                    st.markdown(f"**{idx+1}. {row['question']}**")
                    st.radio(f"Answer {idx}", [row['opt1'], row['opt2'], row['opt3'], row['opt4']], key=f"q{row['id']}", index=None)
                if st.button("Submit Exam", type="primary"):
                    score=0
                    for _,row in qs.iterrows():
                        chosen = st.session_state.get(f"q{row['id']}")
                        opts = [row['opt1'], row['opt2'], row['opt3'], row['opt4']]
                        if chosen and opts.index(chosen)+1 == row['correct']: score+=1
                    c.execute("INSERT INTO exam_results (exam_id, score, total, date, username) VALUES (?,?,?,?,?)",(eid, score, len(qs), str(date.today()), st.session_state["user"])); conn.commit()
                    st.success(f"Score: {score}/{len(qs)}"); st.balloons()
    with tab_results:
        res = pd.read_sql(f"SELECT exam_results.*, exams.exam_name FROM exam_results JOIN exams ON exam_results.exam_id=exams.id WHERE exam_results.username='{st.session_state['user']}' ORDER BY exam_results.id DESC", conn)
        if res.empty: st.info("No results yet")
        else: st.dataframe(res[["exam_name","score","total","date"]], use_container_width=True, hide_index=True)

elif menu=="🏆 Grand Test":
    now = datetime.now()
    total = round(df["duration"].sum(),2) if not df.empty else 0
    pct = round(total/goal*100,1) if goal>0 else 0
    st.markdown(f'<div class="card"><h2 style="color:white; margin:0;">🏆 Grand Test</h2><div style="color:#94a3b8; font-size:13px;">Total {total}h / {goal}h • {pct}% Completed • {now.strftime("%b %Y")}</div></div>', unsafe_allow_html=True)
    if df.empty:
        st.info("No study data yet - Add study first")
    else:
        temp = df.copy()
        temp["subject_clean"] = temp["subject"].astype(str).str.strip().str.lower()
        temp["subject_display"] = temp["subject"].astype(str).str.strip().str.title()
        display_map = temp.drop_duplicates("subject_clean").set_index("subject_clean")["subject_display"].to_dict()
        grouped = temp.groupby("subject_clean")["duration"].sum()
        grouped = grouped[grouped > 0.001].sort_values(ascending=False)
        if grouped.empty:
            st.info("No valid hours found")
        else:
            top_clean = grouped.index[0]
            top_name = display_map.get(top_clean, top_clean.title())
            top_hours = grouped.iloc[0]
            st.markdown(f"""<div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin:16px 0;">
            <div class="card"><div style="color:#64748b; font-size:11px; font-weight:700;">TOTAL HOURS</div><div style="color:white; font-size:26px; font-weight:900;">{total}h</div><div style="color:#3b82f6; font-size:12px;">Goal {goal}h</div></div>
            <div class="card"><div style="color:#64748b; font-size:11px; font-weight:700;">SUBJECTS</div><div style="color:white; font-size:26px; font-weight:900;">{len(grouped)}</div><div style="color:#2dd4bf; font-size:12px;">Active</div></div>
            <div class="card"><div style="color:#64748b; font-size:11px; font-weight:700;">TOP SUBJECT</div><div style="color:#facc15; font-size:20px; font-weight:900;">{top_name}</div><div style="color:white; font-size:12px;">{top_hours:.1f}h</div></div>
            </div>""", unsafe_allow_html=True)
            labels = [display_map.get(c, c.title()) for c in grouped.index]
            values = grouped.values
            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(8, 4))
            fig.patch.set_facecolor("#141b2d"); ax.set_facecolor("#141b2d")
            bars = ax.bar(labels, values, color="#f59e0b", width=0.55, edgecolor="#1f2c42", linewidth=1, zorder=3)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., h + (max(values)*0.02 + 0.05), f'{h:.1f}h', ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
            ax.set_ylabel("Hours", color="white", fontsize=11)
            ax.set_ylim(0, max(values)*1.25 if max(values)>0 else 1)
            ax.tick_params(axis='x', colors="white", labelsize=10, rotation=15)
            ax.tick_params(axis='y', colors="white")
            ax.grid(axis='y', alpha=0.15, zorder=0)
            for spine in ax.spines.values(): spine.set_color("#1f2c42")
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)
