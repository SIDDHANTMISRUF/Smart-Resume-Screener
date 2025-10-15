import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalResumes: 0,
    totalJobs: 0,
    totalMatches: 0,
    averageScore: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [resumesRes, jobsRes, matchesRes] = await Promise.all([
        axios.get('http://localhost:8000/resumes/'),
        axios.get('http://localhost:8000/job-descriptions/'),
        axios.get('http://localhost:8000/match-results/')
      ]);

      const matches = matchesRes.data;
      const avgScore = matches.length > 0 
        ? matches.reduce((sum, match) => sum + match.match_score, 0) / matches.length 
        : 0;

      setStats({
        totalResumes: resumesRes.data.length,
        totalJobs: jobsRes.data.length,
        totalMatches: matches.length,
        averageScore: avgScore.toFixed(1)
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  return (
    <div>
      <div className="card">
        <h1>📊 Dashboard</h1>
        <p>Welcome to Smart Resume Screener - AI-powered candidate matching</p>
      </div>

      <div className="stats-grid" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <div className="card" style={{ textAlign: 'center' }}>
          <h3>📄 Resumes</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
            {stats.totalResumes}
          </p>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <h3>💼 Jobs</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
            {stats.totalJobs}
          </p>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <h3>🎯 Matches</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
            {stats.totalMatches}
          </p>
        </div>

        <div className="card" style={{ textAlign: 'center' }}>
          <h3>⭐ Avg Score</h3>
          <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
            {stats.averageScore}
          </p>
        </div>
      </div>

      <div className="card">
        <h2>🚀 Quick Start</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div style={{ padding: '1rem', border: '2px solid #e1e1e1', borderRadius: '10px' }}>
            <h3>1. Upload Resumes</h3>
            <p>Upload candidate resumes in PDF format for parsing and analysis.</p>
          </div>
          
          <div style={{ padding: '1rem', border: '2px solid #e1e1e1', borderRadius: '10px' }}>
            <h3>2. Create Job Description</h3>
            <p>Define job requirements, skills, and experience needed.</p>
          </div>
          
          <div style={{ padding: '1rem', border: '2px solid #e1e1e1', borderRadius: '10px' }}>
            <h3>3. Match Candidates</h3>
            <p>Use AI to match resumes with job descriptions and get scores.</p>
          </div>
          
          <div style={{ padding: '1rem', border: '2px solid #e1e1e1', borderRadius: '10px' }}>
            <h3>4. Review Results</h3>
            <p>Analyze match scores, strengths, and gaps for each candidate.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;