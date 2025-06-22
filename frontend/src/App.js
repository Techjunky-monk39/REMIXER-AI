import React, { useEffect, useState } from 'react';

function App() {
  const [status, setStatus] = useState('');

  useEffect(() => {
    fetch(`${process.env.REACT_APP_API_URL}/`)
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('Backend not reachable'));
  }, []);

  return (
    <div>
      <h1>Remixer Frontend</h1>
      <p>Connects to Flask backend via Docker network.</p>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;
