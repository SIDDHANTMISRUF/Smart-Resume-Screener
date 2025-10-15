import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import ResumeUpload from './components/ResumeUpload';
import JobDescription from './components/JobDescription';
import CandidateList from './components/CandidateList';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [resumes, setResumes] = useState([]);
  const [jobDescriptions, setJobDescriptions] = useState([]);

  return (
    <div className="App">
      <header className="app-header">
        <h1> Smart Resume Screener</h1>
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''} 
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button 
            className={activeTab === 'upload' ? 'active' : ''} 
            onClick={() => setActiveTab('upload')}
          >
            Upload Resume
          </button>
          <button 
            className={activeTab === 'jobs' ? 'active' : ''} 
            onClick={() => setActiveTab('jobs')}
          >
            Job Descriptions
          </button>
          <button 
            className={activeTab === 'candidates' ? 'active' : ''} 
            onClick={() => setActiveTab('candidates')}
          >
            Candidates
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'upload' && <ResumeUpload onResumeUpload={setResumes} />}
        {activeTab === 'jobs' && <JobDescription onJobCreate={setJobDescriptions} />}
        {activeTab === 'candidates' && <CandidateList />}
      </main>
    </div>
  );
}

export default App;