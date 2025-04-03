-- Create table for stock data
CREATE TABLE IF NOT EXISTS stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    open_price FLOAT,
    high_price FLOAT,
    low_price FLOAT,
    close_price FLOAT,
    volume INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for financial reports
CREATE TABLE IF NOT EXISTS financial_reports (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(255) NOT NULL,
    report_type VARCHAR(50),
    report_date TIMESTAMP,
    title VARCHAR(255),
    content TEXT,
    content_hash VARCHAR(255) UNIQUE,
    url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for news articles
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    content TEXT,
    source VARCHAR(255),
    url VARCHAR(255) UNIQUE,
    content_hash VARCHAR(255) UNIQUE,
    published_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_analyzed BOOLEAN DEFAULT FALSE
);

-- Create table for analysis results
CREATE TABLE IF NOT EXISTS analysis_result (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(255) NOT NULL,
    news_analysis TEXT,
    financial_analysis TEXT,
    prediction TEXT,
    confidence_score VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
