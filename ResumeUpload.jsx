import React, { useState } from 'react';
import axios from 'axios';

const ResumeUpload = ({ onResumeUpload }) => {
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleFileUpload = async (file) => {
    if (!file || file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);

    try {
      const response = await axios.post('http://localhost:8000/upload-resume/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      alert('Resume uploaded successfully!');
      onResumeUpload(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading resume: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  return (
    <div className="card">
      <h2>📄 Upload Resume</h2>
      <p>Upload PDF resumes to parse and analyze candidate information</p>
      
      <div
        className={`upload-area ${dragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input').click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={(e) => handleFileUpload(e.target.files[0])}
        />
        
        {uploading ? (
          <div>
            <div className="loading"></div>
            <p>Processing resume...</p>
          </div>
        ) : (
          <div>
            <p>📁 Drag & drop a PDF resume here</p>
            <p>or click to browse</p>
            <p style={{ fontSize: '0.8rem', color: '#666', marginTop: '1rem' }}>
              Supported format: PDF only
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload;