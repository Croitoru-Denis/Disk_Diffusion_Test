import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(page_title="Disk Diffusion Analyzer", page_icon="🔬", layout="centered")

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
    # 1. Grab the inputs right as the button is clicked
    b = st.session_state.bac_input
    a = st.session_state.anti_input
    
    # 2. Run the logic
    if b == "E. coli" and a == "Ciprofloxacin":
        interpretation, zone, color = "Resistant", "10 mm", "🔴"
    elif b == "S. aureus" and a == "Penicillin":
        interpretation, zone, color = "Semi-Resistant", "16 mm", "🟡"
    elif b == "P. aeruginosa":
        interpretation, zone, color = "Resistant", "8 mm", "🔴"
    else:
        interpretation, zone, color = "Non-Resistant", "24 mm", "🟢"
        
    # 3. Save it for the Results screen to display
    st.session_state.current_result = {
        'bacterium': b,
        'antibiotic': a,
        'interpretation': interpretation,
        'zone': zone,
        'color': color
    }
    
    # 4. AUTO-SAVE to History instantly!
    record = {
        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'bacterium': b,
        'antibiotic': a,
        'result': interpretation
    }
    st.session_state.history.append(record)
    
    # 5. Switch to the results screen
    set_view('results')


# --- 3. Sidebar Navigation ---
if st.session_state.current_view != 'login':
    with st.sidebar:
        st.markdown("### 🔬 Menu")
        st.button("⌂ Analyze", on_click=set_view, args=('setup',), use_container_width=True)
        st.button("🕒 History", on_click=set_view, args=('history',), use_container_width=True)
        st.button("📊 Performance", on_click=set_view, args=('performance',), use_container_width=True)
        st.divider()
        st.markdown(f"👤 **{st.session_state.username}**")
        st.button("Log Out", on_click=logout, use_container_width=True)


# ==========================================
# VIEW 1: LOGIN
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
# VIEW 2: SETUP
# ==========================================
elif st.session_state.current_view == 'setup':
    st.markdown("<h3 style='text-align: center;'>New Analysis</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("#### 📷 Plate Image")
        use_camera = st.toggle("Open Camera to take a photo")
        if use_camera:
            st.camera_input("Take a photo of the plate", label_visibility="collapsed")
        
        st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>— OR UPLOAD FILE —</p>", unsafe_allow_html=True)
        st.file_uploader("Upload", type=['png', 'jpg'], label_visibility="collapsed")

    with st.container(border=True):
        st.markdown("#### 🔬 Parameters")
        st.selectbox("Bacterium", ["E. coli", "S. aureus", "P. aeruginosa"], key="bac_input")
        st.selectbox("Antibiotic", ["Penicillin", "Amoxicillin", "Ciprofloxacin"], key="anti_input")

    st.write("") 
    # Triggers our new all-in-one auto-save function
    st.button("Analyze Test", type="primary", use_container_width=True, on_click=analyze_and_auto_save)


# ==========================================
# VIEW 3: RESULTS (No more save button!)
# ==========================================
elif st.session_state.current_view == 'results':
    with st.spinner("Analyzing plate..."):
        time.sleep(0.5) 
        
    st.success("Analysis Complete & Saved to History!")
    
    # Read the pre-calculated results
    res = st.session_state.current_result
    
    with st.container(border=True):
        st.markdown("#### 📄 Results")
        st.markdown(f"**Tested:** {res['bacterium']} + {res['antibiotic']}")
        st.write("")
        st.metric(label="Measured Zone", value=res['zone'])
        st.metric(label="Interpretation", value=f"{res['color']} {res['interpretation']}")

    st.write("")
    col1, col2 = st.columns(2)
    col1.button("← Start New Analysis", use_container_width=True, on_click=set_view, args=('setup',))
    col2.button("View History →", use_container_width=True, on_click=set_view, args=('history',))


# ==========================================
# VIEW 4: HISTORY
# ==========================================
elif st.session_state.current_view == 'history':
    st.markdown("<h3 style='text-align: center;'>🕒 Saved Outcomes</h3>", unsafe_allow_html=True)
    
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
    st.button("← Back to Analysis", use_container_width=True, on_click=set_view, args=('setup',))


# ==========================================
# VIEW 5: PERFORMANCE DASHBOARD
# ==========================================
elif st.session_state.current_view == 'performance':
    st.markdown("### 📊 Performance Dashboard")
    
    if not st.session_state.history:
        st.warning("Dashboard is using sample data. Run actual tests to see live metrics!")
        df = pd.DataFrame([
            {"result": "Non-Reistant", "bacterium": "E. coli"}, {"result": "Non-Resistant", "bacterium": "E. coli"},
            {"result": "Non-Resistant", "bacterium": "S. aureus"}, {"result": "Semi-Resistant", "bacterium": "S. aureus"},
            {"result": "Resistant", "bacterium": "P. aeruginosa"}, {"result": "Non-Resistant", "bacterium": "P. aeruginosa"}
        ])
    else:
        df = pd.DataFrame(st.session_state.history)

    total_tests = len(df)
    resistant_count = len(df[df['result'] == 'Resistant'])
    res_rate = int((resistant_count / total_tests) * 100) if total_tests > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tests", total_tests)
    col2.metric("Total Results", total_tests * 8) 
    col3.metric("Recent Activity", total_tests)
    col4.metric("Resistance Rate", f"{res_rate}%")

    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        with st.container(border=True):
            st.markdown("**Interpretation Distribution**")
            pie_data = df['result'].value_counts().reset_index()
            pie_data.columns = ['Result', 'Count']
            color_map = {'Non-Resistant': '#10B981', 'Semi-Resistant': '#F59E0B', 'Resistant': '#EF4444'}
            fig_pie = px.pie(pie_data, values='Count', names='Result', hole=0.4, color='Result', color_discrete_map=color_map)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Tested Bacteria**")
            bar_data = df['bacterium'].value_counts().reset_index()
            bar_data.columns = ['Bacterium', 'Count']
            fig_bar = px.bar(bar_data, x='Bacterium', y='Count')
            fig_bar.update_traces(marker_color='#3B82F6') 
            fig_bar.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, xaxis_title="", yaxis_title="")
            st.plotly_chart(fig_bar, use_container_width=True)