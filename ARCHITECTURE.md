# QFZZ Architecture Documentation

## System Overview

QFZZ is an AI-powered personalized radio platform that combines intelligent content recommendation, knowledge graph integration, and quantum-inspired discovery mechanisms to deliver a unique audio experience for each individual user.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Web App      │  │ Mobile App   │  │ API Clients  │          │
│  │ (Next.js)    │  │ (Future)     │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS / WSS
┌────────────────────────┴────────────────────────────────────────┐
│                      API Gateway Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Load Balancer / API Gateway (nginx/traefik)               │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────┬────────────────────────────┬────────────────────────────┘
         │                            │
         ├────────────────┬───────────┤
         │                │           │
┌────────▼──────┐  ┌─────▼─────┐  ┌──▼──────────┐
│ API Service   │  │ Streaming │  │ Real-time   │
│ (Express/     │  │ Service   │  │ Service     │
│  Fastify)     │  │           │  │ (WebSocket) │
└───────┬───────┘  └─────┬─────┘  └──────┬──────┘
        │                │                 │
        └────────────────┴─────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼─────────┐
│ Business Logic │              │ AI/ML Services    │
│                │              │                   │
│ - Auth         │              │ - Recommendations │
│ - User Mgmt    │              │ - Content Gen     │
│ - Content Mgmt │              │ - TTS             │
│ - Playlists    │              │ - LLM Integration │
└───────┬────────┘              └─────────┬─────────┘
        │                                  │
        └────────────────┬─────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼─────────┐
│ Data Layer     │              │ Cache Layer       │
│                │              │                   │
│ - PostgreSQL   │              │ - Redis           │
│ - Vector DB    │              │ - Memcached       │
│ - Elasticsearch│              │                   │
└────────────────┘              └───────────────────┘
```

## Component Details

### 1. Client Layer

#### Web Application (Next.js)
**Responsibilities:**
- User interface and interaction
- Audio player component
- Real-time visualization
- User authentication (NextAuth.js)
- Responsive design for all devices

**Key Features:**
- Server-side rendering for SEO
- Static generation for performance
- Client-side routing
- Progressive Web App capabilities

**Technology Stack:**
- Next.js 14+ (App Router)
- React 18+
- TypeScript
- Tailwind CSS
- Web Audio API
- Zustand (state management)

### 2. API Gateway Layer

**Responsibilities:**
- Request routing
- Load balancing
- Rate limiting
- SSL termination
- CORS handling
- Request/response transformation

**Technology:**
- Nginx or Traefik
- Optional: Kong or AWS API Gateway

### 3. Core API Service

**Responsibilities:**
- RESTful or GraphQL API endpoints
- Business logic orchestration
- Authentication and authorization
- Input validation
- Error handling

**Key Endpoints:**
```
Authentication:
- POST /api/auth/login
- POST /api/auth/register
- POST /api/auth/logout
- GET /api/auth/me

User Management:
- GET /api/users/profile
- PUT /api/users/profile
- GET /api/users/preferences
- PUT /api/users/preferences

Content:
- GET /api/tracks
- GET /api/tracks/:id
- GET /api/playlists
- POST /api/playlists
- GET /api/genres

Playback:
- GET /api/stream/:trackId
- POST /api/play-history
- POST /api/feedback (like/skip/rate)

Recommendations:
- GET /api/recommendations/for-you
- GET /api/recommendations/similar/:trackId
- GET /api/recommendations/discover

Knowledge Graph:
- GET /api/graph/connections
- GET /api/graph/explore/:nodeId
- POST /api/graph/link
```

**Technology Stack:**
- Node.js 20+
- Express.js or Fastify
- TypeScript
- Passport.js (authentication)
- Joi or Zod (validation)

### 4. Streaming Service

**Responsibilities:**
- Audio file serving
- Adaptive bitrate streaming
- Range request handling
- Format conversion (if needed)
- CDN integration

**Features:**
- HTTP streaming protocols
- Progressive download support
- Seek support
- Buffer management

**Technology:**
- Node.js streaming APIs
- FFmpeg (format conversion)
- AWS S3 or similar for storage
- CloudFront or Cloudflare CDN

### 5. Real-time Service

**Responsibilities:**
- Live updates to clients
- Presence detection
- Real-time collaboration features (future)
- Activity feed

**Events:**
- Track started/ended
- Playlist updated
- Recommendations refreshed
- User presence changes

**Technology:**
- Socket.io or native WebSocket
- Redis Pub/Sub for scaling
- Message queue for reliability

### 6. AI/ML Services

#### Recommendation Engine

**Components:**

1. **Collaborative Filtering**
   - User-user similarity
   - Item-item similarity
   - Matrix factorization
   - Neural collaborative filtering

2. **Content-Based Filtering**
   - Audio feature extraction
   - Metadata matching
   - Genre/mood similarity
   - Tempo/energy alignment

3. **Hybrid System**
   - Weighted combination
   - Context-aware switching
   - Cold-start handling
   - Exploration vs exploitation

**Data Flow:**
```
User Interaction → Feature Extraction → Model Inference → Ranking → API Response
                     ↓
                 Training Pipeline
                     ↓
                 Model Update
