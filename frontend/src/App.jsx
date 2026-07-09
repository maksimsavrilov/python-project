import React, { useState } from 'react';

function App() {
  const [token, setToken] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [isOn, setIsOn] = useState(false);
  const [loading, setLoading] = useState(false);

  const [logs, setLogs] = useState([]);

  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';


  const fetchLogs = async (currentToken) => {
    try {
      const response = await fetch(`${API_URL}/api/device/logs`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${currentToken || token}` },
      });
      const data = await response.json();
      if (response.ok) {
        setLogs(data);
        if (data.length > 0) {
          setIsOn(data[0].status === 1);
        }
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        setToken(data.access_token);
        fetchLogs(data.access_token);
      } else {
        alert('Ошибка входа: ' + (data.detail || 'Wrong data'));
      }
    } catch (error) {
      console.error('Failed to login:', error);
      alert('Network error during login, please check the console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async () => {
    const nextState = !isOn;
    setIsOn(nextState);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/device/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ status: nextState }),
      });

      const data = await response.json();
      if (!response.ok) {
        alert('Ошибка бэкенда: ' + (data.detail || 'Нет доступа'));
        if (response.status === 401) setToken(''); // reset auth if unauthorized
      } else {
        fetchLogs(); // Update logs after successful toggle
      }
    } catch (error) {
      console.error('Failed to toggle device:', error);
      alert('Network error during toggle, please check the console for details.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
        <h2>Smart Home learning project</h2>
        <form onSubmit={handleLogin} style={{ display: 'inline-block', textAlign: 'left', gap: '10px' }}>
          <div>
            <label>Login: </label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div style={{ marginTop: '10px' }}>
            <label>Password: </label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" disabled={loading} style={{ marginTop: '15px', width: '100%' }}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    );
  }

  const switchStyles = {
    display: 'inline-block', width: '60px', height: '34px', position: 'relative',
    backgroundColor: isOn ? '#4caf50' : '#ccc', borderRadius: '34px',
    cursor: loading ? 'not-allowed' : 'pointer', transition: '0.4s',
  };

  const circleStyles = {
    position: 'absolute', height: '26px', width: '26px',
    left: isOn ? '30px' : '4px', bottom: '4px',
    backgroundColor: 'white', borderRadius: '50%', transition: '0.4s',
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'sans-serif' }}>
      <h2>Control Panel ({username})</h2>
      <div style={switchStyles} onClick={loading ? null : handleToggle}>
        <div style={circleStyles} />
      </div>
      <p style={{ marginTop: '20px' }}>
        Light: <strong>{isOn ? 'ON' : 'OFF'}</strong>
      </p>
      {loading && <span style={{ color: 'gray' }}>Connecting to server...</span>}

      <div style={{ marginTop: '40px', maxWidth: '450px', display: 'inline-block', textAlign: 'left' }}>
        <h3>Switching History:</h3>
        {logs.length === 0 ? (
          <p style={{ color: 'gray' }}>History is currently empty...</p>
        ) : (
          <ul style={{ paddingLeft: '20px' }}>
            {logs.map((log) => {
              const utcDate = new Date(log.changed_at);

              const localTime = utcDate.toLocaleString('en-EN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              });

              const timeZoneName = Intl.DateTimeFormat().resolvedOptions().timeZone;

              return (
                <li key={log.id} style={{ marginBottom: '5px' }}>
                  [{localTime}] ({timeZoneName}) User {log.username} changed status to:{' '}
                  <strong>{log.status === 1 ? 'ON' : 'OFF'}</strong>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <br />
      <button onClick={() => setToken('')} style={{ marginTop: '30px' }}>Logout</button>
    </div>
  );
}

export default App;
