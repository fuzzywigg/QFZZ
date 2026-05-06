# QFZZ: Getting Started Guide

## Welcome to QFZZ Development

This guide will help you understand the QFZZ project, set up your development environment, and start contributing to "The Pulse of the Quantum Realm - AI radio for the individual."

## Project Overview

QFZZ is an AI-powered personalized radio platform that combines:
- Intelligent music/audio recommendations
- AI-generated content (DJ commentary, news, etc.)
- Knowledge graph integration for deep content relationships
- Quantum-inspired discovery mechanisms
- Privacy-first, open-source architecture

## Current Status

**Stage**: Research & Planning Phase
**Repository**: Initial setup with documentation
**Next Steps**: Begin MVP implementation

## Prerequisites

### Required Knowledge
- JavaScript/TypeScript (intermediate to advanced)
- React and Next.js
- Node.js and Express/Fastify
- REST APIs and/or GraphQL
- SQL databases (PostgreSQL)
- Git and GitHub workflows

### Recommended Knowledge
- Docker and containerization
- Redis and caching strategies
- Machine Learning basics
- Audio processing (Web Audio API)
- Graph databases (Neo4j)
- Cloud platforms (AWS, GCP, or Azure)

## Reading List

Before diving in, please review these documents:

1. **[README.md](./README.md)** - Project introduction
2. **[RESEARCH_GAPS_ANALYSIS.md](./RESEARCH_GAPS_ANALYSIS.md)** - Comprehensive analysis of gaps and opportunities
3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design
4. **[FEATURE_ROADMAP.md](./FEATURE_ROADMAP.md)** - Feature prioritization and timeline

## Quick Setup Guides

**Windows Users**: See **[WINDOWS_SETUP.md](./WINDOWS_SETUP.md)** for complete PowerShell instructions and GUI setup.

**Quick Reference**: See **[docs/QUICK_START_WINDOWS.md](./docs/QUICK_START_WINDOWS.md)** for a condensed cheat sheet.

## Development Setup (MVP Phase)

Once implementation begins, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/fuzzywigg/QFZZ.git
cd QFZZ
```

### 2. Install Dependencies

```bash
# Frontend (Next.js)
cd frontend
npm install

# Backend (Node.js)
cd ../backend
npm install
```

### 3. Set Up Environment Variables

QFZZ uses environment variables for configuration. Start by copying the example file:

```bash
cp .env.example .env
```

Then edit `.env` with your actual API keys and configuration. See [Configuration](#configuration) in README.md for details on obtaining API keys.

**Minimum Configuration** (for basic functionality):
- `GOOGLE_AI_API_KEY` - Primary LLM provider

**Recommended Configuration** (with fallback):
- `GOOGLE_AI_API_KEY` - Primary provider
- `GROQ_API_KEY` - Free tier fallback

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

**Backend (.env):**
```env
PORT=3001
DATABASE_URL=postgresql://user:password@localhost:5432/qfzz
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-jwt-secret
OPENAI_API_KEY=your-openai-key (for AI features)
```

### 4. Set Up Database

```bash
# Start PostgreSQL with Docker
docker run --name qfzz-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=qfzz -p 5432:5432 -d postgres:16

# Run migrations
cd backend
npm run migrate
```

### 5. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
npm run dev

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis
docker run --name qfzz-redis -p 6379:6379 -d redis:7
```

### 6. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:3001
- **API Docs**: http://localhost:3001/api-docs (Swagger)

## Project Structure

