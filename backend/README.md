# Swatantra Backend

An advanced Agentic AI backend system built with FastAPI, LangChain, and Python. Supports both cloud (PostgreSQL/AWS) and offline (SQLite) modes.

## Features

- **Multi-Agent Orchestration** - Manage and coordinate multiple AI agents with LangChain
- **Autonomous Planning & Reasoning** - Agents can break down tasks and execute them independently
- **Tool Integration** - Extensible tool system for agents (web search, code execution, file operations, HTTP requests, etc.)
- **Dual Database Support** - PostgreSQL for cloud, SQLite for offline/local development
- **Offline-First Architecture** - Works offline with SQLite, syncs to PostgreSQL when online
- **RESTful API** - Complete API for agent and task management
- **Analytics & Monitoring** - Track agent performance and task execution history
- **Docker Support** - Easy containerization and cloud deployment

## Architecture

```
backend/
├── app/
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── routes/          # API route handlers
│   ├── agents/          # Agent orchestration & tools
│   ├── db/              # Database and sync managers
│   ├── utils/           # Helper utilities
│   ├── config.py        # Configuration management
│   └── main.py          # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container image
├── docker-compose.yml  # Local development stack
└── .env.example        # Environment variables template
```

## Technology Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI serving

### AI & Machine Learning
- **LangChain** - Framework for building agent applications
- **OpenAI API** - Cloud-based LLM (GPT-3.5-turbo, GPT-4)
- **Ollama** - Run open-source models locally (Mistral, Llama 2)

### Databases
- **PostgreSQL** - Production database for cloud deployment
- **SQLite** - Lightweight database for offline mode

### Cloud & DevOps
- **Docker** - Containerization
- **Docker Compose** - Local development orchestration
- **AWS** - Cloud deployment (EC2, RDS, Lambda ready)

## Installation & Setup

### 1. Clone and Setup

```bash
cd backend
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Choose database mode
DB_TYPE=sqlite              # or "postgresql"

# For offline mode (default)
USE_OFFLINE_LLM=False      # Set to True for Ollama
OLLAMA_BASE_URL=http://localhost:11434

# For online mode
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-3.5-turbo
```

### 3a. Local Development (SQLite + Ollama)

```bash
# Install dependencies
pip install -r requirements.txt

# Download Ollama (optional, for offline LLM)
# https://ollama.ai

# Start Ollama
ollama serve

# In another terminal, pull a model
ollama pull mistral

# Start backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3b. Docker Development Stack

```bash
# Start all services (PostgreSQL + Ollama + Backend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Migrate database (if needed)
docker-compose exec backend alembic upgrade head
```

### 3c. Cloud Deployment (PostgreSQL + AWS)

```bash
# Update .env for PostgreSQL
DB_TYPE=postgresql
POSTGRES_HOST=your-rds-endpoint.amazonaws.com
POSTGRES_PASSWORD=secure_password
OPENAI_API_KEY=your_api_key

# Build Docker image
docker build -t swatantra-backend .

# Push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker tag swatantra-backend:latest YOUR_ECR_URI/swatantra-backend:latest
docker push YOUR_ECR_URI/swatantra-backend:latest

# Deploy on AWS (ECS, EC2, or App Runner)
```

## API Documentation

### Access Interactive Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

#### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{agent_id}` - Get agent details
- `PUT /api/agents/{agent_id}` - Update agent
- `DELETE /api/agents/{agent_id}` - Delete agent
- `POST /api/agents/{agent_id}/activate` - Activate agent
- `POST /api/agents/{agent_id}/deactivate` - Deactivate agent

#### Tasks
- `GET /api/tasks` - List tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/{task_id}` - Get task
- `PUT /api/tasks/{task_id}` - Update task
- `POST /api/tasks/{task_id}/execute` - Execute task
- `POST /api/tasks/{task_id}/cancel` - Cancel task

#### Analytics
- `GET /api/analytics/summary` - Current metrics
- `GET /api/analytics/agents/performance` - Agent performance
- `GET /api/analytics/tasks/distribution` - Task status distribution
- `GET /api/analytics/history` - Historical data

#### System
- `GET /api/health` - Health check
- `GET /api/sync-status` - Offline sync status
- `POST /api/sync-now` - Manual sync (offline to cloud)

### Example: Create and Execute Task

```python
import requests

# Create agent
agent_resp = requests.post("http://localhost:8000/api/agents", json={
    "name": "DocumentAnalyzer",
    "description": "Analyzes documents",
    "agent_type": "reasoning",
    "tools": ["document_processor", "web_search"]
})
agent_id = agent_resp.json()["id"]

