# Agentic Portfolio Chat Widget

A production-grade, multi-tenant chat widget system powered by LangGraph, FastAPI, and React. Built for customer service and lead generation with GoHighLevel CRM integration.

## Features

- **LangGraph Agents**: Conversational AI with RunnableWithMessageHistory
- **Multi-Tenant**: Complete isolation at database and session levels
- **Memory Modes**: Toggle between thread-based and persistent (pgvector) memory
- **Lead Capture**: Automatic lead creation with optional GoHighLevel push
- **Admin Builder**: Configure agent identity, mission, and behavior per tenant
- **Real-time Chat**: Session-based conversations with continuity
- **Azure Ready**: Configured for Azure PostgreSQL and Redis Cache
- **Production Ready**: Docker-based infrastructure with health checks

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key

### Docker Setup (Recommended)

1. Clone and enter the project:
```bash
cd agentic-widget
```

2. Set up environment variables:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your OpenAI API key and other settings
```

3. Start all services:
```bash
docker compose up -d
```

4. The system will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health

### Local Development (Alternative)

#### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set environment variables
$env:OPENAI_API_KEY="sk-your-key-here"
$env:DATABASE_URL="postgresql://agent:agentpw@localhost:5432/agentic"
$env:REDIS_URL="redis://localhost:6379/0"

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Backend Structure
- **FastAPI**: REST API with automatic documentation
- **LangGraph**: Workflow orchestration for agent conversations
- **asyncpg**: Direct PostgreSQL connections with connection pooling
- **Redis**: Session storage and caching
- **Multi-tenant**: Complete data isolation per tenant

### Frontend Structure
- **React + TypeScript**: Modern UI with type safety
- **Tailwind CSS**: Utility-first styling
- **Chat Widget**: Floating launcher with slide-out panel
- **Admin Builder**: Agent configuration interface

### Key Workflows

1. **Agent Configuration**: Admin Builder → File Storage + Database
2. **Chat Processing**: User Input → LangGraph → Response + CRM Notes
3. **Lead Capture**: Form Data → Database → Optional GHL Push
4. **Memory Management**: Thread-based (default) or Persistent (pgvector)

## API Endpoints

### Admin
- `POST /api/v1/admin/agent` - Create/update agent configuration
- `GET /api/v1/admin/agent/{tenant_id}/{agent_name}` - Get agent config

### Chat
- `POST /api/v1/chat` - Process chat message

### Leads
- `POST /api/v1/leads` - Create/update lead with optional GHL push
- `GET /api/v1/leads/{tenant_id}` - Get all leads for tenant

## Azure Configuration

### PostgreSQL (Azure Database for PostgreSQL)
```env
AZURE_POSTGRES_HOST=your-server.postgres.database.azure.com
AZURE_POSTGRES_USER=agent@your-server
AZURE_POSTGRES_PASSWORD=your-password
AZURE_POSTGRES_DB=agentic
```

### Redis (Azure Cache for Redis)
```env
AZURE_REDIS_HOST=your-cache.redis.cache.windows.net
AZURE_REDIS_PASSWORD=your-access-key
```

## Configuration

### Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
TEMPERATURE=0.4
MAX_TOKENS=1024

# Database
DATABASE_URL=postgresql://agent:agentpw@localhost:5432/agentic
REDIS_URL=redis://localhost:6379/0

# GoHighLevel Integration
GHL_API_BASE=https://rest.gohighlevel.com/v1
GHL_API_KEY=your-ghl-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Agent Configuration

Each agent has:
- **Identity**: Brand, tone, capabilities, personality
- **Mission**: Goals, guidelines, compliance rules
- **System Prompt**: Detailed behavior instructions
- **Memory Mode**: Thread or persistent storage

## Smoke Tests

```powershell
# Health check
curl http://localhost:8000/health

# Create agent
$tenant = "00000000-0000-0000-0000-000000000001"
curl -X POST http://localhost:8000/api/v1/admin/agent `
  -H "Content-Type: application/json" `
  -d "{`"tenant_id`":`"$tenant`",`"name`":`"Elena`",`"system_prompt`":`"You are a helpful assistant.`",`"identity`":{`"brand`":`"Portfolio Pro`"},`"mission`":{`"mission`":`"Help visitors`"},`"memory_mode`":`"thread`"}"

# Test chat
$session = [guid]::NewGuid().ToString()
curl -X POST http://localhost:8000/api/v1/chat `
  -H "Content-Type: application/json" `
  -d "{`"tenant_id`":`"$tenant`",`"agent_name`":`"Elena`",`"session_id`":`"$session`",`"user_input`":`"Hello, I'm interested in your services.`"}"

# Create lead
curl -X POST http://localhost:8000/api/v1/leads `
  -H "Content-Type: application/json" `
  -d "{`"tenant_id`":`"$tenant`",`"first_name`":`"John`",`"email`":`"john@example.com`",`"notes`":`"Interested in pricing`",`"push_to_ghl`":false}"
```

## Security

- **Multi-tenant isolation**: All data scoped by tenant_id
- **Session management**: Unique session keys per tenant:agent:session
- **Environment-based secrets**: API keys via environment variables
- **Input validation**: Pydantic models with length limits
- **Error handling**: Graceful degradation with user-friendly messages

## Extending

### Adding Persistent Memory
1. Implement embedding generation in `agents/memory.py`
2. Add vector similarity search using pgvector
3. Update the `n_prepare` node to retrieve relevant context

### GoHighLevel Integration
1. Configure GHL_API_KEY in environment
2. Customize lead mapping in `repo.py`
3. Add pipeline assignments and tags as needed

### Custom Agents
1. Use Admin Builder to configure new agents
2. Customize system prompts for specific use cases
3. Adjust identity and mission for brand alignment

## License

MIT License - see LICENSE file for details.