import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Resume Screener", layout="wide")

st.title("📄 Smart Resume Screener with Database")
st.write("AI-powered resume analysis with persistent storage")

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Analyze Resume", "View History", "Candidate Search"])

if page == "Analyze Resume":
    st.header("🔍 Analyze New Resume")
    
    job_description = st.text_area("Job Description", height=200, placeholder="Paste the job description here...")
    resume_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])

    if st.button("Analyze Resume") and resume_file and job_description:
        with st.spinner("Analyzing resume with AI..."):
            try:
                files = {
                    "resume": (resume_file.name, resume_file.getvalue(), "application/pdf")
                }
                
                data = {
                    "description": job_description
                }
                
                response = requests.post(
                    "http://localhost:8000/analyze-resume/",
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Analysis Complete! Match Score: {result['match_score']}/10")
                    st.info(f"📊 Analysis ID: {result['id']} | Saved to database")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Skills Matched:")
                        for skill in result['skills_matched']:
                            st.write(f"- {skill}")
                    
                    with col2:
                        st.subheader("❌ Skills Missing:")
                        for skill in result['skills_missing']:
                            st.write(f"- {skill}")
                    
                    st.subheader("📝 Justification:")
                    st.write(result['justification'])
                    
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

elif page == "View History":
    st.header("📊 Analysis History")
    
    if st.button("Load All Analyses"):
        try:
            response = requests.get("http://localhost:8000/analyses/")
            if response.status_code == 200:
                analyses = response.json()
                
                if analyses:
                    # Create DataFrame for better display
                    df_data = []
                    for analysis in analyses:
                        df_data.append({
                            "ID": analysis["id"],
                            "Candidate": analysis["candidate_name"],
                            "Score": analysis["match_score"],
                            "Date": analysis["created_at"][:10],
                            "Matched Skills": len(analysis["skills_matched"]),
                            "Missing Skills": len(analysis["skills_missing"])
                        })
                    
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show details when selected
                    selected_id = st.selectbox("Select analysis to view details:", [a["id"] for a in analyses])
                    
                    if selected_id:
                        selected_analysis = next(a for a in analyses if a["id"] == selected_id)
                        st.subheader(f"Details for Analysis #{selected_analysis['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Match Score", f"{selected_analysis['match_score']}/10")
                            st.write("**Skills Matched:**")
                            for skill in selected_analysis['skills_matched']:
                                st.write(f"✅ {skill}")
                        
                        with col2:
                            st.metric("Analysis Date", selected_analysis['created_at'][:10])
                            st.write("**Skills Missing:**")
                            for skill in selected_analysis['skills_missing']:
                                st.write(f"❌ {skill}")
                        
                        st.write("**Justification:**")
                        st.write(selected_analysis['justification'])
                else:
                    st.info("No analyses found in the database.")
            else:
                st.error("Failed to load analyses from database")
                
        except Exception as e:
            st.error(f"Error loading analyses: {str(e)}")

elif page == "Candidate Search":
    st.header("🔍 Search Candidates")
    
    st.info("This feature would allow searching through all analyzed resumes. Additional endpoints needed for full search functionality.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💾 All analyses are stored in SQLite database")