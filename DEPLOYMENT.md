# SGD - Intelligent Document Management System
## Complete Deployment & Usage Manual

### Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [AppSheet Integration](#appsheet-integration)
6. [n8n Workflow Setup](#n8n-workflow-setup)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## System Overview

The SGD (Smart Document Gateway) is a comprehensive intelligent document management system that provides:

### Architecture Components
- **Frontend**: React web application with modern UI
- **Backend API**: FastAPI service for document management
- **AI Service**: Python service for OCR, NLP, and classification
- **Audit Service**: Logging and compliance tracking
- **Database**: PostgreSQL for structured data
- **Storage**: MinIO (S3-compatible) for document files
- **Search**: Weaviate vector database for semantic search
- **Auth**: Keycloak for identity and access management
- **Workflows**: n8n for process automation
- **Mobile Interface**: Google AppSheet integration

### Key Features
- 🤖 AI-powered document processing (OCR, NLP, classification)
- 🔍 Semantic search with OpenAI embeddings
- 💬 Chat with documents using RAG
- 📱 Mobile document upload via AppSheet
- 🔄 Automated workflows and notifications
- 📊 Real-time analytics and reporting
- 🔐 Role-based access control
- 📝 Complete audit logging

---

## Prerequisites

### Required Software
```bash
# Core requirements
- Docker >= 20.10
- Docker Compose >= 2.0
- Node.js >= 18
- Python >= 3.11
- Git

# Optional (for development)
- curl
- jq
- make
```

### Hardware Requirements
- **Minimum**: 8GB RAM, 4 CPU cores, 50GB storage
- **Recommended**: 16GB RAM, 8 CPU cores, 100GB storage

### External Services
- OpenAI API key (for AI features)
- Google Account (for AppSheet)
- SMTP server (for notifications)

---

## Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd sgd-system
```

### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit configuration
nano .env
```

### Required Environment Variables
```bash
# Database Configuration
POSTGRES_DB=sgd_db
POSTGRES_USER=sgd_user
POSTGRES_PASSWORD=your_secure_password_here

# MinIO Configuration
MINIO_ROOT_USER=sgd_minio
MINIO_ROOT_PASSWORD=your_secure_minio_password_here

# Keycloak Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=your_secure_keycloak_password_here
KEYCLOAK_REALM=sgd-realm
KEYCLOAK_CLIENT_ID=sgd-client

# AI Service Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
```

### Step 3: Run Setup Script
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup (will build and start all services)
./scripts/setup.sh
```

### Step 4: Verify Installation
```bash
# Run smoke tests
./scripts/smoke-test.sh

# Check service status
docker-compose ps
```

---

## Configuration

### Keycloak Setup

1. **Access Keycloak Admin Console**
   ```
   URL: http://localhost:8090
   Username: admin
   Password: [KEYCLOAK_ADMIN_PASSWORD from .env]
   ```

2. **Create SGD Realm**
   - Click "Add realm"
   - Name: `sgd-realm`
   - Enable: `Enabled`

3. **Create Client**
   - Client ID: `sgd-client`
   - Client Protocol: `openid-connect`
   - Access Type: `confidential`
   - Valid Redirect URIs: `http://localhost:3000/*`

4. **Configure Roles**
   ```
   - administrator (full access)
   - manager (document management)
   - user (upload and view)
   - viewer (view only)
   ```

5. **Create Users**
   - Add users with appropriate roles
   - Set temporary passwords
   - Configure email settings

### MinIO Setup

1. **Access MinIO Console**
   ```
   URL: http://localhost:9001
   Username: [MINIO_ROOT_USER from .env]
   Password: [MINIO_ROOT_PASSWORD from .env]
   ```

2. **Create Buckets**
   - `documents` (for uploaded files)
   - `backups` (for system backups)

3. **Configure Access Policies**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {"AWS": "*"},
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::documents/*"
       }
     ]
   }
   ```

### Weaviate Schema Setup

The system automatically creates the required schema, but you can verify:

```bash
# Check schema
curl http://localhost:8080/v1/schema

# Expected response should include "Document" class
```

---

## AppSheet Integration

### Step 1: Create AppSheet App

1. **Go to AppSheet**
   ```
   URL: https://www.appsheet.com
   Sign in with Google account
   ```

2. **Create New App**
   - Click "Create" > "App"
   - Choose "Start with your own data"
   - Select "Other data sources"

### Step 2: Configure Data Source

1. **Connect to PostgreSQL**
   ```
   Host: [YOUR_SERVER_IP]:5432
   Database: sgd_db
   Username: sgd_user
   Password: [POSTGRES_PASSWORD]
   ```

2. **Select Tables**
   - `documents` (main documents table)
   - `categories` (document categories)
   - `users` (for user references)

### Step 3: Configure Document Upload

1. **Add Upload View**
   ```yaml
   View Name: "Upload Document"
   Type: "Form"
   Table: "documents"
   ```

2. **Configure Form Fields**
   ```yaml
   Fields:
     - title (required text)
     - description (long text)
     - category_id (choice from categories)
     - tags (text, comma-separated)
     - file_upload (image/file)
   ```

3. **Add Validation Rules**
   ```javascript
   // File size validation (max 50MB)
   [file_upload].[file_size] <= 52428800
   
   // Required fields
   NOT(ISBLANK([title]))
   ```

### Step 4: Configure Workflows

1. **Add Workflow for Upload**
   ```yaml
   Trigger: "On Form Save"
   Action: "Call API"
   URL: "http://[YOUR_SERVER]/api/appsheet/upload"
   Method: "POST"
   ```

2. **Configure API Integration**
   ```javascript
   // AppSheet will send data to our API endpoint
   // The API will handle file processing and AI analysis
   ```

### Step 5: Connect to MinIO for File Storage

1. **Configure AppSheet to use MinIO**
   ```yaml
   Storage Provider: "Amazon S3"
   Endpoint: "http://[YOUR_SERVER]:9000"
   Access Key: [MINIO_ROOT_USER]
   Secret Key: [MINIO_ROOT_PASSWORD]
   Bucket: "documents"
   ```

### Step 6: Test Mobile Upload

1. **Install AppSheet on Mobile**
   - Download from App Store/Play Store
   - Sign in with same Google account

2. **Test Document Upload**
   - Open SGD app
   - Fill form with document details
   - Take photo or select file
   - Submit form

---

## n8n Workflow Setup

### Step 1: Access n8n

```
URL: http://localhost:5678
Username: admin
Password: [N8N_BASIC_AUTH_PASSWORD from .env]
```

### Step 2: Create Document Approval Workflow

1. **Create New Workflow**
   - Name: "Document Approval Process"

2. **Add Nodes**
   ```yaml
   1. Webhook (trigger when document uploaded)
   2. HTTP Request (get document details)
   3. Condition (check if approval needed)
   4. Email (send approval request)
   5. Wait (wait for approval response)
   6. HTTP Request (update document status)
   7. Email (send notification)
   ```

3. **Configure Webhook**
   ```yaml
   Method: POST
   Path: /webhook/document-approval
   Authentication: None
   ```

4. **Configure Email Node**
   ```yaml
   SMTP Host: [SMTP_HOST]
   SMTP Port: [SMTP_PORT]
   Username: [SMTP_USER]
   Password: [SMTP_PASSWORD]
   ```

### Step 3: Create Expiration Notification Workflow

1. **Create Workflow**
   - Name: "Contract Expiration Alerts"

2. **Add Cron Trigger**
   ```yaml
   Schedule: "0 9 * * *" (daily at 9 AM)
   ```

3. **Add Database Query**
   ```sql
   SELECT * FROM documents 
   WHERE metadata->>'expiration_date' < NOW() + INTERVAL '30 days'
   AND status = 'active'
   ```

4. **Add Notification Logic**
   ```yaml
   - Email to document owner
   - Slack message to team
   - Create reminder task
   ```

### Step 4: Create Auto-Categorization Workflow

1. **Trigger**: Document processed by AI
2. **Logic**: Use AI classification results
3. **Actions**: 
   - Update document category
   - Tag document
   - Route to appropriate folder
   - Notify relevant team

---

## Usage Examples

### Document Upload via Web Interface

1. **Access Frontend**
   ```
   URL: http://localhost:3000
   Login with Keycloak credentials
   ```

2. **Upload Document**
   ```javascript
   // Navigate to Documents > Upload
   // Fill form:
   - Title: "Q4 Financial Report"
   - Description: "Quarterly financial analysis"
   - Category: "Financial"
   - Tags: "quarterly, report, 2024"
   - File: select PDF file
   ```

3. **Document Processing**
   ```
   1. File uploaded to MinIO
   2. Metadata saved to PostgreSQL
   3. AI service processes document:
      - OCR extracts text
      - NLP analyzes content
      - Classification assigns category
      - Summary generated
   4. Document indexed in Weaviate
   5. Available for search
   ```

### Semantic Search

1. **Access Search Page**
   ```
   Navigate to Search section
   ```

2. **Perform Search**
   ```javascript
   // Text search
   Query: "quarterly financial performance"
   
   // Semantic search (AI-powered)
   Enable: "Semantic Search" toggle
   Query: "How did we perform financially last quarter?"
   ```

3. **Results**
   ```
   - Ranked by relevance
   - Highlighted excerpts
   - Document metadata
   - Quick actions (view, download, chat)
   ```

### Chat with Documents (RAG)

1. **Select Document**
   ```
   From search results or document list
   Click "Chat" button
   ```

2. **Ask Questions**
   ```javascript
   // Example queries:
   "What were the key findings in this report?"
   "What are the main risks mentioned?"
   "Summarize the recommendations"
   "What is the projected revenue growth?"
   ```

3. **AI Response**
   ```
   - Context-aware answers
   - Source citations
   - Follow-up questions
   - Export conversation
   ```

### Analytics Dashboard

1. **Access Analytics**
   ```
   Navigate to Analytics section
   ```

2. **View Metrics**
   ```yaml
   Overview:
     - Total documents processed
     - Processing time trends
     - User activity
     - Storage usage
   
   Categories:
     - Document distribution
     - Growth trends
     - Popular content types
   
   Performance:
     - OCR accuracy
     - Classification success rate
     - Search effectiveness
   ```

### Admin Functions

1. **User Management**
   ```
   Navigate to Admin > Users
   - Add/edit/disable users
   - Assign roles
   - View activity logs
   ```

2. **System Configuration**
   ```
   Admin > System
   - Monitor service health
   - Adjust settings
   - View system logs
   ```

3. **Audit Logs**
   ```
   Admin > Audit Logs
   - Filter by user/action/date
   - Export compliance reports
   - Track document access
   ```

---

## Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check Docker status
docker --version
docker-compose --version

# Check system resources
docker system df
docker system prune

# Restart services
docker-compose down
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U sgd_user -d sgd_db -c "SELECT 1;"

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### AI Service Errors
```bash
# Check AI service logs
docker-compose logs ai-service

# Common issues:
- OpenAI API key not set
- spaCy models not downloaded
- Insufficient memory

# Fix spaCy models
docker-compose exec ai-service python -m spacy download en_core_web_sm
docker-compose exec ai-service python -m spacy download es_core_news_sm
```

#### MinIO Access Issues
```bash
# Check MinIO logs
docker-compose logs minio

# Reset MinIO
docker-compose down
docker volume rm sgd_minio_data
docker-compose up -d minio
```

### Performance Issues

#### Slow Document Processing
```bash
# Check resource usage
docker stats

# Increase AI service resources
# Edit docker-compose.yml:
ai-service:
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: "2"
```

#### Search Performance
```bash
# Check Weaviate logs
docker-compose logs weaviate

# Optimize Weaviate configuration
# Increase vectorizer batch size
# Add more memory to Weaviate service
```

### Log Analysis

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs -f api-service

# Search logs
docker-compose logs | grep ERROR

# Export logs
docker-compose logs > system.log 2>&1
```

---

## Maintenance

### Backup Procedures

#### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U sgd_user sgd_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U sgd_user sgd_db < backup_20240115.sql
```

#### MinIO Backup
```bash
# Backup documents
docker-compose exec minio mc cp --recursive minio/documents ./backups/documents_$(date +%Y%m%d)/

# Restore documents
docker-compose exec minio mc cp --recursive ./backups/documents_20240115/ minio/documents/
```

#### Full System Backup
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$DATE

# Database
docker-compose exec postgres pg_dump -U sgd_user sgd_db > backups/$DATE/database.sql

# MinIO data
docker-compose exec minio mc cp --recursive minio/documents backups/$DATE/documents

# Configuration
cp .env backups/$DATE/
cp docker-compose.yml backups/$DATE/

# Compress
tar -czf backups/sgd_backup_$DATE.tar.gz backups/$DATE/
```

### Updates and Upgrades

#### Update Services
```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Update services
docker-compose down
docker-compose up -d
```

#### Database Migrations
```bash
# Run migrations
docker-compose exec api-service alembic upgrade head

# Check migration status
docker-compose exec api-service alembic current
```

### Monitoring

#### Health Checks
```bash
# Run health checks
curl http://localhost:8000/health/detailed

# Automated monitoring script
#!/bin/bash
services=("api-service" "ai-service" "postgres" "minio" "weaviate")
for service in "${services[@]}"; do
    if ! docker-compose ps $service | grep -q "Up"; then
        echo "ALERT: $service is down"
        # Send notification
    fi
done
```

#### Performance Monitoring
```bash
# System resources
docker stats

# Service-specific metrics
curl http://localhost:8000/analytics/metrics
curl http://localhost:8001/health
curl http://localhost:8080/v1/meta
```

### Security

#### SSL/TLS Setup
```bash
# Generate certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/private.key -out ssl/certificate.crt

# Update nginx configuration
# Add SSL termination proxy
```

#### Security Hardening
```bash
# Update passwords regularly
# Enable firewall
# Use secrets management
# Regular security updates
# Monitor access logs
```

---

## Support and Documentation

### Additional Resources
- API Documentation: http://localhost:8000/docs
- AI Service Docs: http://localhost:8001/docs
- Audit Service Docs: http://localhost:8002/docs

### Getting Help
- Check logs: `docker-compose logs [service]`
- Run diagnostics: `./scripts/smoke-test.sh`
- Monitor health: `curl http://localhost:8000/health/detailed`

### Contributing
- Follow coding standards
- Add tests for new features
- Update documentation
- Submit pull requests

This completes the comprehensive deployment and usage manual for the SGD Intelligent Document Management System.