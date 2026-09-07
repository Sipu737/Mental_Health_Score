import streamlit as st
import requests
import time

# --- CONFIGURATION ---
API_URL = "https://mental-health-score-0w1g.onrender.com/predict"

st.set_page_config(
    page_title="Student Mental Health Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
def load_css():
    st.markdown("""
        <style>
        /* Modern Dark Theme Overrides */
        .stApp {
            background-color: #0B1120;
            color: #F8FAFC;
        }
        
        /* Hero Section */
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            color: #F8FAFC;
            margin-bottom: 0rem;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #94A3B8;
            margin-bottom: 1.5rem;
        }
        .ml-badge {
            background: linear-gradient(135deg, #0EA5E9, #3B82F6);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 1rem;
        }
        .gradient-line {
            height: 3px;
            background: linear-gradient(90deg, #0EA5E9, transparent);
            margin-top: 1rem;
            margin-bottom: 2rem;
        }

        /* Custom Cards */
        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
            background-color: #1E293B;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        
        /* Results Section */
        .score-hero {
            font-size: 5rem;
            font-weight: 900;
            text-align: center;
            background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .score-label {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        .label-healthy { color: #10B981; }
        .label-moderate { color: #F59E0B; }
        .label-attention { color: #EF4444; }

        /* Progress Bar */
        .gauge-container {
            width: 100%;
            background-color: #334155;
            border-radius: 10px;
            height: 12px;
            margin: 20px 0;
            position: relative;
        }
        .gauge-fill {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, #EF4444, #F59E0B, #10B981);
            transition: width 1s ease-in-out;
        }
        .gauge-marker {
            position: absolute;
            top: -5px;
            width: 4px;
            height: 22px;
            background-color: white;
            border-radius: 2px;
            box-shadow: 0 0 4px rgba(0,0,0,0.5);
        }
        .gauge-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #94A3B8;
            font-weight: 600;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, #2563EB, #0EA5E9);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton button:hover {
            background: linear-gradient(135deg, #1D4ED8, #0284C7);
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
            border: none;
        }
        
        /* Metric overriding */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #38BDF8;
        }
        </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
def init_session_state():
    defaults = {
        'age': 21, 'gender': 'Male', 'country': 'India', 'academic_level': 'Undergraduate',
        'platform': 'Instagram', 'purpose': 'Education', 'usage_hours': 5.5, 'unlocks': 50,
        'study_hours': 5.0, 'activity_hours': 1.5, 'sleep_hours': 7.0, 'stress': 'Medium'
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def reset_form():
    st.session_state.clear()
    init_session_state()

# --- API HELPERS ---
def check_api_status():
    try:
        base_url = API_URL.replace("/predict", "/")
        res = requests.get(base_url, timeout=2)
        return True if res.status_code == 200 else False
    except:
        return False

def get_prediction(payload):
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "Mental_Health_Score" in data:
            return data["Mental_Health_Score"], None
        return None, "Invalid JSON response: Missing 'Mental_Health_Score'."
    except requests.exceptions.Timeout:
        return None, "Connection timed out. The server took too long to respond."
    except requests.exceptions.ConnectionError:
        return None, "Unable to connect to the prediction server. Please make sure the FastAPI backend is running."
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP Error: {e.response.status_code}. Please check your inputs."
    except Exception as e:
        return None, "An unexpected error occurred while communicating with the API."

# --- INSIGHTS GENERATOR ---
def generate_personalized_insights(payload):
    insights = []
    if payload["Avg_Daily_Usage_Hours"] >= 7:
        insights.append(("📱 High social-media usage", "Your reported daily social-media usage is relatively high. Consider setting intentional screen-time boundaries."))
    if payload["Sleep_Hours_Per_Night"] < 6:
        insights.append(("😴 Low sleep", "Your reported sleep duration is relatively low. Improving sleep consistency may support overall wellbeing."))
    if payload["Physical_Activity_Hours"] < 2:
        insights.append(("🏃 Low physical activity", "Your reported physical activity is limited. Adding regular movement could help create a more balanced routine."))
    if payload["Stress_Level"] in ["High", "Very High"]:
        insights.append(("⚠️ Elevated stress", "Your reported stress level is elevated. Consider stress-management strategies and regular recovery time."))
    if payload["Study_Hours"] >= 8:
        insights.append(("📚 Intensive study schedule", "Your study schedule appears intensive. Make sure your routine includes breaks and adequate recovery."))
    
    if not insights:
        insights.append(("⚖️ Balanced inputs", "Your reported lifestyle appears relatively balanced across several of the measured factors."))
    
    return insights

# --- UI COMPONENTS ---
def render_sidebar():
    with st.sidebar:
        st.markdown("### About the Project")
        st.write("This application uses a machine-learning regression model to estimate a student's mental health score from demographic, academic, lifestyle, stress, and social-media behavior data.")
        
        st.markdown("---")
        st.markdown("### Technology Stack")
        st.markdown("""
        **Frontend** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Streamlit  
        **Backend** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FastAPI  
        **ML Model** &nbsp;&nbsp;&nbsp;&nbsp;Random Forest Regressor  
        **Pipeline** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Scikit-learn
        """)
        
        st.markdown("---")
        st.markdown("### API Status")
        if check_api_status():
            st.markdown("🟢 **API Connected**")
        else:
            st.markdown("🔴 **API Offline**")
            
        st.markdown("---")
        st.button("↻ Reset Form Defaults", on_click=reset_form, use_container_width=True)

def render_header():
    st.markdown('<div class="ml-badge">MACHINE LEARNING • RANDOM FOREST</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="hero-title">🧠 Student Mental Health<br>Score Predictor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Estimate a student\'s mental health score using lifestyle, academic, stress, and digital behavior patterns.</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-line"></div>', unsafe_allow_html=True)

def render_input_cards():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👤 Student Profile")
        st.slider("Age", 10, 100, key="age")
        st.selectbox("Gender", ["Male", "Female"], key="gender")
        st.selectbox("Country", ["Other", "Canada", "USA", "India", "Australia", "UK", "Germany"], key="country")
        st.selectbox("Academic Level", ["Undergraduate", "Graduate", "High School"], key="academic_level")
        
    with col2:
        st.markdown("### 📱 Digital Behavior")
        st.selectbox("Most Used Platform", ["Facebook", "LinkedIn", "Instagram", "Snapchat", "Twitter", "YouTube", "TikTok", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"], key="platform")
        st.selectbox("Purpose Of Use", ["Networking", "Education", "Entertainment", "News"], key="purpose")
        st.slider("Avg Daily Usage Hours", 0.0, 24.0, step=0.1, key="usage_hours")
        st.slider("Daily Unlocks", 0, 1000, step=1, key="unlocks")
        
    with col3:
        st.markdown("### 🌿 Lifestyle & Wellness")
        st.slider("Study Hours", 0.0, 24.0, step=0.1, key="study_hours")
        st.slider("Physical Activity Hours", 0.0, 24.0, step=0.1, key="activity_hours")
        st.slider("Sleep Hours Per Night", 0.0, 24.0, step=0.1, key="sleep_hours")
        st.selectbox("Stress Level", ["Low", "Medium", "High", "Very High"], key="stress")

def render_prediction_results(score, payload):
    st.markdown("---")
    st.markdown("## 📊 Prediction Results")
    
    # Logic for Interpretation
    if score >= 70:
        label = "Healthy Range"
        desc = "The predicted score indicates a relatively healthier pattern based on the information provided."
        css_class = "label-healthy"
    elif score >= 40:
        label = "Moderate Range"
        desc = "The prediction suggests that some lifestyle or behavioral areas may benefit from greater balance."
        css_class = "label-moderate"
    else:
        label = "Needs Attention"
        desc = "The predicted score suggests that some lifestyle or behavioral factors may warrant closer attention."
        css_class = "label-attention"

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div style="text-align: center; color: #94A3B8; font-weight: 600; letter-spacing: 2px;">MENTAL HEALTH SCORE</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-hero">{score:.2f}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-label {css_class}">{label.upper()}</p>', unsafe_allow_html=True)
        
        # Progress Bar / Gauge
        marker_pos = max(0, min(100, score))
        st.markdown(f"""
            <div class="gauge-container">
                <div class="gauge-fill" style="width: 100%;"></div>
                <div class="gauge-marker" style="left: {marker_pos}%;"></div>
            </div>
            <div class="gauge-labels">
                <span>0</span>
                <span>50</span>
                <span>100</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #cbd5e1;'>{desc}</p>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: rgba(245, 158, 11, 0.1); border-left: 4px solid #F59E0B; padding: 12px; border-radius: 4px; margin-top: 20px;">
            <p style="color: #FCD34D; font-size: 0.85rem; margin: 0;"><b>⚠ Educational Prediction:</b> This machine-learning prediction is for educational and demonstration purposes only. It is not a medical diagnosis and should not replace professional mental-health advice.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### 💡 Personalized Insights")
        insights = generate_personalized_insights(payload)
        for title, text in insights:
            st.markdown(f"**{title}**<br><span style='color: #94A3B8;'>{text}</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Your Submitted Profile")
    
    # Analytics Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📱 Screen Time", f"{payload['Avg_Daily_Usage_Hours']} hrs")
    m2.metric("📚 Study", f"{payload['Study_Hours']} hrs")
    m3.metric("😴 Sleep", f"{payload['Sleep_Hours_Per_Night']} hrs")
    m4.metric("🏃 Activity", f"{payload['Physical_Activity_Hours']} hrs")
    
    # Data Grid
    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f"**Age:** {payload['Age']}<br>**Gender:** {payload['Gender']}<br>**Country:** {payload['Country']}<br>**Academic Level:** {payload['Academic_Level']}", unsafe_allow_html=True)
    with g2:
        st.markdown(f"**Daily Unlocks:** {payload['Daily_Unlocks']}<br>**Stress:** {payload['Stress_Level']}<br>**Platform:** {payload['Most_Used_Platform']}<br>**Purpose:** {payload['Purpose_Of_Use']}", unsafe_allow_html=True)

# --- MAIN APP FLOW ---
def main():
    load_css()
    init_session_state()
    render_sidebar()
    render_header()
    render_input_cards()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔮 Predict Mental Health Score"):
        payload = {
            "Age": st.session_state.age,
            "Gender": st.session_state.gender,
            "Country": st.session_state.country,
            "Academic_Level": st.session_state.academic_level,
            "Most_Used_Platform": st.session_state.platform,
            "Purpose_Of_Use": st.session_state.purpose,
            "Avg_Daily_Usage_Hours": st.session_state.usage_hours,
            "Daily_Unlocks": st.session_state.unlocks,
            "Study_Hours": st.session_state.study_hours,
            "Physical_Activity_Hours": st.session_state.activity_hours,
            "Sleep_Hours_Per_Night": st.session_state.sleep_hours,
            "Stress_Level": st.session_state.stress
        }
        
        with st.spinner("Analyzing profile and generating prediction..."):
            score, error = get_prediction(payload)
            
        if error:
            st.error(error)
        else:
            render_prediction_results(score, payload)

if __name__ == "__main__":
    main()