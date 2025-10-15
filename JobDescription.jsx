import React, { useState } from 'react';
import axios from 'axios';

const JobDescription = ({ onJobCreate }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    required_skills: '',
    required_experience: '',
    required_education: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const jobData = {
      ...formData,
      required_skills: formData.required_skills.split(',').map(skill => skill.trim()),
      required_experience: parseFloat(formData.required_experience) || 0
    };

    try {
      const response = await axios.post('http://localhost:8000/job-descriptions/', jobData);
      alert('Job description created successfully!');
      onJobCreate(prev => [...prev, response.data]);
      setFormData({
        title: '',
        description: '',
        required_skills: '',
        required_experience: '',
        required_education: ''
      });
    } catch (error) {
      console.error('Error creating job description:', error);
      alert('Error creating job description: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="card">
      <h2>💼 Create Job Description</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Job Title *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            placeholder="e.g., Senior Software Engineer"
          />
        </div>

        <div className="form-group">
          <label>Job Description *</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows="6"
            placeholder="Enter detailed job description..."
          />
        </div>

        <div className="form-group">
          <label>Required Skills (comma-separated) *</label>
          <input
            type="text"
            name="required_skills"
            value={formData.required_skills}
            onChange={handleChange}
            required
            placeholder="e.g., Python, React, AWS, Machine Learning"
          />
        </div>

        <div className="form-group">
          <label>Required Experience (years) *</label>
          <input
            type="number"
            name="required_experience"
            value={formData.required_experience}
            onChange={handleChange}
            required
            min="0"
            step="0.5"
            placeholder="e.g., 3.5"
          />
        </div>

        <div className="form-group">
          <label>Required Education</label>
          <input
            type="text"
            name="required_education"
            value={formData.required_education}
            onChange={handleChange}
            placeholder="e.g., Bachelor's in Computer Science"
          />
        </div>

        <button type="submit" className="btn">Create Job Description</button>
      </form>
    </div>
  );
};

export default JobDescription;