# 🚀 Advanced CI/CD Pipelines

Production-grade GitHub Actions workflows demonstrating enterprise DevOps patterns: multi-stage deployments, security scanning, automated testing, and observability.

---

## Workflows Overview

### 1. `advanced-pipeline.yml` — Main CI/CD Pipeline
**Trigger:** Push to `main`/`develop`, tags, PRs

**Stages:**
1. **Code Quality** — Lint (flake8) + Test (pytest) + Coverage
2. **Security Scan** — Trivy vulnerability scanning + Dependency check
3. **Build & Push** — Docker image with semantic versioning
4. **Deploy Dev** — Auto-deploy `develop` branch
5. **Deploy Staging** — Auto-deploy `main` branch
6. **Deploy Prod** — Auto-deploy on version tags (`v*`)
7. **Notify** — Slack notifications + PR comments

**Key Features:**
- Multi-environment deployment (dev → staging → prod)
- Automated security scanning
- Docker layer caching for fast builds
- Semantic versioning with git tags
- GitHub Container Registry integration
- Rollback capability

---

### 2. `manual-deploy.yml` — Manual Deployment
**Trigger:** Manual workflow dispatch

**Use Cases:**
- Hotfix deployments
- Specific version rollbacks
- Testing deployments outside normal flow

**Inputs:**
- `environment`: development | staging | production
- `image_tag`: Docker image tag to deploy
- `run_tests`: Run pre-deployment tests (boolean)

---

### 3. `scheduled-maintenance.yml` — Automated Maintenance
**Trigger:** Daily at 2 AM UTC (cron)

**Tasks:**
- **Health Checks** — Monitor production endpoints
- **Dependency Updates** — Check for outdated packages
- **Image Cleanup** — Delete old container images
- **Metrics Report** — Weekly deployment statistics

---

### 4. `performance-testing.yml` — Load & Stress Testing
**Trigger:** Weekly on Sunday (cron) or manual

**Tests:**
- **Load Testing** — k6 with graduated load (10 → 50 users)
- **Stress Testing** — Find breaking point
- **Performance Thresholds** — P95 < 500ms, error rate < 1%

---

## Setup Instructions

### Step 1: Add Workflows to Your Repo
```bash
cd devops-api

# Create workflows directory
mkdir -p .github/workflows

# Copy workflow files
cp advanced-pipeline.yml .github/workflows/
cp manual-deploy.yml .github/workflows/
cp scheduled-maintenance.yml .github/workflows/
cp performance-testing.yml .github/workflows/
```

### Step 2: Configure Secrets
Go to **GitHub repo → Settings → Secrets and variables → Actions**

Add these secrets (optional):
- `SLACK_WEBHOOK_URL` — For deployment notifications
- `PROD_DEPLOY_KEY` — SSH key for production deployments

### Step 3: Enable GitHub Container Registry
1. Go to **Settings → Packages**
2. Connect repository to package
3. Set package visibility (public/private)

### Step 4: Create Environment Protection Rules
Go to **Settings → Environments**

Create these environments with protection:
- `development` — No restrictions
- `staging` — Require reviewers (optional)
- `production` — Require manual approval + reviewers

---

## Usage Examples

### Deploy to Production
```bash
# Create a version tag
git tag v1.0.0
git push origin v1.0.0

# Pipeline automatically:
# 1. Runs tests
# 2. Scans for vulnerabilities
# 3. Builds Docker image
# 4. Deploys to staging
# 5. Waits for approval
# 6. Deploys to production
```

### Manual Deployment
1. Go to **Actions** tab
2. Select **Manual Deployment**
3. Click **Run workflow**
4. Choose environment and image tag
5. Click **Run workflow** button

### Rollback
```bash
# Option 1: Deploy previous version manually
# Find previous image tag in Container Registry
# Run manual deployment with that tag

# Option 2: Revert git commit
git revert <commit-hash>
git push origin main
```

---

## Pipeline Flow Diagram

