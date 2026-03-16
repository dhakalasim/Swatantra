# Swatantra AI Frontend

A modern React + Next.js + TypeScript dashboard for managing AI agents and tasks in the Swatantra Agentic AI system.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Font Awesome

## Features

- 🤖 **Agent Management**: Create, activate, and monitor AI agents
- 📋 **Task Management**: Queue, execute, and track task execution
- 📊 **Analytics Dashboard**: Monitor system performance and metrics
- 🌙 **Dark Mode**: Modern dark theme optimized for long usage
- 🇳🇵 **Nepali Language**: Full UI in Nepali language
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- ⚡ **Real-time Updates**: Auto-refresh agent and task status
- 🔌 **API Integration**: Full integration with Swatantra backend API

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── globals.css         # Global styles
│   ├── page.tsx            # Dashboard page
│   ├── agents/page.tsx     # Agents management
│   ├── tasks/page.tsx      # Tasks management
│   ├── analytics/page.tsx  # Analytics dashboard
│   └── settings/page.tsx   # Settings page
├── components/
│   ├── Layout.tsx          # Main layout wrapper
│   ├── Sidebar.tsx         # Navigation sidebar
│   ├── AgentCard.tsx       # Agent card component
│   └── TaskCard.tsx        # Task card component
├── lib/
│   └── apiClient.ts        # API client with axios
├── types/
│   └── index.ts            # TypeScript type definitions
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── postcss.config.js
```

## Installation

### Prerequisites
- Node.js 18+
- npm or yarn

### Steps

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file (copy from .env.example):
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

Build the application:
```bash
npm run build
```

Start the production server:
```bash
npm start
```

## Type Checking

Run TypeScript type checking:
```bash
npm run type-check
```

## API Integration

The frontend connects to the Swatantra backend API running on `http://localhost:8000`.

### Available API Endpoints

- `GET /api/health` - System health status
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `POST /api/tasks/{id}/execute` - Execute task
- `GET /api/analytics/summary` - Get analytics summary

For more details, see the [Backend API Documentation](../backend/README.md).

## Environment Variables

- `NEXT_PUBLIC_API_BASE_URL` - Backend API base URL (default: http://localhost:8000)

## Features Roadmap

- [ ] Advanced agent configuration UI
- [ ] Task scheduling and automation
- [ ] Real-time logs streaming
- [ ] Export reports in PDF/Excel
- [ ] Multi-user support with authentication
- [ ] Agent performance comparison graphs
- [ ] Custom workflow builder

## Troubleshooting

### API Connection Issues
If you get CORS or connection errors:
1. Verify backend is running on `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_BASE_URL` in `.env.local`
3. Ensure `CORS` is enabled in backend

### Build Issues
If you encounter build errors:
1. Clear `.next` folder: `rm -rf .next`
2. Clear node_modules: `rm -rf node_modules`
3. Reinstall: `npm install`
4. Rebuild: `npm run build`

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions, please create an issue in the repository.