```

**Technology:**
- Python (TensorFlow, PyTorch, scikit-learn)
- Surprise library for collaborative filtering
- FastAPI for ML service API
- MLflow for model management

#### Content Generation Service

**Capabilities:**
- AI DJ commentary generation
- Show script creation
- News summarization
- Playlist description generation

**Technology:**
- OpenAI GPT-4 API
- Anthropic Claude API
- Local LLMs (optional, LLaMA 2/3)

#### Text-to-Speech Service

**Features:**
- Natural voice generation
- Custom AI DJ personas
- Multiple voice options
- Emotion/tone control

**Technology:**
- ElevenLabs API
- OpenAI TTS API
- Local models (Coqui TTS, optional)

### 7. Knowledge Graph System

**Purpose:**
- Connect content through semantic relationships
- Track user's learning and exploration journey
- Enable bidirectional content discovery
- Integrate with BackLink repository

**Schema:**
```graphql
Node {
  id: ID!
  type: NodeType! (Track, Album, Artist, Genre, Mood, Theme, Concept)
  metadata: JSON
  embeddings: Vector
}

Edge {
  id: ID!
  source: ID!
  target: ID!
  type: EdgeType! (SimilarTo, LeadsTo, PartOf, InspiredBy, ThemeOf)
  weight: Float
  metadata: JSON
}

UserJourney {
  userId: ID!
  nodes: [ID!]
  timestamp: DateTime
  context: JSON
}
```

**Operations:**
- Find related nodes
- Traverse paths
- Shortest path between concepts
- Cluster detection
- Community detection

**Technology:**
- Neo4j (graph database)
- Or PostgreSQL with recursive queries
- Graph visualization (D3.js, Cytoscape.js)

### 8. Data Layer

#### PostgreSQL (Primary Database)

**Schema Overview:**

```sql
-- Users and Authentication
users (
  id, username, email, password_hash,
  created_at, updated_at
)

user_profiles (
  user_id, display_name, avatar_url,
  bio, preferences_json
)

-- Content
tracks (
  id, title, artist, album, duration,
  file_path, genre, mood, energy, tempo,
  metadata_json, created_at
)

playlists (
  id, user_id, name, description,
  is_public, created_at, updated_at
)

playlist_tracks (
  playlist_id, track_id, position
)

-- User Activity
play_history (
  id, user_id, track_id,
  started_at, completed_at,
  completion_percentage, skipped
)

feedback (
  id, user_id, track_id,
  type (like/dislike/skip), created_at
)

-- Recommendations
user_embeddings (
  user_id, embedding_vector, updated_at
)

track_embeddings (
  track_id, embedding_vector, updated_at
)
```

#### Redis (Cache & Session Storage)

**Use Cases:**
- User sessions
- Recently played tracks (cache)
- Recommendation cache
- Rate limiting counters
- Real-time presence data

**Key Patterns:**
```
user:session:{token}
user:recent:{userId}
recommendations:{userId}
ratelimit:{ip}:{endpoint}
```

#### Elasticsearch (Search & Discovery)

**Indexed Data:**
- Track metadata (searchable)
- Artist information
- Playlist descriptions
- User-generated content

**Features:**
- Full-text search
- Fuzzy matching
- Faceted search
- Aggregations

#### Vector Database (Embeddings)

**Purpose:**
- Store high-dimensional embeddings
- Fast similarity search
- Semantic search capabilities

**Options:**
- Pinecone
- Weaviate
- Qdrant
- pgvector (PostgreSQL extension)

### 9. Storage Layer

#### Object Storage (Audio Files)

**Structure:**
```
bucket/
  tracks/
    {track_id}/
      original.{format}
      compressed.mp3
      compressed.ogg
  generated/
    commentary/
      {id}.mp3
  covers/
    {id}.jpg
```

**Technology:**
- AWS S3
- Google Cloud Storage
- MinIO (self-hosted)

**Features:**
- Pre-signed URLs for secure access
- Lifecycle policies for old data
- CDN integration
- Multi-region replication

## Data Flow Diagrams

### User Authentication Flow
```
User → Web App → API Gateway → Auth Service → PostgreSQL
                                      ↓
                                  JWT Token
                                      ↓
                                  Redis Cache
                                      ↓
                                  ← Response
```

### Playback Request Flow
```
User clicks play
    ↓
Web App requests stream URL
    ↓
API Service checks auth
    ↓
API Service generates pre-signed URL
    ↓
Web App streams from CDN/S3
    ↓
Playback events sent via WebSocket
    ↓
Real-time Service updates Redis
    ↓
Background job logs to PostgreSQL
```

### Recommendation Generation Flow
```
User requests recommendations
    ↓
API checks Redis cache
    ↓
If miss: ML Service queries
    ↓
ML Service fetches user embeddings (PostgreSQL)
    ↓
ML Service searches similar tracks (Vector DB)
    ↓
ML Service ranks results
    ↓
