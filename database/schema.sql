-- PostgreSQL. Waktu disimpan dalam UTC tanpa zona, sampai detik (dibaca frontend lewat parseScanDate)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP(0) DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    photo_path TEXT NOT NULL,
    scan_date TIMESTAMP(0) DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    conditions_detected TEXT NOT NULL,
    confidence_scores TEXT NOT NULL,
    recommendations TEXT NOT NULL,
    acne TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    price INTEGER NOT NULL,
    bpom_number TEXT NOT NULL,
    bpom_verified INTEGER DEFAULT 1,
    image_url TEXT,
    active_ingredients TEXT,
    created_at TIMESTAMP(0) DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE TABLE IF NOT EXISTS product_reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    reviewer_name TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT NOT NULL,
    review_date TIMESTAMP(0) DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS skincare_routines (
    id SERIAL PRIMARY KEY,
    condition_type TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    step_title TEXT NOT NULL,
    step_description TEXT NOT NULL
);
