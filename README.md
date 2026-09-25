# AniList Telegram Bot

A production-quality Telegram bot that integrates deeply with AniList for anime/manga library management.

## Tech Stack

- Python 3.12+
- python-telegram-bot 22+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- httpx
- Pydantic v2
- pydantic-settings
- Redis
- uvicorn
- asyncio

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── server.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── application.py
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   ├── callbacks/
│   │   ├── middlewares/
│   │   └── utils/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   ├── anilist/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── queries.py
│   │   ├── mutations.py
│   │   └── models.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repositories/
│   ├── services/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── constants.py
├── migrations/
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── run.py
```

## Setup Instructions

### 1. Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 2. PostgreSQL

Install PostgreSQL 15+ and create a database:

```sql
CREATE DATABASE anilist_bot;
CREATE USER bot_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE anilist_bot TO bot_user;
```

### 3. Redis

Install Redis 7+ and ensure it's running on localhost:6379 (default).

### 4. Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- `BOT_TOKEN` - Get from @BotFather
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ANILIST_CLIENT_ID` - From AniList developer settings
- `ANILIST_CLIENT_SECRET` - From AniList developer settings
- `ANILIST_REDIRECT_URI` - OAuth callback URL
- `WEBHOOK_URL` - Production webhook URL (optional for development)
- `ENVIRONMENT` - `development` or `production`
- `LOG_LEVEL` - `DEBUG`, `INFO`, `WARNING`, `ERROR`

### 5. Alembic Migration

Initialize the database schema:

```bash
alembic upgrade head
```

### 6. Starting the Bot

#### Development (Polling Mode)

```bash
python run.py
```

#### Production (Webhook Mode)

```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

The webhook endpoint will be available at `POST /webhook`.

### 7. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### 8. Testing

```bash
pytest tests/ -v
```

## Current Features (STEP 1)

- ✅ Project structure and configuration
- ✅ PostgreSQL + SQLAlchemy 2.x + Alembic setup
- ✅ User model with Telegram profile sync
- ✅ AniList client abstraction (skeleton)
- ✅ Telegram bot with polling and webhook support
- ✅ `/start` command with user creation/update
- ✅ Keyboard system with colored buttons (primary/success/danger/neutral)
- ✅ Structured callback data architecture
- ✅ Centralized error handling
- ✅ Structured logging
- ✅ Health endpoint
- ✅ Basic tests
- ✅ Vercel deployment ready
- ✅ No __pycache__ generation

## Vercel Deployment (Neon + Upstash)

### 1. Prerequisites
- Vercel account
- **Neon PostgreSQL** (serverless, branchable, autoscaling)
- **Upstash Redis** (HTTP-based, serverless, no persistent connections)
- Telegram Bot Token from @BotFather
- AniList OAuth credentials

### 2. Setup Neon Database

1. Create a Neon project at https://neon.tech
2. Copy the connection string (Pooled connection for serverless):
   ```
   postgresql+asyncpg://user:password@ep-xxx.us-east-1.aws.neon.tech/anilist_bot?sslmode=require
   ```
3. Run the schema in Neon SQL Editor:
   ```bash
   # In Neon Console -> SQL Editor, paste contents of schema.sql
   ```

### 3. Setup Upstash Redis

1. Create an Upstash Redis database at https://upstash.com
2. Choose **HTTP/REST** API (not TCP) for serverless
3. Copy credentials:
   ```
   UPSTASH_REDIS_REST_URL=https://us1-bird-12345.upstash.io
   UPSTASH_REDIS_REST_TOKEN=your_token_here
   ```

### 4. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### 5. Configure Environment Variables in Vercel Dashboard

Go to your Vercel project settings and add these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | `123456:ABC-DEF...` |
| `DATABASE_URL` | Neon pooled connection string | `postgresql+asyncpg://user:pass@ep-xxx.neon.tech/db?sslmode=require` |
| `REDIS_URL` | Upstash Redis (TCP, optional) | `redis://default:pass@us1-bird.upstash.io:6379` |
| `UPSTASH_REDIS_REST_URL` | Upstash REST URL (preferred for serverless) | `https://us1-bird.upstash.io` |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash REST token | `your_token_here` |
| `ANILIST_CLIENT_ID` | AniList OAuth Client ID | `12345` |
| `ANILIST_CLIENT_SECRET` | AniList OAuth Client Secret | `abcdef...` |
| `ANILIST_REDIRECT_URI` | OAuth callback URL | `https://your-app.vercel.app/api/auth/anilist/callback` |
| `WEBHOOK_URL` | Your Vercel deployment URL | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `production` | `production` |
| `LOG_LEVEL` | `INFO` | `INFO` |
| `PYTHONDONTWRITEBYTECODE` | `1` | `1` |

### 6. Set Telegram Webhook

After deployment, set the webhook:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-app.vercel.app/api/webhook"}'
```

Or visit: `https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-app.vercel.app/api/webhook`

### 7. Verify Deployment

```bash
curl https://your-app.vercel.app/api/health
# Should return: {"status": "ok"}
```

### Database Schema

The complete schema is in `schema.sql`. It includes:

- **users** - Telegram users with AniList OAuth tokens (encrypted)
- **library_entries** - User's anime/manga library with status, progress, scores
- **favorites** - User's favorite anime/manga/characters/staff
- **notifications** - Airing alerts, chapter releases, activity notifications
- **activities** - User activity feed (list updates, ratings, progress)
- **search_history** - User search queries for autocomplete/suggestions
- **RLS policies** - Row-level security for multi-user isolation
- **Triggers** - Auto-update `updated_at` timestamps

## Next Steps

Future steps will add:
- AniList OAuth integration
- Anime/Manga search
- Library management
- Progress tracking
- Notifications
- Recommendations

## License

MIT License - see [LICENSE](LICENSE) for details.