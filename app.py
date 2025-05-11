import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import plotly.graph_objs as go
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GENAI_API_KEY")
if not google_api_key:
    st.error("API key not found. Please set GENAI_API_KEY in your .env file.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Improved prompt template for better structured output
prompt_template_resto = """
Diet Recommendation System:
Based on the following user profile, provide detailed, well-formatted recommendations:

User Profile:
- Name: {name}
- Age: {age}
- Gender: {gender}
- Weight: {weight} kg
- Height: {height} cm
- Diet Preference: {veg_or_nonveg}
- Health Conditions: {disease}
- Region: {region}
- State: {state}
- Allergies: {allergics}
- Food Type Preference: {foodtype}

Please provide recommendations in the following CLEARLY SEPARATED sections:

## RESTAURANTS
Provide 6 restaurant names suitable for this person's diet and preferences. Include a brief description of each.

## BREAKFAST IDEAS
Suggest 6 nutritious breakfast options tailored to their needs. Include ingredients and brief preparation notes.

## DINNER IDEAS
Recommend 5 balanced dinner options appropriate for their diet. Include key ingredients.

## WORKOUT RECOMMENDATIONS
Suggest 6 exercise activities suited to their profile. Include frequency and duration guidelines.

## HEALTH NOTES
Provide 3-4 specific health tips based on their profile.

Format each section with clear headings, bullet points, and concise descriptions.
"""

# Function to generate recommendations
def generate_recommendations(inputs):
    prompt = prompt_template_resto.format(**inputs)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

# Usage tracking
if 'usage_data' not in st.session_state:
    st.session_state.usage_data = []

def capture_usage(user_data):
    usage_entry = {
        'timestamp': datetime.now(),
        'user_age': user_data.get('age', 'Unknown'),
        'user_region': user_data.get('region', 'Unknown')
    }
    st.session_state.usage_data.append(usage_entry)

def create_usage_tracking_graph():
    start_date = date(2024, 1, 1)
    end_date = date.today()
    date_range = pd.date_range(start_date, end_date, freq='W-MON')
    weeks = [date.strftime("%Y-%m-%d") for date in date_range]
    usage_count = [10, 20, 15, 25, 30, 5, 10, 8, 15, 18, 8, 15, 10, 20, 22]  # Example data
    
    fig = go.Figure(data=[
        go.Bar(
            x=weeks, 
            y=usage_count, 
            text=usage_count, 
            textposition='auto',
            marker_color='rgb(26, 118, 255)'
        )
    ])
    
    fig.update_layout(
        title='Weekly Usage Tracking',
        title_font_size=20,
        xaxis_title='Week', 
        yaxis_title='Usage Count',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Calculate BMI and categorize
def calculate_bmi(weight, height):
    try:
        weight_kg = float(weight)
        height_m = float(height) / 100
        bmi = weight_kg / (height_m ** 2)
        return bmi
    except:
        return None

def categorize_bmi(bmi):
    if bmi < 18.5: 
        return "Underweight", "blue", "Consider consulting with a healthcare provider about healthy weight gain."
    elif bmi < 24.9: 
        return "Normal", "green", "Your weight is within a healthy range for your height."
    elif bmi < 29.9: 
        return "Overweight", "orange", "Consider moderate lifestyle changes to achieve a healthier weight."
    else: 
        return "Obesity", "red", "Consider consulting with a healthcare provider about weight management."

# Page configuration
st.set_page_config(
    page_title="Diet & Workout Recommendations",
    page_icon="🥗",
    layout="wide"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    .main-header {
        font-size: 38px;
        font-weight: bold;
        text-align: center;
        color: white;
        background: linear-gradient(to right, #1e3c72, #2a5298);
        padding: 20px 0;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .subtitle {
        font-size: 22px;
        text-align: center;
        color: white;
        background: rgba(42, 82, 152, 0.8);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .form-header {
        font-size: 24px;
        font-weight: bold;
        color: #1e3c72;
        margin-bottom: 15px;
    }
    .form-container {
        background: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .results-container {
        background: white;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    .bmi-container {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #1e3c72;
        margin: 15px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #e0e0e0;
    }
    .markdown-text-container {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #1e3c72;
    }
    .stButton>button {
        background-color: #1e3c72;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">🥗 Diet & Workout Recommendation System 💪</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Personalized suggestions powered by Gemini AI</div>', unsafe_allow_html=True)

# Create columns for form and results
col1, col2 = st.columns([1, 1.5])

# Form Input Column
with col1:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown('<div class="form-header">Enter Your Information</div>', unsafe_allow_html=True)
    
    with st.form(key='user_input_form'):
        name = st.text_input("Full Name")
        
        col_age_gender1, col_age_gender2 = st.columns(2)
        with col_age_gender1:
            age = st.text_input("Age")
        with col_age_gender2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
        col_height_weight1, col_height_weight2 = st.columns(2)
        with col_height_weight1:
            weight = st.text_input("Weight (kg)")
        with col_height_weight2:
            height = st.text_input("Height (cm)")
        
        veg_or_nonveg = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan", "Pescatarian"])
        disease = st.text_input("Health Conditions (if any)")
        
        col_location1, col_location2 = st.columns(2)
        with col_location1:
            region = st.text_input("Region/City")
        with col_location2:
            state = st.text_input("State/Province")
        
        allergics = st.text_input("Allergies (if any)")
        foodtype = st.text_input("Preferred Cuisine (e.g., South Indian, Mediterranean)")
        
        submit_button = st.form_submit_button(label='Generate Recommendations')
    
    st.markdown('</div>', unsafe_allow_html=True)

# Results Column
with col2:
    if submit_button:
        if all([name, age, gender, weight, height, veg_or_nonveg]):
            with st.spinner("Generating personalized recommendations..."):
                input_data = {
                    "name": name, "age": age, "gender": gender,
                    "weight": weight, "height": height,
                    "veg_or_nonveg": veg_or_nonveg, "disease": disease or "None",
                    "region": region or "Not specified", "state": state or "Not specified", 
                    "allergics": allergics or "None", "foodtype": foodtype or "General"
                }
                
                # Track usage
                capture_usage(input_data)
                
                # Calculate BMI
                bmi = calculate_bmi(weight, height)
                
                # Generate recommendations
                recommendations = generate_recommendations(input_data)
                
                # Display results
                st.markdown('<div class="results-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="section-header">Hello {name}! Here are your personalized recommendations:</div>', unsafe_allow_html=True)
                
                # Display BMI information if valid
                if bmi:
                    category, color, message = categorize_bmi(bmi)
                    st.markdown(f"""
                    <div class="bmi-container" style="background-color: rgba({color}, 0.1); border: 2px solid {color};">
                        <h3 style="color: {color};">BMI: {bmi:.1f} - {category}</h3>
                        <p>{message}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display recommendations
                st.markdown('<div class="markdown-text-container">', unsafe_allow_html=True)
                st.markdown(recommendations)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # BMI 3D Visualization
                if bmi:
                    st.markdown('<div class="section-header">BMI Visualization</div>', unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Scatter3d(
                        x=[int(age)], y=[float(weight)], z=[bmi],
                        mode='markers',
                        marker=dict(size=15, color=color, opacity=0.8),
                        text=[f"Age: {age}<br>Weight: {weight} kg<br>BMI: {bmi:.2f} ({category})"],
                        hoverinfo="text"
                    )])
                    fig.update_layout(
                        scene=dict(
                            xaxis_title='Age',
                            yaxis_title='Weight (kg)',
                            zaxis_title='BMI',
                            xaxis=dict(gridcolor='rgb(255, 255, 255)', showbackground=True),
                            yaxis=dict(gridcolor='rgb(255, 255, 255)', showbackground=True),
                            zaxis=dict(gridcolor='rgb(255, 255, 255)', showbackground=True),
                        ),
                        margin=dict(l=0, r=0, b=0, t=0),
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div class="results-container">', unsafe_allow_html=True)
            st.error("Please fill in all required fields to generate recommendations.")
            st.markdown('</div>', unsafe_allow_html=True)

# Usage Statistics Section
st.markdown('<div class="subtitle">Usage Statistics</div>', unsafe_allow_html=True)
create_usage_tracking_graph()

# Footer with disclaimer
st.markdown("""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin-top: 20px; text-align: center; font-size: 12px;">
    <p><strong>Disclaimer:</strong> This application provides general recommendations only and is not a substitute for professional medical advice. 
    Always consult with a healthcare provider or registered dietitian for personalized guidance.</p>
</div>
""", unsafe_allow_html=True)