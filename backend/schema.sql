-- Reference only. The FastAPI app creates these tables automatically on
-- startup via SQLAlchemy (see app/main.py). You do NOT need to run this
-- manually against Supabase - it's here so you can see the shape of the
-- data model without reading Python.

CREATE TABLE clients (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    primary_website VARCHAR,
    rss_feeds TEXT,
    alert_email VARCHAR,
    negative_spike_threshold FLOAT DEFAULT 0.4,
    created_at TIMESTAMPTZ,
    last_polled_at TIMESTAMPTZ
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    role VARCHAR NOT NULL, -- 'agency_admin' or 'client_user'
    client_id UUID REFERENCES clients(id),
    created_at TIMESTAMPTZ
);

CREATE TABLE keywords (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    term VARCHAR NOT NULL,
    is_competitor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ,
    UNIQUE (client_id, term)
);

CREATE TABLE mentions (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    keyword_id UUID REFERENCES keywords(id),
    source_type VARCHAR NOT NULL,
    source_name VARCHAR,
    title VARCHAR,
    excerpt TEXT,
    url VARCHAR NOT NULL,
    author VARCHAR,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ,
    sentiment_label VARCHAR,
    sentiment_score FLOAT,
    UNIQUE (client_id, url)
);

CREATE TABLE alert_log (
    id UUID PRIMARY KEY,
    client_id UUID REFERENCES clients(id),
    triggered_at TIMESTAMPTZ,
    reason VARCHAR NOT NULL,
    negative_ratio FLOAT,
    mention_count FLOAT,
    email_sent BOOLEAN DEFAULT FALSE
);
