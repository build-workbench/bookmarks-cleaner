# Related Projects

This page is not a generic link dump. It frames adjacent projects and enabling stacks in terms that matter to Bookmarks Cleaner: runtime model, privacy boundary, extensibility, and intelligence strategy.

## Comparative Frame

| Project | Runtime model | Data boundary | Intelligence model | Operational burden | Why it matters here |
|---------|---------------|---------------|--------------------|--------------------|---------------------|
| Bookmarks Cleaner | Local CLI | Local files stay local | Rules-first with hybrid fusion | Very low | The baseline being justified |
| linkding | Self-hosted web app | User-controlled server | Tagging and retrieval, not classifier fusion | Medium | Useful comparison for ownership without local-first execution |
| Shaarli | Lightweight self-hosted web app | User-controlled server | Manual organization | Low to medium | Good contrast for minimal self-hosted bookmarking |
| Browser-native exports | Browser feature, not a system | Fully local | No intelligence layer | Very low | Establishes the lower bound: portability without organization intelligence |

## Adjacent Bookmark Systems

### linkding

- **Repository**: [sissbruecker/linkding](https://github.com/sissbruecker/linkding)
- **Why it matters**: strong self-hosted bookmark ownership model, but a different product shape. It solves persistence and retrieval better than local cleanup and classification.
- **Main contrast**: linkding turns bookmark management into an always-on service; Bookmarks Cleaner keeps it as an episodic local processing task.

### Shaarli

- **Repository**: [shaarli/Shaarli](https://github.com/shaarli/Shaarli)
- **Why it matters**: demonstrates how far a personal bookmarking tool can go with manual curation and a light runtime.
- **Main contrast**: Shaarli optimizes for durable storage and lightweight hosting, not automated classification or whitepaper-style runtime decomposition.

## Enabling Technical Stacks

### scikit-learn

- **Repository**: [scikit-learn/scikit-learn](https://github.com/scikit-learn/scikit-learn)
- **Role in this project**: represents the mature ML substrate used for practical local classification work.

### Sentence Transformers

- **Repository**: [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- **Role in this project**: makes semantic similarity and embedding-based enrichment feasible inside the local runtime.

### Ollama

- **Repository**: [ollama/ollama](https://github.com/ollama/ollama)
- **Role in this project**: illustrates how optional LLM support can stay compatible with the local-first trust boundary when the user chooses to run a local model host.

## Interpretation

The comparison worth remembering is not "which tool has more features", but "which problem shape each tool accepts":

- self-hosted bookmark systems optimize for persistent access and sharing;
- browser-native export flows optimize for portability only;
- Bookmarks Cleaner optimizes for episodic local cleanup and classification with explicit architecture boundaries.
