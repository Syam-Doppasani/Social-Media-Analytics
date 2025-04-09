# app.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time
import os
from PIL import Image

# Configuration
API_URL = "http://localhost:8000"  # Change this if your API is hosted elsewhere
DEFAULT_USER = "user123"

# Page Setup
st.set_page_config(
    page_title="Instagram Optimizer Pro",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #405de6;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        border-radius: 10px 10px 0 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def call_api(endpoint, method="GET", json_data=None):
    try:
        if method == "GET":
            response = requests.get(f"{API_URL}{endpoint}")
        else:
            response = requests.post(f"{API_URL}{endpoint}", json=json_data)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Initialize Session State
if 'user_id' not in st.session_state:
    st.session_state.user_id = DEFAULT_USER
if 'prediction' not in st.session_state:
    st.session_state.prediction = None

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=100)
    st.title("Account Settings")
    
    # User ID Input
    st.session_state.user_id = st.text_input(
        "Your User ID", 
        value=st.session_state.user_id,
        help="This identifies your personal model"
    )
    
    st.markdown("---")
    st.markdown("""
    **How it works:**
    1. Add your historical posts
    2. Train your personal model
    3. Get optimized recommendations
    """)
    
    # Model Info
    model_info = call_api(f"/model-info/{st.session_state.user_id}")
    if model_info:
        st.markdown("---")
        st.markdown("**Your Model Status**")
        st.caption(f"Trained on: {model_info.get('training_posts', 0)} posts")
        st.caption(f"Last updated: {model_info.get('last_modified', 'Never')}")

# Main App
def main():
    st.title("📈 Instagram Post Optimizer")
    st.markdown("Boost your engagement with AI-powered recommendations")
    
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Predict", "📚 Train Model", "📊 Analytics"])
    
    # Prediction Tab
    with tab1:
        st.header("Create Optimized Post")
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            # Post Content Form
            with st.form("prediction_form"):
                caption = st.text_area(
                    "Post Caption", 
                    "Just posted a new workout! #fitness",
                    height=150
                )
                
                col1a, col1b = st.columns(2)
                with col1a:
                    media_type = st.radio(
                        "Media Type", 
                        ["image", "video"],
                        horizontal=True
                    )
                with col1b:
                    niche = st.selectbox(
                        "Content Niche",
                        ["fitness", "food", "travel", "fashion", "tech"]
                    )
                
                col2a, col2b = st.columns(2)
                with col2a:
                    hour = st.slider(
                        "Posting Hour", 
                        0, 23, 18,
                        help="Best times are usually 9-11am or 7-9pm"
                    )
                with col2b:
                    day = st.selectbox(
                        "Day of Week",
                        ["Monday", "Tuesday", "Wednesday", "Thursday", 
                         "Friday", "Saturday", "Sunday"],
                        index=2
                    )
                
                hashtag_count = st.slider(
                    "Number of Hashtags", 
                    0, 30, 5,
                    help="5-10 niche-specific hashtags work best"
                )
                
                submitted = st.form_submit_button(
                    "Get Recommendations", 
                    type="primary"
                )
        
        with col2:
            # Results Display
            if submitted:
                with st.spinner("Analyzing your post..."):
                    # Call prediction API
                    prediction = call_api(
                        "/predict",
                        method="POST",
                        json_data={
                            "user_id": st.session_state.user_id,
                            "caption": caption,
                            "media_type": media_type,
                            "hour": hour,
                            "day_of_week": ["Monday", "Tuesday", "Wednesday", 
                                          "Thursday", "Friday", "Saturday", 
                                          "Sunday"].index(day),
                            "hashtag_count": hashtag_count,
                            "niche": niche
                        }
                    )
                    
                    if prediction:
                        st.session_state.prediction = prediction
                        st.success("Optimization complete!")
            
            if st.session_state.prediction:
                pred = st.session_state.prediction
                
                # Metrics
                st.subheader("Predicted Performance")
                m1, m2, m3 = st.columns(3)
                m1.metric("Estimated Likes", f"{pred['likes']:,}")
                m2.metric("Expected Comments", f"{pred['comments']:,}")
                m3.metric("New Followers", f"+{pred['new_followers']}")
                
                # Recommendations
                st.subheader("Optimization Tips")
                
                with st.expander("💬 Caption Improvements", expanded=True):
                    st.markdown("""
                    - **Add power words**: Try "🔥 PROVEN workout routine" 
                    - **Include a CTA**: "Which exercise is your favorite? Comment below!"
                    - **Optimal length**: 138-150 characters
                    """)
                
                with st.expander("⏰ Posting Strategy"):
                    days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                           "Friday", "Saturday", "Sunday"]
                    best_day = days[(hour % 7)]  # Example calculation
                    st.markdown(f"""
                    - **Recommended Day**: {best_day}
                    - **Best Time**: {hour}:00
                    - **Hashtag Strategy**: Use {hashtag_count} niche-specific tags
                    """)
    
    # Training Tab
    with tab2:
        st.header("Improve Your Model")
        st.markdown("Add your historical posts to train your personal AI")
        
        # File Upload
        uploaded_file = st.file_uploader(
            "Upload your post history (CSV)", 
            type="csv",
            help="Requires columns: timestamp,likes,comments,new_followers,media_type,hashtags,caption"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Preview
                with st.expander("Preview your data"):
                    st.dataframe(df.head())
                
                # Validate columns
                required_cols = {'timestamp', 'likes', 'comments', 'new_followers', 
                               'media_type', 'hashtags', 'caption'}
                if not required_cols.issubset(df.columns):
                    missing = required_cols - set(df.columns)
                    st.error(f"Missing columns: {', '.join(missing)}")
                else:
                    if st.button("Train My Model", type="primary"):
                        with st.spinner("Training your personal model..."):
                            # Prepare training data
                            posts = df.to_dict('records')
                            response = call_api(
                                "/train",
                                method="POST",
                                json_data={
                                    "user_id": st.session_state.user_id,
                                    "posts": posts
                                }
                            )
                            
                            if response:
                                st.success(
                                    f"Model trained on {len(posts)} posts! "
                                    f"Now using version: {response.get('last_trained')}"
                                )
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    # Analytics Tab
    with tab3:
        st.header("Performance Analytics")
        
        # Model Info
        model_info = call_api(f"/model-info/{st.session_state.user_id}")
        if model_info:
            st.subheader("Model Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Training Posts", model_info.get('training_posts', 0))
            col2.metric("Last Trained", model_info.get('last_modified', 'Never')[:10])
            col3.metric("Model Version", model_info.get('model_version', '1.0')[-6:])
        
        # Sample Analytics (in production, use real data)
        st.subheader("Engagement Trends")
        
        # Generate sample data
        dates = pd.date_range(end=datetime.today(), periods=30)
        trend_data = pd.DataFrame({
            'Date': dates,
            'Likes': (np.random.rand(30) * 500 + 100).cumsum(),
            'Comments': (np.random.rand(30) * 50 + 10).cumsum(),
            'Followers': (np.random.rand(30) * 20 + 5).cumsum()
        })
        
        # Plot
        tab1, tab2 = st.tabs(["📈 Trends", "📅 Calendar"])
        
        with tab1:
            st.line_chart(
                trend_data.set_index('Date'),
                y=['Likes', 'Comments', 'Followers'],
                color=["#FF0000", "#00FF00", "#0000FF"]
            )
        
        with tab2:
            st.calendar_chart(
                trend_data.set_index('Date')['Likes'].reset_index(),
                x='Date',
                y='Likes'
            )

if __name__ == "__main__":
    main()