```
┌─────────────────┐
│   Push to main  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lint & Test    │  ← Code quality checks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Security Scan   │  ← Trivy, dependency check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build Image     │  ← Docker build + push to GHCR
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│ Deploy Staging  │  │  Deploy Dev     │
└────────┬────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Integration     │  ← Tests on staging
│ Tests           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Manual Approval │  ← Production gate
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deploy Prod     │  ← Production deployment
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Notify & Report │  ← Slack, GitHub Release
└─────────────────┘
```

---

## Key Patterns Demonstrated

### 1. Multi-Stage Deployments
Progressive rollout through environments reduces production risk:
- **Development** — Latest changes, minimal testing
- **Staging** — Production-like, full integration tests
- **Production** — Manual approval gate, full monitoring

### 2. Security-First Pipeline
Security scanning before deployment:
- Filesystem scanning (Trivy)
- Container image scanning
- Dependency vulnerability checks
- Results uploaded to GitHub Security tab

### 3. Semantic Versioning
Automated version tagging:
- `main` branch → `latest` tag
- Git tags → Semantic version (`v1.2.3`, `v1.2`, `v1`)
- Branch commits → `<branch>-<sha>` tags

### 4. Environment Protection
GitHub Environments with:
- Manual approval for production
- Required reviewers
- Deployment branches restrictions
- Environment-specific secrets

### 5. Observability
Built-in monitoring:
- Deployment notifications (Slack)
- PR comments with build status
- GitHub Releases with changelogs
- Metrics reports

---

## Customization Guide

### Add a New Environment
1. Edit `advanced-pipeline.yml`
2. Copy `deploy-staging` job
3. Rename to new environment
4. Update environment name and URL
5. Create environment in GitHub Settings

### Add Deployment Target
Replace placeholder commands in deploy jobs:

**Kubernetes:**
```yaml
- name: Deploy to Production
  run: |
    kubectl set image deployment/api \
      api=ghcr.io/${{ github.repository }}:${{ github.sha }} \
      -n production
    kubectl rollout status deployment/api -n production
```

**Docker Swarm:**
```yaml
- name: Deploy to Production
  run: |
    docker service update \
      --image ghcr.io/${{ github.repository }}:${{ github.sha }} \
      api_service
```

**VM/EC2:**
```yaml
- name: Deploy to Production
  run: |
    ssh user@prod-server << 'EOF'
      cd /opt/api
      docker pull ghcr.io/${{ github.repository }}:${{ github.sha }}
      docker-compose up -d
    EOF
```

### Add Slack Notifications
1. Create Slack webhook: https://api.slack.com/messaging/webhooks
2. Add as secret: `SLACK_WEBHOOK_URL`
3. Uncomment notification steps in workflows

---

## What This Demonstrates

- **Enterprise CI/CD patterns** — Multi-stage pipelines with gates
- **Security scanning** — Vulnerability detection and reporting
- **Automated testing** — Unit, integration, and performance tests
- **Container registry** — Docker image management with GHCR
- **GitOps principles** — Infrastructure as code, version controlled
- **Deployment strategies** — Progressive rollout, manual approval
- **Observability** — Notifications, metrics, audit logs
- **DevOps automation** — Scheduled maintenance, dependency updates

---

## Cost

**GitHub Actions minutes:**
- Free tier: 2,000 minutes/month
- Public repos: Unlimited
- These workflows use ~10-15 minutes per run

**GitHub Container Registry:**
- Free for public repos
- 500MB free storage for private repos

---

## Troubleshooting

### "Resource not accessible by integration"
**Solution:** Enable workflow permissions:
- Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"

### Image push fails
**Solution:** Enable GitHub Packages:
- Settings → Packages
- Link repository to package

### Environment deployment stuck
**Solution:** Check environment protection rules:
- Settings → Environments → [environment name]
- Verify reviewers are set correctly

---

## Author

**Josimar Arias** — Software Engineer · Mesa, AZ  
[josimar85209@gmail.com](mailto:josimar85209@gmail.com) · [GitHub](https://github.com/josimar549) · [Portfolio](https://josimar549.github.io)

---

## License

MIT
