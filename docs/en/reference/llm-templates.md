# LLM Prompt Templates

Prompt template collection for LLM-powered bookmark classification.

## Usage

### Method 1: Command Line Tool

```bash
# Generate batch classification prompt
python src/export_llm_prompt.py output/report_xxx.md

# Generate review prompt
python src/export_llm_prompt.py output/report_xxx.md -m review

# Generate export HTML prompt
python src/export_llm_prompt.py output/report_xxx.md -m export

# Save to file
python src/export_llm_prompt.py output/report_xxx.md -o prompt.txt
```

### Method 2: Direct Copy Templates

---

## Template 1: Batch Classification (Recommended)

For: Processing unclassified or low-confidence bookmarks

```markdown
# Bookmark Intelligent Classification Task

## Role
You are a professional information architect, skilled at accurately classifying web resources.

## Classification System

### Main Categories
- **Workbench**: Internal company systems, project management, internal tools
- **Artificial Intelligence**: AI model platforms, machine learning, AI coding tools, LLM applications
- **Programming**: Code repositories, programming languages, web development, DevOps
- **Biology**: Bioinformatics, genomics, single-cell analysis
- **Learning**: Technical documentation, tutorials, courses, books
- **Community**: Technical communities, forums, Q&A
- **News**: News, blogs, newsletters
- **Entertainment**: Video, games, music
- **Tools**: Online tools, software, productivity tools
- **Other**: Unclassifiable content

## Bookmarks to Classify

[Paste bookmark list here, format: Title | URL]

## Output Requirements

Output in JSON array format:
```json
[
  {
    "title": "Bookmark Title",
    "category": "Main Category/Subcategory",
    "confidence": 0.95,
    "reason": "Classification reason"
  }
]
```

## Classification Rules

1. **Domain Priority**:
   - github.com/gitlab.com → Programming/Code Repository
   - huggingface.co → AI/Model Platform
   - Internal company domains → Workbench

2. **Keyword Recognition**:
   - LLM/GPT/Claude/AI → Artificial Intelligence
   - Docker/K8s/DevOps → Programming/DevOps
   - Gene/Sequencing/Bioinfo → Biology

3. **Content Type**:
   - Documentation/Tutorial → Learning/Documentation
   - Forum/Community → Community
   - Tool/Service → Tools

Please start classifying:
```

---

## Template 2: Classification Review

For: Checking the accuracy of classified bookmarks

```markdown
# Bookmark Classification Review Task

## Task Description
Please review the following classified bookmarks and check if the classification is accurate.

## Current Classification Results

[Paste categorized bookmark list here]

## Review Points

1. **Accuracy**: Are bookmarks placed in the correct categories?
2. **Consistency**: Are similar bookmarks in the same category?
3. **Granularity**: Are categories too broad or too granular?

## Output Format

```json
{
  "corrections": [
    {
      "title": "Bookmark Title",
      "current": "Current Category",
      "suggested": "Suggested Category",
      "reason": "Reason for change"
    }
  ],
  "merge_suggestions": [
    {
      "from": ["Category A", "Category B"],
      "to": "Merged Category",
      "reason": "Merge reason"
    }
  ],
  "overall_feedback": "Overall evaluation and suggestions"
}
```

Please start reviewing:
```

---

## Template 3: Smart Organization

For: Deep organization and optimization of bookmarks

```markdown
# Bookmark Smart Organization Task

## Task Description
Please help me organize these bookmarks: deduplicate, optimize classification, and generate a clean bookmark structure.

## Raw Bookmarks

[Paste all bookmarks here]

## Organization Requirements

1. **Deduplication**: Remove duplicate or highly similar bookmarks
2. **Classification**: Reasonably categorize by topic
3. **Naming**: Optimize bookmark titles for clarity
4. **Sorting**: Sort similar bookmarks by importance/usage frequency

## Output Format

Output organized bookmarks by category:

```markdown
## Category Name

- [Bookmark Title](URL)
- [Bookmark Title](URL)

## Another Category

- [Bookmark Title](URL)
```

## Additional Output

1. List of deleted duplicate bookmarks
2. Category statistics
3. Organization suggestions

Please start organizing:
```

---

## Prompt Optimization Tips

### 1. Provide Context

Tell the LLM about your usage scenario:
```
I am a bioinformatics engineer, mainly focusing on genomics and AI applications...
```

### 2. Give Examples

Provide a few classification examples to help the LLM understand:
```
Examples:
- "BWA-MEM2 GitHub" → Biology/Bioinformatics
- "ChatGPT" → AI/Model Platform
- "Docker Hub" → Programming/DevOps
```

### 3. Specify Output Format

Clearly request JSON or Markdown format for easier subsequent processing.

### 4. Batch Processing

When there are too many bookmarks, process in batches of 50-100 for best results.

---

## FAQ

### Q: LLM classification is not accurate, what should I do?
A: Try providing more context and examples, or use a stronger model (such as GPT-4, Claude 3).

### Q: How to handle large numbers of bookmarks?
A: Use the command line tool to generate prompts in batches, 50-100 per batch.

### Q: How to import classification results back into the system?
A: Save the JSON results, an import feature can be developed later.
