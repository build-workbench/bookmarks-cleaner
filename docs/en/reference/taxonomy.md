# Taxonomy Format

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

```yaml
subjects:
  - preferred: "Artificial Intelligence"
    variants:
      - "AI"
      - "Machine Learning"
      - "Deep Learning"
    icon: "🤖"
    description: "AI tools, platforms, and resources"
    
  - preferred: "Programming"
    variants:
      - "Development"
      - "Software Engineering"
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

## resource_types.yaml

```yaml
resource_types:
  - name: "documentation"
    label: "Documentation"
    icon: "📚"
    
  - name: "code_repository"
    label: "Repository"
    icon: "📦"
    
  - name: "tutorial"
    label: "Tutorial"
    icon: "📖"
    
  - name: "tool"
    label: "Tool"
    icon: "🛠️"
```

## Standardization

```python
from src.utils.taxonomy import TaxonomyStandardizer

standardizer = TaxonomyStandardizer()

# Normalize subject
standardizer.normalize_subject("Machine Learning")  # → "Artificial Intelligence"
standardizer.normalize_subject("ML")                # → "Artificial Intelligence"
```
