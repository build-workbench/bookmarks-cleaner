# Browser Bookmark Management Best Practices

In the era of information explosion, browser bookmarks are our personal map for navigating the digital world. However, a disorganized, poorly maintained bookmark library not only reduces our efficiency in finding information but also becomes a mental burden.

CleanBook aims to solve the "entropy increase" problem of bookmarks through automation. This document provides a comprehensive set of best practices ranging from daily habits to tool usage and advanced techniques, helping you build an efficient, well-organized personal knowledge base that truly serves you.

---

## The Golden Four Principles: Develop Efficient Bookmark Habits

### 1. Select Carefully, Decisively "Let Go"

**Principle:** Bookmarks are for "reference", not for "collection".

Before clicking the "bookmark" button, ask yourself: "**Will I actually visit this page again in a month?**"

- **Only save frequently visited sites:** Create bookmarks only for websites, tools, or documents you know you'll revisit
- **Distinguish "to-do" from "reference":** If a link is just an article to read later, use a read-later service like Pocket or Instapaper instead of polluting your reference library
- **Avoid "emotion-based collection":** Often we bookmark because something "looks useful," but 99% of such links are never opened again. Let them go decisively

### 2. Smart Naming for Future Search

**Principle:** Bookmark names serve YOU, not the website.

Never settle for default website titles, especially when they're vague (like "Home", "Login").

- **Consistent format:** Adopt a fixed naming format like `[Project/Topic] - [Specific Content]`
  - ❌ `Dashboard`
  - ✅ `[Work] - LUSH Project Management Panel`
  - ❌ `The Illustrated Word2vec`
  - ✅ `[AI] - Illustrated Word2vec (Jay Alammar)`
- **Keywords first:** Put the most important keywords at the beginning for quick identification and search

### 3. Logical Grouping, Clear Structure

**Principle:** A good folder structure is itself an efficient index.

- **Keep top-level categories minimal:** Limit top-level folders to 5-7, e.g., `01_Work`, `02_TechStack`, `03_Learning`, `04_Tools`, `05_Life`. Use numeric prefixes to maintain order
- **Don't go too deep:** Try to keep structure depth at 2-3 levels. If a category can be infinitely subdivided, it may need restructuring
- **CleanBook automation:** Automatically groups based on rules defined in your `config.json`

### 4. Regular Review, Dynamic Balance

**Principle:** A bookmark library is a "living" system that needs metabolism.

- **Set reminders:** Spend 15-30 minutes every 2-3 months quickly browsing your bookmarks
- **Delete boldly:** Remove links for finished projects, outdated technologies, or topics you've already mastered
- **Check dead links:** Use browser extensions to find and clean up inaccessible dead links

---

## Configuring CleanBook: Build Your Classification System

### Step 1: Define Your Main Categories

Define top-level categories in `config.json`. Consider these dimensions:

| Dimension | Example Categories |
|-----------|-------------------|
| Work Projects | Workbench, Internal Systems |
| Technical Domains | AI/ML, Programming, Bioinformatics |
| Learning Resources | Tutorials, Courses, Documentation |
| Tool Collections | Online Tools, Productivity Software |
| Personal Interests | Reading, Entertainment, Life |

### Step 2: Define Classification Rules

Add recognition rules for each category:

```json
{
  "category_rules": {
    "Artificial Intelligence": {
      "rules": [
        {
          "match": "domain",
          "keywords": ["openai.com", "huggingface.co", "arxiv.org"],
          "weight": 15
        },
        {
          "match": "title",
          "keywords": ["GPT", "LLM", "neural network", "deep learning"],
          "weight": 10
        }
      ]
    }
  }
}
```

### Step 3: Maintain Controlled Vocabulary

Maintain subject vocabularies in `taxonomy/subjects.yaml`:

```yaml
preferred: "Artificial Intelligence"
variants:
  - "AI"
  - "Machine Learning"
  - "Deep Learning"
```

---

## Recommended Workflows

### Monthly Organization Workflow

1. **Export bookmarks:** Export bookmarks in HTML format from your browser
2. **Place in working directory:** Put the file in your project directory or custom location
3. **One-click execution:**
   ```bash
   cleanbook -i chrome_bookmarks.html -o output
   ```
4. **Analyze new items:** Review the Markdown report in `output/` to identify unclassified bookmarks
5. **Tune configuration:** Update `config.json` when you discover new domain/keyword patterns
6. **Import results:** Import the organized HTML into a clean browser folder

### Incremental Maintenance Workflow

For daily new bookmarks:

1. Use browser plugins or shortcuts for temporary bookmarking
2. Run CleanBook weekly to process new bookmarks
3. Import classified bookmarks into your main bookmark bar
4. Delete temporary bookmarks

---

## Advanced Techniques

### Address Bar Keyword Search

Top-level efficiency technique. Set keywords for frequently used bookmarks:

**Chrome/Edge Setup:**
1. Open Bookmark Manager (Ctrl+Shift+O)
2. Find target bookmark, right-click → Edit
3. Set keyword in "Nickname" field, e.g., `gh`
4. Then type `gh` in address bar and press Enter to navigate

**Recommended Keywords:**
| Keyword | Target | Use Case |
|---------|--------|----------|
| `gh` | GitHub | Quick access to code repositories |
| `doc` | Team docs | Open internal documentation |
| `mail` | Email | Open mail system |

### Using JavaScript Bookmarklets

Save JavaScript code as a bookmark to execute operations on the current page:

```javascript
// Example: Extract all images from page
javascript:(function(){
  var imgs = document.querySelectorAll('img');
  var urls = Array.from(imgs).map(img => img.src);
  prompt('Image URLs', urls.join('\n'));
})()
```

### Browser Built-in Search Tips

- Type `*` + `space` + `keyword` in address bar to search bookmarks only
- This is much faster than searching in history

---

## Classification Design Recommendations

### Two-Level Faceted Classification

CleanBook recommends using `subject -> resource_type` two-level structure:

```
Artificial Intelligence/    ← subject
├── documentation/         ← resource_type
├── code_repository/
├── video/
└── article/
```

### Common Resource Type Categories

| Type | Description | Examples |
|------|-------------|----------|
| `code_repository` | Code repositories | GitHub, GitLab |
| `documentation` | Official documentation | API docs, Wiki |
| `article` | Articles & blogs | Tech blogs, news |
| `video` | Video resources | YouTube, Bilibili |
| `tool` | Online tools | Online editors, calculators |
| `course` | Courses & tutorials | Online courses, MOOC |

---

## Conclusion

An excellent bookmark library is an extension of your personal digital identity and knowledge system. It should be like a well-trained librarian, always ready to quickly and accurately serve you the information you need.

We hope these best practices, combined with the powerful CleanBook tool, will help you say goodbye to bookmark chaos forever and enjoy an efficient, clean digital life.
