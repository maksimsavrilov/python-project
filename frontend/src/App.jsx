import React, { useState } from 'react';

function App() {
  const [token, setToken] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [isOn, setIsOn] = useState(false);
  const [loading, setLoading] = useState(false);

  // Используем адрес бэкенда из переменных окружения Vite (или локальный фолбэк)
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

  // 1. ФУНКЦИЯ АВТОРИЗАЦИИ (ВХОДА)
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    // OAuth2PasswordRequestForm на бэкенде ждет данные в формате x-www-form-urlencoded
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
        setToken(data.access_token); // Сохраняем токен!
      } else {
        alert('Ошибка входа: ' + (data.detail || 'Неверные данные'));
      }
    } catch (error) {
      alert('Ошибка сети при авторизации');
    } finally {
      setLoading(false);
    }
  };

  // 2. ФУНКЦИЯ ПЕРЕКЛЮЧЕНИЯ ЛАМПОЧКИ (ЗАЩИЩЕННАЯ)
  const handleToggle = async () => {
    const nextState = !isOn;
    setIsOn(nextState);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/device/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // ПЕРЕДАЕМ ТОКЕН В ЗАГОЛОВКЕ!
          'Authorization': `Bearer ${token}`, 
        },
        body: JSON.stringify({ status: nextState }),
      });

      const data = await response.json();
      if (!response.ok) {
        alert('Ошибка бэкенда: ' + (data.detail || 'Нет доступа'));
        if (response.status === 401) setToken(''); // Если токен протух, сбрасываем авторизацию
      }
    } catch (error) {
      alert('Ошибка сети при отправке команды');
    } finally {
      setLoading(false);
    }
  };

  // --- ИНТЕРФЕЙС ЭКРАНА ВХОДА ---
  if (!token) {
    return (
      <div style={{ textAlign: 'center', marginTop: '100px', fontFamily: 'sans-serif' }}>
        <h2>Вход в Умный Дом</h2>
        <form onSubmit={handleLogin} style={{ display: 'inline-block', textAlign: 'left', gap: '10px' }}>
          <div>
            <label>Логин: </label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div style={{ marginTop: '10px' }}>
            <label>Пароль: </label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" disabled={loading} style={{ marginTop: '15px', width: '100%' }}>
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    );
  }

  // --- ИНТЕРФЕЙС УПРАВЛЕНИЯ ЛАМПОЧКОЙ ---
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
      <h2>Панель управления ({username})</h2>
      <div style={switchStyles} onClick={loading ? null : handleToggle}>
        <div style={circleStyles} />
      </div>
      <p style={{ marginTop: '20px' }}>
        Лампочка: <strong>{isOn ? 'ВКЛ' : 'ВЫКЛ'}</strong>
      </p>
      {loading && <span style={{ color: 'gray' }}>Связь с сервером...</span>}
      <br />
      <button onClick={() => setToken('')} style={{ marginTop: '30px' }}>Выйти из аккаунта</button>
    </div>
  );
}

export default App;