# Create task
task_resp = requests.post("http://localhost:8000/api/tasks", json={
    "agent_id": agent_id,
    "title": "Analyze PDF Report",
    "objective": "Summarize this report and extract key metrics",
    "input_data": {
        "url": "https://example.com/report.pdf"
    }
})
task_id = task_resp.json()["id"]

# Execute task
exec_resp = requests.post(f"http://localhost:8000/api/tasks/{task_id}/execute")
print(exec_resp.json())
```

## Modes of Operation

### 1. Offline Mode (SQLite + Ollama)
- Uses SQLite for local database
- Runs Ollama for local LLM (Mistral, Llama 2)
- Perfect for development and edge deployment
- Syncs to cloud when online

```bash
DB_TYPE=sqlite
USE_OFFLINE_LLM=True
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Online Mode (PostgreSQL + OpenAI)
- Uses PostgreSQL for cloud database
- Integrates with OpenAI API
- Suitable for production deployment
- Better for scalability and concurrent users

```bash
DB_TYPE=postgresql
POSTGRES_HOST=your-rds-endpoint
OPENAI_API_KEY=your_key
```

### 3. Hybrid Mode
- Starts with local SQLite + Ollama
- Automatically syncs to PostgreSQL + OpenAI when online
- Best of both worlds for reliability

## Offline Sync System

The backend includes an intelligent offline-first sync system:

1. **Local Queue** - Changes saved locally in sync_queue.db
2. **Background Sync** - Automatically syncs when connection available
3. **Manual Sync** - `POST /api/sync-now` to trigger sync
4. **Sync Status** - `GET /api/sync-status` to check pending

```bash
# Check sync status
curl http://localhost:8000/api/sync-status

# Trigger manual sync
curl -X POST http://localhost:8000/api/sync-now
```

## Available Tools for Agents

Pre-built tools agents can use:

- **web_search** - Search internet for information
- **execute_code** - Run Python code snippets
- **read_file** - Read file contents
- **write_file** - Write to files
- **get_time** - Get current timestamp
- **http_request** - Make HTTP API calls
- **analyze_data** - Analyze JSON, CSV, text
- **document_processor** - Summarize and analyze documents

### Extending Tools

Add custom tools in `app/agents/tools.py`:

```python
def my_custom_tool(param: str) -> str:
    """Custom tool description"""
    return "result"

custom_tool = Tool(
    name="my_tool",
    func=my_custom_tool,
    description="What this tool does"
)
```

## Database Schema

### Core Tables

- **agents** - AI agent definitions and state
- **tasks** - Task definitions and execution results
- **agent_executions** - Execution history and reasoning steps
- **task_executions** - Individual step execution details
- **analytics_snapshots** - Historical metrics

## Configuration

See `.env.example` for all configuration options:

```
DB_TYPE               # sqlite or postgresql
POSTGRES_*            # PostgreSQL connection
SQLITE_DB_PATH       # SQLite file location
OPENAI_API_KEY       # OpenAI API key
LLM_MODEL            # Model name (gpt-3.5-turbo, gpt-4)
USE_OFFLINE_LLM      # True to use Ollama
OLLAMA_BASE_URL      # Ollama server URL
```

## Monitoring & Debugging

### Enable Debug Mode

```bash
DEBUG=True
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Local
# Logs appear in terminal
```

### Health Check

```bash
curl http://localhost:8000/api/health
```

## Deployment to AWS

### Architecture
```
Frontend (S3/CloudFront)
    ↓
API Gateway → ALB
    ↓
ECS Fargate (Backend)
    ↓
RDS PostgreSQL
```

### Steps
1. Create RDS PostgreSQL instance
2. Push Docker image to ECR
3. Create ECS Fargate task definition
4. Configure ALB and security groups
5. Deploy via CloudFormation or Terraform

See [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for detailed guide.

## Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black app/
isort app/
```

### Type Checking

```bash
mypy app/
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running: `psql -U postgres -d swatantra`
- Or use SQLite: `DB_TYPE=sqlite`

### LLM Not Responding
- Ensure OpenAI API key is set or Ollama is running
- Check: `curl http://localhost:11434/api/tags`

### Port Already in Use
```bash
# Change port in .env or command
uvicorn app.main:app --port 8001
```

## Contributing

1. Create feature branch
2. Make changes following code style
3. Test locally with Docker Compose
4. Submit PR

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- GitHub Issues: [Swatantra Issues]
- Email: support@swatantra.dev
- Documentation: https://docs.swatantra.dev