Results cached in Redis
    ↓
Response to user
```

### Content Generation Flow
```
Trigger: New track added or user requests AI commentary
    ↓
Content Gen Service fetches track metadata
    ↓
LLM generates script/commentary
    ↓
TTS Service converts to audio
    ↓
Audio saved to S3
    ↓
Reference stored in PostgreSQL
    ↓
Available for playback
```

## Scaling Considerations

### Horizontal Scaling
- API services run in multiple instances behind load balancer
- Stateless design (sessions in Redis)
- Database read replicas
- CDN for static assets and audio files

### Caching Strategy
- **L1**: Browser cache (service worker)
- **L2**: CDN cache (audio files, static assets)
- **L3**: Redis cache (API responses, user data)
- **L4**: Database query cache

### Performance Optimizations
- Database indexing strategy
- Query optimization
- Connection pooling
- Lazy loading of audio files
- Pre-fetching next track
- Compression (gzip, brotli)

## Security Architecture

### Authentication & Authorization
- JWT-based authentication
- Refresh token rotation
- OAuth 2.0 for social login
- Role-based access control (RBAC)
- API key management for integrations

### Data Security
- Encryption at rest (database, storage)
- Encryption in transit (TLS 1.3)
- Secure password hashing (bcrypt/argon2)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS prevention (Content Security Policy)

### Privacy
- GDPR compliance
- Data minimization
- User data export capability
- Right to deletion
- Anonymization of analytics data

## Monitoring & Observability

### Metrics (Prometheus)
- Request rate, latency, errors (RED)
- Resource utilization (CPU, memory, disk)
- Cache hit rates
- Recommendation quality metrics
- User engagement metrics

### Logging (Structured Logs)
- Application logs (info, warn, error)
- Access logs
- Audit logs (user actions)
- Error tracking with stack traces

### Tracing (Distributed Tracing)
- Request flow across services
- Bottleneck identification
- Dependency mapping

### Alerting
- Error rate thresholds
- Latency thresholds
- Resource exhaustion
- Service health checks

**Tools:**
- Prometheus + Grafana
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Sentry (error tracking)
- Jaeger (distributed tracing)

## Development & Deployment

### Local Development
```yaml
docker-compose.yml:
  - postgres
  - redis
  - nginx
  - api-service
  - frontend (Next.js dev server)
```

### CI/CD Pipeline
```
Git Push → GitHub Actions
    ↓
Lint & Test
    ↓
Build Docker Images
    ↓
Push to Registry
    ↓
Deploy to Staging
    ↓
Run Integration Tests
    ↓
Manual Approval
    ↓
Deploy to Production
```

### Infrastructure as Code
- Terraform for cloud resources
- Kubernetes manifests for orchestration
- Helm charts for deployments
- Ansible for configuration management

### Environments
- **Development**: Local Docker Compose
- **Staging**: Kubernetes cluster (mimics production)
- **Production**: Kubernetes cluster with auto-scaling

## Future Architecture Enhancements

### Phase 2: Advanced Features
- Real-time collaboration (listening parties)
- Social features (followers, shared playlists)
- Mobile apps (React Native)
- Offline mode (PWA with IndexedDB)

### Phase 3: Scale & Global
- Multi-region deployment
- Edge computing for low latency
- Blockchain for content rights (optional)
- Federated learning for privacy

### Phase 4: Ecosystem
- Public API for developers
- Plugin system for extensions
- Integration marketplace
- White-label solution

## Integration Points

### BackLink Repository Integration
If integrating with existing BackLink system:

**API Integration:**
```
QFZZ → BackLink API
  - Create backlinks from tracks to notes
  - Query related content
  - Sync user preferences

BackLink → QFZZ API
  - Embed audio player in notes
  - Auto-play related content
  - Cross-reference audio and text
```

**Shared Data:**
- User authentication (SSO)
- Knowledge graph nodes
- Tags and categories
- User preferences

## Technology Decisions & Rationale

### Why Next.js?
- Excellent developer experience
- Built-in SSR/SSG for performance and SEO
- API routes for backend-for-frontend
- Strong ecosystem and community
- Easy deployment (Vercel)

### Why PostgreSQL?
- ACID compliance for critical user data
- Rich query capabilities (JSON, arrays, full-text search)
- pgvector extension for embeddings
- Mature and reliable
- Great performance for read-heavy workloads

### Why Redis?
- Extremely fast for caching
- Pub/Sub for real-time features
- Session storage
- Sorted sets for leaderboards/recommendations
- Easy to scale

### Why Docker & Kubernetes?
- Consistent development and production environments
- Easy scaling and orchestration
- Rolling updates with zero downtime
- Resource isolation
- Industry standard

## Conclusion

This architecture provides a solid foundation for QFZZ while allowing for future growth and enhancements. The modular design ensures that components can be developed, tested, and deployed independently. The use of industry-standard technologies reduces risk and ensures a strong ecosystem of tools and libraries.

The architecture balances simplicity (for MVP) with scalability (for future growth), ensuring that QFZZ can start small but grow into a robust, production-grade platform.
