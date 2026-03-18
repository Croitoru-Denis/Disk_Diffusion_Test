import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. Page Configuration ---
# Changed layout to "wide" to better accommodate the right-side menu
st.set_page_config(page_title="Disk Diffusion Analyzer B", page_icon="🔬", layout="wide")

# --- 2. State Management ---
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'login'
if 'username' not in st.session_state:
    st.session_state.username = "Researcher"
if 'history' not in st.session_state:
    st.session_state.history = [] 
if 'current_result' not in st.session_state:
    st.session_state.current_result = {}

# --- Navigation & Action Functions ---
def set_view(view_name):
    st.session_state.current_view = view_name

def login():
    if st.session_state.user_input.strip():
        st.session_state.username = st.session_state.user_input.strip()
    else:
        st.session_state.username = "Researcher"
    set_view('setup')

def logout():
    st.session_state.username = "Researcher"
    set_view('login')

def analyze_and_auto_save():
    b = st.session_state.bac_input
    a = st.session_state.anti_input
    
    if b == "E. coli" and a == "Ciprofloxacin":
        interpretation, zone, color = "Resistant", "10 mm", "🔴"
    elif b == "S. aureus" and a == "Penicillin":
        interpretation, zone, color = "Semi-Resistant", "16 mm", "🟡"
    elif b == "P. aeruginosa":
        interpretation, zone, color = "Resistant", "8 mm", "🔴"
    else:
        interpretation, zone, color = "Non-Resistant", "24 mm", "🟢"
        
    st.session_state.current_result = {
        'bacterium': b,
        'antibiotic': a,
        'interpretation': interpretation,
        'zone': zone,
        'color': color
    }
    
    record = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'bacterium': b,
        'antibiotic': a,
        'result': interpretation
    }
    st.session_state.history.append(record)
    set_view('results')


# ==========================================
# VIEW 1: LOGIN (Unchanged layout)
# ==========================================
if st.session_state.current_view == 'login':
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔬</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Disk Diffusion Analyzer</h3>", unsafe_allow_html=True)
        st.write("")
        with st.container(border=True):
            st.text_input("Username", placeholder="e.g. Dr. John Smith", key="user_input")
            st.text_input("Password", placeholder="••••••••", type="password")
            st.button("Sign In", type="primary", use_container_width=True, on_click=login)