```
QFZZ/
├── README.md
├── ARCHITECTURE.md
├── FEATURE_ROADMAP.md
├── RESEARCH_GAPS_ANALYSIS.md
├── GETTING_STARTED.md (this file)
│
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # Next.js 14 App Router
│   │   ├── components/      # React components
│   │   ├── lib/             # Utilities and helpers
│   │   ├── hooks/           # Custom React hooks
│   │   └── types/           # TypeScript type definitions
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                 # Node.js API
│   ├── src/
│   │   ├── routes/          # API routes
│   │   ├── controllers/     # Request handlers
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Express middleware
│   │   └── utils/           # Utilities
│   ├── migrations/          # Database migrations
│   └── package.json
│
├── ml-service/              # Python ML/AI service
│   ├── src/
│   │   ├── recommendations/ # Recommendation engine
│   │   ├── content_gen/     # Content generation
│   │   └── models/          # ML models
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker/                  # Docker configurations
│   ├── docker-compose.yml
│   └── Dockerfile.*
│
├── docs/                    # Additional documentation
│   ├── api/                 # API documentation
│   ├── design/              # Design documents
│   └── guides/              # User guides
│
└── scripts/                 # Utility scripts
    ├── seed-data.js         # Database seeding
    └── setup-dev.sh         # Development setup
```

## Development Workflow

### 1. Pick an Issue or Feature

