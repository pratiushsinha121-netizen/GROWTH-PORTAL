import streamlit as st
import datetime
import json
import os

DB_FILE = "challengers_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def calculate_time_gap(wut, fwst):
    if fwst == "00": return 999
    try:
        t1 = datetime.datetime.strptime(wut, "%H:%M")
        t2 = datetime.datetime.strptime(fwst, "%H:%M")
        if t2 < t1: t2 += datetime.timedelta(days=1)
        return (t2 - t1).total_seconds() / 3600.0
    except ValueError:
        return 999

# Web App Interface Configuration
st.set_page_config(page_title="Growth Challengers", layout="wide")
st.title("🚀 Growth Challengers Portal")

# Load existing data
data = load_data()

# Create navigation tabs
tab1, tab2, tab3 = st.tabs(["🎯 Post Targets", "📝 Submit Report", "🏆 Leaderboard"])

with tab1:
    st.header("Post Daily Targets")
    with st.form("targets_form"):
        uid = st.text_input("Unique ID (e.g., A0001)").strip().upper()
        targets = st.text_area("Enter your targets (one per line)")
        posted_time = st.text_input("Time Posted (HH:MM, 24hr format)", value="05:00")
        submit_targets = st.form_submit_button("Save Targets")
        
        if submit_targets and uid:
            if uid not in data:
                data[uid] = {"streak": 0, "total_points": 0, "daily_points": 0, "targets": []}
            data[uid]["posted_time"] = posted_time
            data[uid]["targets"] = targets.split('\n')
            save_data(data)
            st.success(f"Targets saved for {uid}!")

with tab2:
    st.header("Submit Work Report & Calculate Points")
    with st.form("report_form"):
        uid_report = st.text_input("Confirm Unique ID").strip().upper()
        
        col1, col2 = st.columns(2)
        with col1:
            wut = st.text_input("Wake Up Time (WUT) [HH:MM]", value="04:30")
            fwst = st.text_input("First Work Session Time (FWST) [HH:MM or '00']", value="05:00")
            st_time = st.number_input("Non-Academic Screen Time (Hours)", min_value=0.0, value=1.0, step=0.5)
            comp = st.slider("Task Completion Percentage", 0, 100, 100)
            extra_tasks = st.number_input("Additional Tasks Done", min_value=0, value=0)
        
        with col2:
            hop_target = st.number_input("HOP Target Hours Completed", min_value=0.0, value=0.0, step=0.5)
            hop_extra = st.number_input("Extra Hours in HOP", min_value=0.0, value=0.0, step=0.5)
            fhop_hours = st.number_input("FHOP Hours Clocked", min_value=0.0, value=0.0, step=0.5)
            failed_hops = st.number_input("Failed HOPs", min_value=0, value=0)
            rules_broken = st.number_input("Self Rules Violated", min_value=0, value=0)
            unnecessary_msgs = st.number_input("Unnecessary Messages (>5)", min_value=0, value=0)
            ofa_completed = st.checkbox("Completed an OFA Challenge?")
            ofa_size = st.number_input("OFA Challenge Points (10-50)", min_value=10, max_value=50, value=10) if ofa_completed else 0

        submit_report = st.form_submit_button("Calculate & Submit")
        
        if submit_report and uid_report in data:
            points = 20 # Work report writing bonus
            gap = calculate_time_gap(wut, fwst)
            
            if gap > 2: points -= 20
            if st_time <= 1.5: points += 50
            else: points -= int((st_time - 1.5) * 10)
            
            if comp == 100: points += 100
            else: points += (100 - int((100 - comp) / 10) * 10)
            
            points += (extra_tasks * 10)
            
            posted = data[uid_report].get("posted_time", "00:00")
            try:
                p_time = datetime.datetime.strptime(posted, "%H:%M").time()
                if datetime.time(4, 30) <= p_time <= datetime.time(9, 30):
                    points += 20
            except ValueError: pass
            
            if hop_target == 0 and fhop_hours == 0: points -= 20
            points += int(hop_target * 10) + int(hop_extra * 10) + int(fhop_hours * 10) - (failed_hops * 10)
            points -= (rules_broken * 10) + (unnecessary_msgs * 10)
            if ofa_completed: points += ofa_size
            
            streak = data[uid_report].get("streak", 0)
            if comp > 50:
                streak += 1
                if streak in [3, 4]: points += 50
                elif streak in [5, 6]: points += 75
                elif streak in [7, 8]: points += 100
                elif streak >= 9: points += 125
            else: streak = 0
            
            data[uid_report]["streak"] = streak
            data[uid_report]["daily_points"] = points
            data[uid_report]["total_points"] = data[uid_report].get("total_points", 0) + points
            save_data(data)
            
            st.success(f"Report saved! You earned {points} points today. Current streak: {streak} days.")
        elif submit_report:
            st.error("ID not found. Please post targets in the first tab before submitting a report.")

with tab3:
    st.header("🏆 Daily Leaderboard")
    if data:
        sorted_users = sorted(data.items(), key=lambda x: x[1].get('daily_points', 0), reverse=True)
        for rank, (uid, info) in enumerate(sorted_users, start=1):
            points = info.get('daily_points', 0)
            streak = info.get('streak', 0)
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🔸"
            st.markdown(f"#{rank} {medal} [{uid}]: {points} POINTS *(Streak: {streak})*")
    else:
        st.info("No data yet. Start tracking to see the leaderboard!")
