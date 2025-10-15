import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CandidateList = () => {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedResumes, setSelectedResumes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectAll, setSelectAll] = useState(false);
  const [showCurrentMatchesOnly, setShowCurrentMatchesOnly] = useState(true);
  const [currentSessionMatches, setCurrentSessionMatches] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'match_score', direction: 'desc' });
  const [resetting, setResetting] = useState(false);                                                                                                                                

  useEffect(() => {
    fetchResumes();
    fetchJobs();
    fetchMatchResults();
  }, []);

  // Update selected resumes when selectAll changes
  useEffect(() => {
    if (selectAll) {
      setSelectedResumes(resumes.map(resume => resume.id));
    } else {
      setSelectedResumes([]);
    }
  }, [selectAll, resumes]);

  const fetchResumes = async () => {
    try {
      const response = await axios.get('http://localhost:8000/resumes/');
      setResumes(response.data);
    } catch (error) {
      console.error('Error fetching resumes:', error);
    }
  };

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/job-descriptions/');
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const fetchMatchResults = async () => {
    try {
      const response = await axios.get('http://localhost:8000/match-results/');
      setMatches(response.data);
    } catch (error) {
      console.error('Error fetching matches:', error);
    }
  };

  const handleResumeSelection = (resumeId) => {
    setSelectedResumes(prev => {
      if (prev.includes(resumeId)) {
        return prev.filter(id => id !== resumeId);
      } else {
        return [...prev, resumeId];
      }
    });
  };

  const handleSelectAll = () => {
    setSelectAll(!selectAll);
  };

  const handleMatchSelected = async () => {
    if (!selectedJob) {
      alert('Please select a job description first');
      return;
    }

    if (selectedResumes.length === 0) {
      alert('Please select at least one resume to match');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/bulk-match/', {
        resume_ids: selectedResumes,
        job_description_id: parseInt(selectedJob)
      });

      // Store current session matches separately
      setCurrentSessionMatches(response.data.results);
      
      // Also update main matches for persistence
      setMatches(prev => [...prev, ...response.data.results]);
      
      alert(`Matched ${response.data.results.length} selected candidates successfully!`);
      
      // Clear selection after matching
      setSelectedResumes([]);
      setSelectAll(false);
    } catch (error) {
      console.error('Error in bulk match:', error);
      alert('Error matching candidates: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleMatchAll = async () => {
    if (!selectedJob) {
      alert('Please select a job description first');
      return;
    }

    setLoading(true);
    try {
      const resumeIds = resumes.map(resume => resume.id);
      const response = await axios.post('http://localhost:8000/bulk-match/', {
        resume_ids: resumeIds,
        job_description_id: parseInt(selectedJob)
      });

      // Store current session matches separately
      setCurrentSessionMatches(response.data.results);
      
      // Also update main matches for persistence
      setMatches(prev => [...prev, ...response.data.results]);
      
      alert(`Matched all ${response.data.results.length} candidates successfully!`);
    } catch (error) {
      console.error('Error in bulk match:', error);
      alert('Error matching candidates: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const clearCurrentMatches = () => {
    setCurrentSessionMatches([]);
  };

  const getScoreClass = (score) => {
    if (score >= 8) return 'score-high';
    if (score >= 6) return 'score-medium';
    return 'score-low';
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const getDisplayMatches = () => {
    let matchesToDisplay = [];
    
    if (showCurrentMatchesOnly) {
      matchesToDisplay = currentSessionMatches;
    } else {
      const jobMatches = matches.filter(match => 
        !selectedJob || match.job_description_id === parseInt(selectedJob)
      );
      
      // For existing matches, we need to manually link resume data
      const enhancedMatches = jobMatches.map(match => {
        // Check if match already has resume data (from new API)
        if (match.resume) {
          return match;
        }
        
        // For old matches, manually link data
        const resume = resumes.find(r => r.id === match.resume_id);
        const job = jobs.find(j => j.id === match.job_description_id);
        
        return {
          ...match,
          resume: resume || { name: 'Unknown Candidate', email: 'N/A', experience: 0, skills: [] },
          job_description: job || { title: 'Unknown Position' }
        };
      });
      
      matchesToDisplay = enhancedMatches;
    }

    // Sort the matches
    return matchesToDisplay.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (aValue < bValue) {
        return sortConfig.direction === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return sortConfig.direction === 'asc' ? 1 : -1;
      }
      return 0;
    });
  };

  const selectedCount = selectedResumes.length;
  const totalResumes = resumes.length;
  const displayMatches = getDisplayMatches();
  const hasCurrentMatches = currentSessionMatches.length > 0;

  return (
    <div>
      <div className="card">
        <h2>👥 Candidate Matching</h2>
        
        <div className="form-group">
          <label>Select Job Description</label>
          <select 
            value={selectedJob} 
            onChange={(e) => setSelectedJob(e.target.value)}
          >
            <option value="">Select a job description</option>
            {jobs.map(job => (
              <option key={job.id} value={job.id}>
                {job.title}
              </option>
            ))}
          </select>
        </div>

        {/* Resume Selection Section */}
        <div className="resume-selection-section">
          <h3>Select Resumes to Match</h3>
          <div className="selection-controls">
            <div className="select-all-control">
              <input
                type="checkbox"
                id="select-all"
                checked={selectAll}
                onChange={handleSelectAll}
              />
              <label htmlFor="select-all">
                Select All Resumes ({totalResumes})
              </label>
            </div>
            <div className="selection-count">
              {selectedCount} of {totalResumes} selected
            </div>
          </div>

          <div className="resume-list">
            {resumes.map(resume => (
              <div key={resume.id} className="resume-item">
                <input
                  type="checkbox"
                  id={`resume-${resume.id}`}
                  checked={selectedResumes.includes(resume.id)}
                  onChange={() => handleResumeSelection(resume.id)}
                />
                <label htmlFor={`resume-${resume.id}`} className="resume-label">
                  <span className="resume-name">{resume.name}</span>
                  <span className="resume-details">
                    {resume.email} • {resume.experience} years experience • {resume.skills?.length || 0} skills
                  </span>
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button 
            className="btn btn-secondary"
            onClick={handleMatchSelected}
            disabled={loading || !selectedJob || selectedCount === 0}
          >
            {loading ? 'Matching...' : `Match Selected (${selectedCount})`}
          </button>
          
          <button 
            className="btn"
            onClick={handleMatchAll}
            disabled={loading || !selectedJob || totalResumes === 0}
          >
            {loading ? 'Matching...' : `Match All (${totalResumes})`}
          </button>
        </div>

        {/* Match Results Filter */}
        {hasCurrentMatches && (
          <div className="match-filter-section">
            <h3>Match Results</h3>
            <div className="filter-controls">
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={showCurrentMatchesOnly}
                  onChange={(e) => setShowCurrentMatchesOnly(e.target.checked)}
                />
                <span>Show only current session matches</span>
              </label>
              {showCurrentMatchesOnly && (
                <button 
                  className="btn btn-clear"
                  onClick={clearCurrentMatches}
                >
                  Clear Current Results
                </button>
              )}
            </div>
            <div className="match-stats">
              Showing {displayMatches.length} match{displayMatches.length !== 1 ? 'es' : ''}
              {showCurrentMatchesOnly && ` (from current session)`}
            </div>
          </div>
        )}
      </div>

      {/* Horizontal Match Results Table */}
      {displayMatches.length > 0 ? (
        <div className="card">
          <div className="table-container">
            <table className="matches-table">
              <thead>
                <tr>
                  <th 
                    className="sortable" 
                    onClick={() => handleSort('match_score')}
                  >
                    Score {sortConfig.key === 'match_score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th>Candidate</th>
                  <th>Email</th>
                  <th 
                    className="sortable" 
                    onClick={() => handleSort('resume.experience')}
                  >
                    Experience {sortConfig.key === 'resume.experience' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th>Skills</th>
                  <th>Strengths</th>
                  <th>Gaps</th>
                  <th>Analysis</th>
                </tr>
              </thead>
              <tbody>
                {displayMatches.map((match, index) => (
                  <tr key={index} className="match-row">
                    <td>
                      <div className={`score-badge ${getScoreClass(match.match_score)}`}>
                        {match.match_score}/10
                      </div>
                    </td>
                    <td className="candidate-info">
                      <div className="candidate-name">{match.resume?.name || 'Unknown'}</div>
                    </td>
                    <td className="candidate-email">
                      {match.resume?.email || 'N/A'}
                    </td>
                    <td className="experience">
                      {match.resume?.experience || 0} years
                    </td>
                    <td className="skills-column">
                      <div className="skills-tags">
                        {(match.resume?.skills || []).slice(0, 3).map((skill, idx) => (
                          <span key={idx} className="skill-tag-small">{skill}</span>
                        ))}
                        {(match.resume?.skills || []).length > 3 && (
                          <span className="more-skills">+{(match.resume.skills.length - 3)} more</span>
                        )}
                      </div>
                    </td>
                    <td className="strengths-column">
                      <ul className="strengths-list-small">
                        {match.strengths && match.strengths.slice(0, 2).map((strength, idx) => (
                          <li key={idx} className="strength-item-small">✅ {strength}</li>
                        ))}
                      </ul>
                    </td>
                    <td className="gaps-column">
                      <ul className="gaps-list-small">
                        {match.gaps && match.gaps.slice(0, 2).map((gap, idx) => (
                          <li key={idx} className="gap-item-small">❌ {gap}</li>
                        ))}
                      </ul>
                    </td>
                    <td className="analysis-column">
                      <div className="justification-text">
                        {match.justification}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card empty-results">
          {hasCurrentMatches ? (
            <p>No matches found for the current filters. Try changing your filter settings.</p>
          ) : (
            <p>No match results found. Upload resumes, create job descriptions, and run matching to see results.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default CandidateList;