# ==========================================
# MAIN APP LAYOUT (For Views 2, 3, 4, 5)
# ==========================================
else:
    # Top Bar: Username & Logout in the top right
    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
        st.markdown(f"<div style='text-align: right;'>👤 <b>{st.session_state.username}</b></div>", unsafe_allow_html=True)
        st.button("Log Out", on_click=logout, use_container_width=True)
    
    st.divider()

    # Main structural columns: App content on the left (ratio 4), Menu on the right (ratio 1)
    main_content_col, menu_col = st.columns([4, 1], gap="large")

    # --- RIGHT SIDE MENU ---
    with menu_col:
        st.markdown("### 🔬 Menu")
        st.button("⌂ Analyze", on_click=set_view, args=('setup',), use_container_width=True)
        st.button("🕒 History", on_click=set_view, args=('history',), use_container_width=True)
        st.button("📊 Performance", on_click=set_view, args=('performance',), use_container_width=True)

    # --- LEFT SIDE CONTENT (Views) ---
    with main_content_col:
        
        # VIEW 2: SETUP
        if st.session_state.current_view == 'setup':
            st.markdown("### New Analysis")
            
            with st.container(border=True):
                st.markdown("#### 📷 Plate Image")
                use_camera = st.toggle("Open Camera to take a photo")
                if use_camera:
                    st.camera_input("Take a photo of the plate", label_visibility="collapsed")
                
                st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>— OR UPLOAD FILE —</p>", unsafe_allow_html=True)
                st.file_uploader("Upload", type=['png', 'jpg'], label_visibility="collapsed")

            with st.container(border=True):
                st.markdown("#### 🔬 Parameters")
                col_b, col_a = st.columns(2)
                with col_b:
                    st.selectbox("Bacterium", ["E. coli", "S. aureus", "P. aeruginosa"], key="bac_input")
                with col_a:
                    st.selectbox("Antibiotic", ["Penicillin", "Amoxicillin", "Ciprofloxacin"], key="anti_input")

            st.write("") 
            st.button("Analyze Test", type="primary", use_container_width=True, on_click=analyze_and_auto_save)

        # VIEW 3: RESULTS
        elif st.session_state.current_view == 'results':
            with st.spinner("Analyzing plate..."):
                time.sleep(0.5) 
                
            st.success("Analysis Complete & Saved to History!")
            res = st.session_state.current_result
            
            with st.container(border=True):
                # Modification 1: Display Interpretation FIRST and prominently
                st.markdown(f"<h2 style='text-align: center;'>{res['color']} {res['interpretation']}</h2>", unsafe_allow_html=True)
                st.divider()
                
                # Then display the rest of the info
                st.markdown(f"**Tested:** {res['bacterium']} + {res['antibiotic']}")
                st.metric(label="Measured Zone", value=res['zone'])

            st.write("")
            
            # Modification 2 & 3: Only "Start New Analysis" button, arrows removed
            st.button("Start New Analysis", use_container_width=True, on_click=set_view, args=('setup',))

        # VIEW 4: HISTORY
        elif st.session_state.current_view == 'history':
            st.markdown("### 🕒 Saved Outcomes")
            
            if not st.session_state.history:
                st.info("No results saved yet. Go analyze a test!")
            else:
                for record in reversed(st.session_state.history):
                    with st.container(border=True):
                        st.caption(f"🗓️ {record['date']}")
                        st.markdown(f"**{record['bacterium']}** vs **{record['antibiotic']}**")
                        
                        color = "green" if record['result'] == "Non-Resistant" else "orange" if record['result'] == "Semi-Resistant" else "red"
                        st.markdown(f"Result: <span style='color:{color}; font-weight:bold;'>{record['result']}</span>", unsafe_allow_html=True)
                        
            st.write("")
            st.button("Back to Analysis", use_container_width=True, on_click=set_view, args=('setup',))

        # VIEW 5: PERFORMANCE DASHBOARD (Upgraded)
        elif st.session_state.current_view == 'performance':
            st.markdown("### 📊 Performance Dashboard")
            
            if not st.session_state.history:
                st.warning("Dashboard is using sample data. Run actual tests to see live metrics!")
                df = pd.DataFrame([
                    {"date": "2023-10-01", "result": "Non-Resistant", "bacterium": "E. coli", "antibiotic": "Amoxicillin"}, 
                    {"date": "2023-10-02", "result": "Non-Resistant", "bacterium": "E. coli", "antibiotic": "Penicillin"},
                    {"date": "2023-10-03", "result": "Semi-Resistant", "bacterium": "S. aureus", "antibiotic": "Penicillin"}, 
                    {"date": "2023-10-04", "result": "Resistant", "bacterium": "S. aureus", "antibiotic": "Amoxicillin"},
                    {"date": "2023-10-05", "result": "Resistant", "bacterium": "P. aeruginosa", "antibiotic": "Ciprofloxacin"}, 
                    {"date": "2023-10-06", "result": "Non-Resistant", "bacterium": "P. aeruginosa", "antibiotic": "Penicillin"}
                ])
            else:
                df = pd.DataFrame(st.session_state.history)

            total_tests = len(df)
            resistant_count = len(df[df['result'] == 'Resistant'])
            semi_count = len(df[df['result'] == 'Semi-Resistant'])
            res_rate = int((resistant_count / total_tests) * 100) if total_tests > 0 else 0
            
            # Upgraded metrics
            col1, col2, col3 = st.columns(3)
            with st.container(border=True):
                col1.metric("Total Tests", total_tests)
                col2.metric("High Resistance Rate", f"{res_rate}%")
                col3.metric("Actionable Alerts", resistant_count + semi_count, delta="Requires Attention", delta_color="inverse")

            # Upgraded Visuals: Added a stacked bar chart for Bacteria vs Resistance profile
            st.markdown("#### Resistance Profiles by Bacteria")
            profile_data = df.groupby(['bacterium', 'result']).size().reset_index(name='count')
            color_map = {'Non-Resistant': '#10B981', 'Semi-Resistant': '#F59E0B', 'Resistant': '#EF4444'}
            
            fig_bar = px.bar(profile_data, x="bacterium", y="count", color="result", 
                             color_discrete_map=color_map, barmode="stack")
            fig_bar.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=300, xaxis_title="Bacterium", yaxis_title="Number of Tests")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Keep the pie chart but make it secondary
            with st.container(border=True):
                st.markdown("**Overall Interpretation Distribution**")
                pie_data = df['result'].value_counts().reset_index()
                pie_data.columns = ['Result', 'Count']
                fig_pie = px.pie(pie_data, values='Count', names='Result', hole=0.4, color='Result', color_discrete_map=color_map)
                fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
                st.plotly_chart(fig_pie, use_container_width=True)