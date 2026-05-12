# Taxonomy Format

<CbBadge text="Vocabulary Config" type="info" />

CleanBook uses YAML files to define controlled vocabularies and classification systems.

## File Locations

```
config/
└── taxonomy/
    ├── subjects.yaml         # Subject taxonomy
    └── resource_types.yaml   # Resource type taxonomy
```

## subjects.yaml

Defines the subject classification system.

### Basic Structure

```yaml
subjects:
  - preferred: "Artificial Intelligence"
    variants:
      - "AI"
      - "Machine Learning"
      - "Deep Learning"
      - "Neural Networks"
    icon: "🤖"
    description: "AI tools, platforms, and resources"

  - preferred: "Programming"
    variants:
      - "Development"
      - "Software Engineering"
      - "Code"
    icon: "💻"
    description: "Software development and programming languages"
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `preferred` | string | Yes | Preferred term (canonical name) |
| `variants` | array | No | Synonym list |
| `icon` | string | No | Category icon (Emoji) |
| `description` | string | No | Category description |
| `parent` | string | No | Parent category |

### Hierarchical Categories

```yaml
subjects:
  - preferred: "Programming"
    icon: "💻"

  - preferred: "Programming/Python"
    parent: "Programming"
    variants: ["Python Dev", "Py"]
    icon: "🐍"

  - preferred: "Programming/JavaScript"
    parent: "Programming"
    variants: ["JS", "JS Dev"]
    icon: "📜"
```

## resource_types.yaml

Defines resource type facets.

```yaml
resource_types:
  - name: "documentation"
    label: "Documentation"
    icon: "📚"
    description: "Official docs, API references, technical documentation"

  - name: "code_repository"
    label: "Repository"
    icon: "📦"
    description: "GitHub, GitLab, and other code repositories"

  - name: "tutorial"
    label: "Tutorial"
    icon: "📖"
    description: "Learning tutorials, getting started guides"

  - name: "tool"
    label: "Tool"
    icon: "🛠️"
    description: "Online tools, software, services"

  - name: "article"
    label: "Article"
    icon: "📝"
    description: "Blog posts, technical articles"

  - name: "video"
    label: "Video"
    icon: "▶️"
    description: "Video tutorials, talks"

  - name: "community"
    label: "Community"
    icon: "👥"
    description: "Forums, communities, Q&A sites"

  - name: "news"
    label: "News"
    icon: "📰"
    description: "News, newsletters, aggregators"
```

## Taxonomy Standardization

CleanBook uses taxonomy to map arbitrary text to canonical categories:

```python
from src.utils.taxonomy import TaxonomyStandardizer

standardizer = TaxonomyStandardizer()

# Normalize subject
standardizer.normalize_subject("Machine Learning")  # → "Artificial Intelligence"
standardizer.normalize_subject("ML")                # → "Artificial Intelligence"
standardizer.normalize_subject("AI")                # → "Artificial Intelligence"

# Normalize resource type
standardizer.normalize_resource_type("api-docs")  # → "documentation"
```

## Priority Rules

When ambiguity arises, the standardizer will:

1. Prefer full-word matches (e.g., "machine learning" > "learning")
2. Prefer preferred terms
3. Match in order of appearance (earlier = higher priority)

## Best Practices

1. **Keep it simple**: Don't create too many categories; 10-15 main categories recommended
2. **Clear naming**: Use concise, unambiguous names
3. **Add variants**: Include common synonyms for each category
4. **Regular maintenance**: Adjust taxonomy based on actual usage
5. **Version control**: Commit taxonomy files to version control

## Complete Example

```yaml
# subjects.yaml
subjects:
  - preferred: "Artificial Intelligence"
    variants: ["AI", "Machine Learning", "Deep Learning", "ML"]
    icon: "🤖"

  - preferred: "Programming"
    variants: ["Coding", "Development", "Software Engineering"]
    icon: "💻"

  - preferred: "Data Structures & Algorithms"
    variants: ["Algorithms", "Data Structures", "DSA"]
    parent: "Programming"
    icon: "🔢"

  - preferred: "Frontend Development"
    variants: ["Frontend", "Web Frontend", "FE"]
    parent: "Programming"
    icon: "🎨"

  - preferred: "Backend Development"
    variants: ["Backend", "Server-side", "BE"]
    parent: "Programming"
    icon: "⚙️"

  - preferred: "Developer Tools"
    variants: ["Tools", "DevTools"]
    icon: "🛠️"

  - preferred: "Technical Documentation"
    variants: ["Docs", "Documentation"]
    icon: "📚"

  - preferred: "Tech Community"
    variants: ["Community", "Forum"]
    icon: "👥"

  - preferred: "Tech News"
    variants: ["News", "Updates"]
    icon: "📰"
```

## Relationship with Classification Rules

Taxonomy and `category_rules` are complementary:

- **Taxonomy**: Defines "what categories exist"
- **Classification Rules**: Defines "how to identify these categories"

```
Taxonomy:
  - Artificial Intelligence

Rules:
  - If domain contains "openai.com" → Artificial Intelligence
  - If title contains "GPT" → Artificial Intelligence
```
