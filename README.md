# SGD - Intelligent Document Management System

A comprehensive, production-ready document management system with AI-powered processing, semantic search, and automated workflows.

## 🚀 Features

### Core Capabilities
- **AI-Powered Processing**: OCR, NLP, automatic classification, and summarization
- **Semantic Search**: Vector-based search using OpenAI embeddings and Weaviate
- **Chat with Documents**: RAG-powered conversational interface
- **Mobile Integration**: Google AppSheet for mobile document upload
- **Automated Workflows**: n8n integration for approval processes and notifications
- **Role-Based Access Control**: Keycloak authentication with fine-grained permissions
- **Real-time Analytics**: Comprehensive dashboards and reporting
- **Complete Audit Trail**: Full logging and compliance tracking

### Technical Architecture
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **AI/ML**: Python + spaCy + OpenAI + Tesseract
- **Database**: PostgreSQL + Weaviate (vector DB)
- **Storage**: MinIO (S3-compatible)
- **Authentication**: Keycloak
- **Workflows**: n8n
- **Infrastructure**: Docker + Docker Compose

## 📋 Prerequisites

- Docker >= 20.10
- Docker Compose >= 2.0
- Node.js >= 18
- Python >= 3.11
- 8GB+ RAM (16GB recommended)
- 50GB+ storage
- OpenAI API key

## ⚡ Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sgd-system
   ```

2. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Run setup script**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/setup.sh
   ```

4. **Verify installation**
   ```bash
   ./scripts/smoke-test.sh
   ```

## 🌐 Service URLs

After successful deployment:

- **📱 Frontend**: http://localhost:3000
- **📚 API Documentation**: http://localhost:8000/docs
- **🤖 AI Service**: http://localhost:8001/docs
- **🔐 Keycloak Admin**: http://localhost:8090
- **💾 MinIO Console**: http://localhost:9001
- **🔄 n8n Workflows**: http://localhost:5678

## 📖 Documentation

- **[Complete Deployment Guide](DEPLOYMENT.md)**: Step-by-step setup instructions
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation
- **[Architecture Overview](docs/architecture.md)**: System design and components

## 🛠️ Development

### Backend Services

```bash
# API Service (main backend)
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# AI Service (document processing)
cd backend/ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Audit Service (logging)
cd backend/audit-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

### Frontend Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Development

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart api-service
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
POSTGRES_DB=sgd_db
POSTGRES_USER=sgd_user
POSTGRES_PASSWORD=your_password

# Authentication
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin_password

# AI Services
OPENAI_API_KEY=your_openai_key

# Storage
MINIO_ROOT_USER=sgd_minio
MINIO_ROOT_PASSWORD=minio_password
```

### Service Configuration

- **API Service**: Configure in `backend/api/main.py`
- **AI Service**: Configure in `backend/ai-service/main.py`
- **Database**: Schema in `scripts/init-db.sql`
- **Frontend**: Environment variables in `.env`

## 🔍 Usage Examples

### Document Upload and Processing

1. **Web Interface**
   - Navigate to Documents → Upload
   - Select file and fill metadata
   - AI automatically processes: OCR → NLP → Classification → Indexing

2. **AppSheet Mobile**
   - Open SGD app on mobile
   - Take photo or select document
   - Fill form and upload
   - Document processed in background

### Semantic Search

```javascript
// Text search
query: "financial report Q4"

// Semantic search (AI-powered)
query: "What were our sales figures last quarter?"
```

### Chat with Documents

```javascript
// Example queries
"What are the key findings in this report?"
"Summarize the main recommendations"
"What risks are mentioned?"
```

## 📊 Analytics and Monitoring

### Built-in Dashboards
- Document processing metrics
- User activity analytics
- Storage usage tracking
- AI performance metrics
- System health monitoring

### Health Checks
```bash
# System health
curl http://localhost:8000/health/detailed

# Individual services
curl http://localhost:8001/health  # AI Service
curl http://localhost:8002/health  # Audit Service
```

## 🔐 Security Features

- **Authentication**: Keycloak with OAuth2/OIDC
- **Authorization**: Role-based access control (RBAC)
- **Audit Logging**: Complete activity tracking
- **Data Encryption**: TLS in transit, encrypted storage
- **Input Validation**: Comprehensive request validation
- **File Security**: Malware scanning and type validation

## 📱 Mobile Integration (AppSheet)

### Setup Steps
1. Create AppSheet app connected to PostgreSQL
2. Configure document upload forms
3. Set up MinIO integration for file storage
4. Connect workflows for processing

### Features
- Mobile document capture
- Offline form completion
- Automatic metadata extraction
- Integration with main system

## 🔄 Workflow Automation (n8n)

### Pre-built Workflows
- **Document Approval**: Multi-stage approval process
- **Expiration Alerts**: Contract and document expiration notifications
- **Auto-categorization**: AI-based document routing
- **Compliance Checks**: Regulatory compliance workflows

### Custom Workflows
- Drag-and-drop workflow builder
- 200+ integrations available
- Email, Slack, Teams notifications
- Database operations and API calls

## 🚨 Troubleshooting

### Common Issues

**Services won't start:**
```bash
docker-compose down
docker system prune
docker-compose up -d
```

**Database connection issues:**
```bash
docker-compose logs postgres
docker-compose restart postgres
```

**AI processing failures:**
```bash
docker-compose logs ai-service
# Check OpenAI API key configuration
```

### Performance Optimization

**For high-volume processing:**
- Increase AI service resources
- Scale Weaviate cluster
- Optimize database queries
- Use Redis caching

## 🧪 Testing

```bash
# Run smoke tests
./scripts/smoke-test.sh

# API testing
curl -X POST http://localhost:8000/documents/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Frontend testing
npm test
```

## 🔄 Updates and Maintenance

### Regular Maintenance
```bash
# Update services
docker-compose pull
docker-compose up -d

# Database backup
./scripts/backup.sh

# System cleanup
docker system prune
```

### Monitoring Scripts
- Health check automation
- Performance monitoring
- Backup verification
- Security scanning

## 📈 Scalability

### Horizontal Scaling
- Load balancer configuration
- Database clustering
- Microservice replication
- CDN integration

### Performance Tuning
- Caching strategies
- Database optimization
- AI model optimization
- Resource allocation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend
- Write comprehensive tests
- Document API changes
- Update deployment guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: Create GitHub issues
- **Discussions**: GitHub discussions

## 🗺️ Roadmap

### Upcoming Features
- [ ] Advanced OCR for handwritten text
- [ ] Multi-language support expansion
- [ ] Blockchain document verification
- [ ] Advanced analytics with ML insights
- [ ] Voice-to-text document creation
- [ ] Integration with major cloud providers

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Enhanced AI processing
- **v1.2.0**: Mobile optimization
- **v2.0.0**: Multi-tenant architecture (planned)

---

Built with ❤️ for intelligent document management.