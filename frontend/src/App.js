import React, { useEffect, useState, useRef } from 'react';

export function App() {
  const [status, setStatus] = useState('');
  const [files, setFiles] = useState([]);
  const [fileNames, setFileNames] = useState([]);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [message, setMessage] = useState('Upload some audio files to get started!');
  const [remixReady, setRemixReady] = useState(false);
  const [remixResult, setRemixResult] = useState(null);
  const [tempo, setTempo] = useState(100);
  const [pitch, setPitch] = useState(0);
  const [effectMix, setEffectMix] = useState(0);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  // Backend status check
  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/`)
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('Backend not reachable'));
  }, []);

  // Handle file selection
  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files);
    setFiles(selected);
    setFileNames(selected.map(f => f.name));
    setRemixReady(selected.length > 0);
    setMessage(selected.length > 0
      ? `Loaded ${selected.length} samples. Ready to generate!`
      : 'Upload some audio files to get started!');
  };

  // Remove a file from the list
  const handleRemoveFile = (idx) => {
    const newFiles = files.slice();
    newFiles.splice(idx, 1);
    setFiles(newFiles);
    setFileNames(newFiles.map(f => f.name));
    setRemixReady(newFiles.length > 0);
    setMessage(newFiles.length > 0
      ? `Loaded ${newFiles.length} samples. Ready to generate!`
      : 'Upload some audio files to get started!');
    // Reset file input if all files removed
    if (newFiles.length === 0 && fileInputRef.current) fileInputRef.current.value = '';
  };

  // Handle YouTube URL submit
  const handleUrlSubmit = async () => {
    if (!youtubeUrl.trim()) {
      setMessage('Please enter a valid URL.');
      return;
    }
    setLoading(true);
    setMessage('Sending URL to backend...');
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/process_url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: youtubeUrl.trim() })
      });
      const data = await response.json();
      if (response.ok) {
        setMessage(data.message || 'URL processed successfully!');
      } else {
        setMessage(data.error || 'Failed to process URL.');
      }
    } catch (err) {
      setMessage('Error connecting to backend.');
    }
    setLoading(false);
  };

  // Handle file upload to backend
  const handleUpload = async () => {
    if (files.length === 0) {
      setMessage('Please select audio files to upload.');
      return;
    }
    setLoading(true);
    setMessage('Uploading files...');
    const formData = new FormData();
    files.forEach(f => formData.append('file', f));
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/upload`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (response.ok) {
        setMessage(data.message || 'Files uploaded!');
        setRemixReady(true);
      } else {
        setMessage(data.error || 'Failed to upload files.');
      }
    } catch (err) {
      setMessage('Error uploading files.');
    }
    setLoading(false);
  };

  // Handle remix generation (stub: just simulates backend call)
  const handleGenerateRemix = async () => {
    setLoading(true);
    setMessage('Generating remix...');
    try {
      // Simulate backend remix endpoint
      const response = await fetch(`${process.env.REACT_APP_API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tempo,
          pitch,
          effectMix,
          files: fileNames
        })
      });
      const data = await response.json();
      if (response.ok) {
        setRemixResult(data);
        setMessage('Remix generated! (Demo: see backend response below)');
      } else {
        setMessage(data.error || 'Failed to generate remix.');
      }
    } catch (err) {
      setMessage('Error connecting to backend.');
    }
    setLoading(false);
  };

  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      background: '#1a202c',
      color: '#e2e8f0',
      minHeight: '100vh',
      padding: 20,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'flex-start'
    }}>
      <div style={{
        background: '#2d3748',
        padding: 30,
        borderRadius: 15,
        boxShadow: '0 10px 20px rgba(0,0,0,0.4)',
        width: '100%',
        maxWidth: 900,
        textAlign: 'center',
        border: '1px solid #4a5568'
      }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: 25, color: '#63b3ed' }}>
          AI DJ Hip-Hop Remixer (React)
        </h1>
        <div className="message-box" style={{
          background: '#4a5568', padding: 20, borderRadius: 10, marginBottom: 20, border: '1px solid #63b3ed',
          minHeight: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', fontStyle: 'italic'
        }}>
          {loading ? <span>Loading...</span> : <span>{message}</span>}
        </div>
        <div className="input-section" style={{
          background: '#4a5568', padding: 20, borderRadius: 10, marginBottom: 20, border: '1px solid #63b3ed'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: 16, color: '#fff' }}>
            1. Upload Your Audio Samples
          </h2>
          <p style={{ fontSize: '0.9rem', color: '#a0aec0', marginBottom: 16 }}>
            (MP3, WAV, OGG supported. Multiple files are encouraged for more variety.)
          </p>
          <label htmlFor="audioFileInput" style={{
            border: '2px dashed #a0aec0', padding: '15px 20px', borderRadius: 8, cursor: 'pointer',
            display: 'inline-block', marginTop: 10, color: '#a0aec0'
          }}>
            <i className="fas fa-cloud-upload-alt" style={{ marginRight: 8 }}></i> Choose Audio Files
          </label>
          <input
            id="audioFileInput"
            type="file"
            accept=".mp3,.wav,.ogg"
            multiple
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          {fileNames.length > 0 && (
            <div style={{
              marginTop: 15, textAlign: 'left', maxHeight: 150, overflowY: 'auto',
              border: '1px solid #63b3ed', borderRadius: 8, padding: 10, background: '#2d3748'
            }}>
              {fileNames.map((name, idx) => (
                <div key={idx} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '8px 0', borderBottom: '1px solid #4a5568'
                }}>
                  <span style={{ flexGrow: 1, marginRight: 10, color: '#cbd5e0' }}>{name}</span>
                  <button
                    style={{
                      background: '#e53e3e', color: '#fff', border: 'none', borderRadius: 5,
                      padding: '5px 8px', cursor: 'pointer', fontSize: '0.8rem'
                    }}
                    onClick={() => handleRemoveFile(idx)}
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              ))}
            </div>
          )}
          <div style={{ marginTop: 24 }}>
            <input
              type="text"
              className="input-url"
              style={{
                width: '70%', padding: 10, borderRadius: 6, border: '1px solid #63b3ed',
                background: '#2d3748', color: '#e2e8f0'
              }}
              placeholder="Paste audio or YouTube URL here..."
              value={youtubeUrl}
              onChange={e => setYoutubeUrl(e.target.value)}
              disabled={loading}
            />
            <button
              className="submit-url-btn"
              style={{
                marginLeft: 10, background: '#63b3ed', color: '#fff', padding: '12px 25px',
                border: 'none', borderRadius: 8, cursor: 'pointer', fontWeight: 'bold'
              }}
              onClick={handleUrlSubmit}
              disabled={loading}
            >
              <i className="fas fa-link" style={{ marginRight: 8 }}></i>Submit URL
            </button>
          </div>
          <div style={{ marginTop: 16 }}>
            <button
              onClick={handleUpload}
              disabled={files.length === 0 || loading}
              style={{
                background: '#63b3ed', color: '#fff', padding: '12px 25px', border: 'none',
                borderRadius: 8, cursor: files.length === 0 ? 'not-allowed' : 'pointer',
                fontWeight: 'bold', marginTop: 10
              }}
            >
              <i className="fas fa-upload" style={{ marginRight: 8 }}></i>Upload Files
            </button>
          </div>
        </div>
        <div className="controls-section" style={{
          background: '#4a5568', padding: 20, borderRadius: 10, marginBottom: 20, border: '1px solid #63b3ed'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: 16, color: '#fff' }}>
            2. Remix Controls
          </h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'center', marginBottom: 16 }}>
            <button
              onClick={handleGenerateRemix}
              disabled={!remixReady || loading}
              style={{
                background: '#63b3ed', color: '#fff', padding: '12px 25px', border: 'none',
                borderRadius: 8, cursor: remixReady ? 'pointer' : 'not-allowed',
                fontWeight: 'bold', margin: '10px 5px'
              }}
            >
              <i className="fas fa-magic" style={{ marginRight: 8 }}></i> Generate Remix
            </button>
          </div>
          <div className="slider-group" style={{ marginBottom: 15, textAlign: 'left', padding: '0 10px' }}>
            <label htmlFor="tempoSlider" style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#cbd5e0' }}>
              Tempo (BPM): <span>{tempo}</span>
            </label>
            <input
              id="tempoSlider"
              type="range"
              min={60}
              max={180}
              value={tempo}
              onChange={e => setTempo(Number(e.target.value))}
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
          <div className="slider-group" style={{ marginBottom: 15, textAlign: 'left', padding: '0 10px' }}>
            <label htmlFor="samplePitchSlider" style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#cbd5e0' }}>
              Sample Pitch Shift: <span>{pitch}</span> semitones
            </label>
            <input
              id="samplePitchSlider"
              type="range"
              min={-12}
              max={12}
              value={pitch}
              onChange={e => setPitch(Number(e.target.value))}
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
          <div className="slider-group" style={{ marginBottom: 15, textAlign: 'left', padding: '0 10px' }}>
            <label htmlFor="effectMixSlider" style={{ display: 'block', marginBottom: 5, fontWeight: 'bold', color: '#cbd5e0' }}>
              Effect Mix (Reverb): <span>{effectMix}</span>%
            </label>
            <input
              id="effectMixSlider"
              type="range"
              min={0}
              max={100}
              value={effectMix}
              onChange={e => setEffectMix(Number(e.target.value))}
              disabled={loading}
              style={{ width: '100%' }}
            />
          </div>
        </div>
        <div style={{ marginTop: 24, color: '#a0aec0', fontSize: '0.95rem' }}>
          <div>Backend status: {status}</div>
          {remixResult && (
            <div style={{ marginTop: 16, background: '#232b3b', padding: 16, borderRadius: 8 }}>
              <strong>Remix Result (backend response):</strong>
              <pre style={{ textAlign: 'left', color: '#e2e8f0', marginTop: 8 }}>
                {JSON.stringify(remixResult, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
