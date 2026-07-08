-- Создаем таблицу пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brightness INT CHECK (brightness >= 1 AND brightness <= 100) NOT NULL
);

-- Создаем таблицу логов переключений, связанную с пользователем
CREATE TABLE IF NOT EXISTS switch_logs (
    id SERIAL PRIMARY KEY,
    status SMALLINT NOT NULL, -- 1 для ON, 0 для OFF
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Теперь вставляем пользователя С РЕАЛЬНЫМ ХЭШЕМ пароля 'secret'
INSERT INTO users (username, password_hash) 
VALUES ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36XQrYQ6KnHjgfnJDjVWAGW')
ON CONFLICT (username) DO NOTHING;