- Check [GitHub Issues](https://github.com/fuzzywigg/QFZZ/issues)
- Review [FEATURE_ROADMAP.md](./FEATURE_ROADMAP.md) for upcoming features
- Join discussions in GitHub Discussions

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Develop and Test

- Write code following our style guide (ESLint + Prettier configured)
- Write tests for new functionality
- Run tests locally: `npm test`
- Test manually in the browser

### 4. Commit Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add user preference survey"
git commit -m "fix: resolve audio playback issue on Safari"
git commit -m "docs: update API documentation"
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issue
- Screenshots (for UI changes)
- Test results

## Coding Standards

### TypeScript

```typescript
// Use explicit types
interface User {
  id: string;
  username: string;
  email: string;
  createdAt: Date;
}

// Use async/await over promises
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// Use functional components with hooks
export function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);

  return <div>{user?.username}</div>;
}
```

### API Design

```typescript
// RESTful routes
GET    /api/tracks              // List tracks
GET    /api/tracks/:id          // Get single track
POST   /api/tracks              // Create track
PUT    /api/tracks/:id          // Update track
DELETE /api/tracks/:id          // Delete track

// Use proper status codes
200 OK
201 Created
400 Bad Request
401 Unauthorized
404 Not Found
500 Internal Server Error
```

### Database Queries

```typescript
// Use parameterized queries (SQL injection prevention)
const result = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [userId]
);

// Use transactions for multiple operations
await db.transaction(async (trx) => {
  await trx('users').insert(user);
  await trx('profiles').insert(profile);
});
```

## Testing Strategy

### Unit Tests

```typescript
// Jest + React Testing Library
import { render, screen } from '@testing-library/react';
import { AudioPlayer } from './AudioPlayer';

test('renders play button', () => {
  render(<AudioPlayer trackId="123" />);
  expect(screen.getByRole('button', { name: /play/i })).toBeInTheDocument();
});
```

### Integration Tests

```typescript
// Test API endpoints
describe('GET /api/tracks', () => {
  it('returns list of tracks', async () => {
    const response = await request(app).get('/api/tracks');
    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('tracks');
  });
});
```

### E2E Tests

```typescript
// Playwright or Cypress
test('user can play a track', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=Login');
  await page.fill('input[name=email]', 'test@example.com');
  await page.fill('input[name=password]', 'password');
  await page.click('button[type=submit]');
  await page.click('button[aria-label=Play]');
  // Assert audio is playing
});
```

## Key Technologies

### Frontend Stack
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Zustand**: State management
- **React Query**: Data fetching and caching
- **Web Audio API**: Audio playback and visualization

### Backend Stack
- **Node.js 20+**: Runtime
- **Express/Fastify**: Web framework
- **TypeScript**: Type safety
- **PostgreSQL**: Primary database
- **Redis**: Caching and sessions
- **Socket.io**: Real-time communication

### ML/AI Stack
- **Python 3.11+**: ML runtime
- **FastAPI**: ML service API
- **TensorFlow/PyTorch**: Deep learning
- **scikit-learn**: Traditional ML
- **OpenAI API**: LLM integration

## Common Tasks

### Add a New API Endpoint

1. Define route in `backend/src/routes/`
2. Create controller in `backend/src/controllers/`
3. Add service logic in `backend/src/services/`
4. Update API documentation
5. Write tests

### Add a New React Component

1. Create component in `frontend/src/components/`
2. Add TypeScript types
3. Style with Tailwind CSS
4. Export from index.ts
5. Write Storybook story (optional)
6. Write tests

### Add a Database Migration

```bash
cd backend
npm run migration:create -- add_user_preferences
# Edit the migration file
npm run migration:up
```

### Seed Test Data

```bash
cd backend
npm run seed
```

## Debugging Tips

### Frontend Debugging
- Use React DevTools
- Use browser Network tab for API calls
- Check console for errors
- Use `console.log` or debugger breakpoints

### Backend Debugging
- Use VS Code debugger (launch.json configured)
- Check logs: `npm run dev` shows detailed logs
- Use PostgreSQL client to inspect database
- Use Redis CLI: `redis-cli monitor`

### Audio Issues
- Check browser console for Web Audio API errors
- Verify audio file URLs are accessible
- Test in different browsers (Chrome, Firefox, Safari)
- Check CORS headers for audio files

## Contributing Guidelines

### Code Reviews
- All PRs require at least one review
- Address feedback promptly
- Keep PRs focused and small
- Update documentation as needed

### Communication
- Be respectful and constructive
- Ask questions in GitHub Discussions
- Use issues for bugs and features
- Join our Discord (link TBD)

### Documentation
- Update README for major changes
- Document new APIs in Swagger/OpenAPI
- Add inline code comments for complex logic
- Update architecture docs for structural changes

## Resources

### Learning Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [Web Audio API Guide](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [Recommendation Systems](https://developers.google.com/machine-learning/recommendation)

### Similar Projects
- [Infinite Radio](https://github.com/unforced/infinite-radio)
- [Melodisco](https://github.com/all-in-aigc/melodisco)
- [InfiniteRadio by LaurieWired](https://github.com/LaurieWired/InfiniteRadio)

### Tools
- [VS Code](https://code.visualstudio.com/) - Recommended IDE
- [Postman](https://www.postman.com/) - API testing
- [Figma](https://www.figma.com/) - Design collaboration
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL GUI

## Getting Help

### Where to Ask Questions
1. **GitHub Discussions**: General questions and ideas
2. **GitHub Issues**: Bugs and feature requests
3. **Discord** (TBD): Real-time chat
4. **Email**: fuzzywigg@example.com (project maintainer)

### Common Issues

**Issue**: Database connection fails
**Solution**: Check PostgreSQL is running and `.env` is configured correctly

**Issue**: Audio won't play
**Solution**: Check browser console, verify audio file exists, check CORS

**Issue**: Dependencies won't install
**Solution**: Clear node_modules and package-lock.json, then `npm install` again

**Issue**: Port already in use
**Solution**: Kill process on port: `lsof -ti:3000 | xargs kill -9` (Mac/Linux)

## Next Steps

1. **Read all documentation** in this repository
2. **Set up your development environment** (once MVP starts)
3. **Pick your first issue** from GitHub Issues (look for "good first issue" label)
4. **Join the community** via GitHub Discussions
5. **Start coding!** 🚀

## Welcome Aboard!

We're excited to have you contribute to QFZZ. This project aims to revolutionize personalized audio experiences through AI and knowledge integration. Your contributions, whether code, design, documentation, or ideas, help make this vision a reality.

**Happy coding!** 🎵🌌✨

---

**Questions?** Open a GitHub Discussion or reach out to the maintainers.

**Found a bug?** Open a GitHub Issue with reproduction steps.

**Have an idea?** Share it in GitHub Discussions - we'd love to hear it!
