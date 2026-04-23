# Team Setup

Share unified CleanBook configuration across your team.

## Config Repository

Create a Git repository for team configuration:

```
team-config/
├── config.json          # Unified team config
├── taxonomy/
│   ├── subjects.yaml    # Subject taxonomy
│   └── companies.yaml   # Company domain mapping
└── README.md
```

## Sharing Methods

### Method 1: Git Submodule

```bash
git submodule add https://github.com/your-team/cleanbook-config.git config/cleanbook
ln -s config/cleanbook/config.json config.json
```

### Method 2: Download

```bash
curl -O https://internal.company.com/cleanbook/config.json
```

### Method 3: Docker Image

```dockerfile
FROM python:3.11-slim
COPY team-config/ /etc/cleanbook/
RUN pip install cleanbook
ENV CLEANBOOK_CONFIG=/etc/cleanbook/config.json
ENTRYPOINT ["cleanbook"]
```
