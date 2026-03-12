CREATE DATABASE IF NOT EXISTS campus_events;
USE campus_events;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('admin', 'faculty', 'student') DEFAULT 'student',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS venues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    location VARCHAR(200),
    capacity INT NOT NULL,
    amenities TEXT,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type ENUM('academic','cultural','sports','seminar','workshop','other') DEFAULT 'other',
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    venue_id INT,
    organizer_id INT NOT NULL,
    status ENUM('pending','approved','rejected','cancelled') DEFAULT 'pending',
    max_attendees INT DEFAULT 100,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venue_id) REFERENCES venues(id) ON DELETE SET NULL,
    FOREIGN KEY (organizer_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    status ENUM('registered','waitlisted','cancelled') DEFAULT 'registered',
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_booking (event_id, user_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info','success','warning','danger') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Seed admin user (password: admin123)
INSERT IGNORE INTO users (name, email, password_hash, role, department) VALUES
('System Admin', 'admin@campus.edu', 'scrypt:32768:8:1$salt$hash', 'admin', 'Administration');

-- Seed venues
INSERT IGNORE INTO venues (name, location, capacity, amenities) VALUES
('Main Auditorium', 'Block A, Ground Floor', 500, 'Projector, Sound System, AC, Stage'),
('Seminar Hall 1', 'Block B, First Floor', 100, 'Projector, Whiteboard, AC'),
('Seminar Hall 2', 'Block B, Second Floor', 80, 'Projector, Whiteboard'),
('Sports Ground', 'Campus Ground', 1000, 'Open Ground, Floodlights'),
('Conference Room', 'Admin Block', 30, 'Projector, Video Conferencing, AC'),
('Computer Lab 1', 'Block C, Ground Floor', 60, '60 PCs, Projector, AC');