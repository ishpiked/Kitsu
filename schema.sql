-- Neon PostgreSQL Schema for AniList Telegram Bot
-- Run this in Neon SQL Editor or via psql
-- Database: anilist_bot

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    telegram_username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    anilist_user_id BIGINT UNIQUE,
    anilist_access_token_encrypted TEXT,
    anilist_token_expires_at TIMESTAMPTZ,
    anilist_token_refresh_token_encrypted TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexes for users
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_anilist_user_id ON users(anilist_user_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Anime/Manga library entries (user's AniList library)
CREATE TABLE IF NOT EXISTS library_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    anilist_media_id BIGINT NOT NULL,
    media_type VARCHAR(20) NOT NULL CHECK (media_type IN ('ANIME', 'MANGA')),
    status VARCHAR(50) NOT NULL CHECK (status IN ('CURRENT', 'PLANNING', 'COMPLETED', 'DROPPED', 'PAUSED', 'REPEATING')),
    progress INTEGER NOT NULL DEFAULT 0,
    progress_volumes INTEGER NOT NULL DEFAULT 0,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    priority INTEGER,
    repeat_count INTEGER NOT NULL DEFAULT 0,
    started_at DATE,
    completed_at DATE,
    notes TEXT,
    custom_lists JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, anilist_media_id, media_type)
);

-- Indexes for library_entries
CREATE INDEX IF NOT EXISTS idx_library_entries_user_id ON library_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_library_entries_media_id ON library_entries(anilist_media_id);
CREATE INDEX IF NOT EXISTS idx_library_entries_status ON library_entries(status);
CREATE INDEX IF NOT EXISTS idx_library_entries_media_type ON library_entries(media_type);
CREATE INDEX IF NOT EXISTS idx_library_entries_user_status ON library_entries(user_id, status);

-- Favorites (user's favorite anime/manga/characters/staff)
CREATE TABLE IF NOT EXISTS favorites (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    anilist_id BIGINT NOT NULL,
    favorite_type VARCHAR(20) NOT NULL CHECK (favorite_type IN ('ANIME', 'MANGA', 'CHARACTER', 'STAFF', 'STUDIO')),
    order_rank INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, anilist_id, favorite_type)
);

-- Indexes for favorites
CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_favorites_type ON favorites(favorite_type);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN ('AIRING', 'CHAPTER_RELEASE', 'NEWS', 'ACTIVITY', 'RECOMMENDATION')),
    media_id BIGINT,
    title VARCHAR(500) NOT NULL,
    message TEXT NOT NULL,
    url VARCHAR(1000),
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_sent BOOLEAN NOT NULL DEFAULT FALSE,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_notifications_unsent ON notifications(is_sent) WHERE is_sent = FALSE;

-- User activities (for activity feed)
CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('LIST_UPDATE', 'RATING', 'PROGRESS', 'FAVORITE', 'REVIEW', 'RECOMMENDATION')),
    media_id BIGINT,
    media_type VARCHAR(20) CHECK (media_type IN ('ANIME', 'MANGA')),
    progress INTEGER,
    score INTEGER,
    status VARCHAR(50),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for activities
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_media ON activities(media_id, media_type);

-- Search history
CREATE TABLE IF NOT EXISTS search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    media_type VARCHAR(20) CHECK (media_type IN ('ANIME', 'MANGA', 'CHARACTER', 'STAFF', 'STUDIO')),
    results_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for search_history
CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at DESC);

-- Update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_library_entries_updated_at BEFORE UPDATE ON library_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (optional, for multi-tenant safety)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE library_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
CREATE POLICY users_own_data ON users
    FOR ALL USING (telegram_id = current_setting('app.current_telegram_id')::BIGINT);

CREATE POLICY library_entries_own_data ON library_entries
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_setting('app.current_telegram_id')::BIGINT));

CREATE POLICY favorites_own_data ON favorites
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_setting('app.current_telegram_id')::BIGINT));

CREATE POLICY notifications_own_data ON notifications
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_setting('app.current_telegram_id')::BIGINT));

CREATE POLICY activities_own_data ON activities
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_setting('app.current_telegram_id')::BIGINT));

CREATE POLICY search_history_own_data ON search_history
    FOR ALL USING (user_id IN (SELECT id FROM users WHERE telegram_id = current_setting('app.current_telegram_id')::BIGINT));

-- Function to set current user context for RLS
CREATE OR REPLACE FUNCTION set_current_user(telegram_id BIGINT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_telegram_id', telegram_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT EXECUTE ON FUNCTION set_current_user(BIGINT) TO anon, authenticated;