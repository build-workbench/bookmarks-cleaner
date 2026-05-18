# Evolution

This page explains the architectural story that the rest of the site assumes: Bookmarks Cleaner did not begin as a polished pipeline system. The current runtime emerged because earlier code shapes made change too expensive.

## Phase 1, single-purpose script

The earliest version answered one narrow question: clean an exported `bookmarks.html` file and collapse obvious duplicates. That version was useful precisely because it was small, but it also had no named boundaries. Parsing, deduplication, classification, and export logic all lived in one mental unit.

## Phase 2, toolification without strong boundaries

As configuration, logging, and smarter classification rules accumulated, the script became a tool but not yet a system. More capabilities existed, yet they were still threaded through shared state and broad utility functions. Change became possible, but locality of change remained poor.

## Phase 3, the god-class plateau

The repository then paid the classic price of growth without decomposition: too much logic collected inside `BookmarkProcessor`. The façade stopped being a façade and became the system itself. This was the pivotal moment, because it made the next step obvious:

- every new classifier touched too many call sites;
- tests had to route through too much unrelated behavior;
- understanding one feature required loading the entire runtime into working memory.

## Phase 4, façade plus pipeline

The current design reorganized the runtime around smaller, named units:

| Boundary | Why it was extracted |
|----------|----------------------|
| Container | to make dependency wiring explicit |
| Coordinator | to separate sequencing from public API shape |
| Pipelines | to isolate stage-specific behavior |
| Protocols and services | to reduce coupling between changing components |

The architectural win was not aesthetic, it was operational: changes became more local, tests became more targeted, and documentation could finally describe the system without hand-waving over a giant implementation blob.

## What the site now claims because of that evolution

The rest of this documentation site depends on those changes being real:

- the [whitepaper](/en/whitepaper) can describe a runtime boundary because one now exists;
- the [pipeline page](/en/architecture/pipeline) can name stages because the stages are structurally real;
- the [related projects analysis](/en/resources/related-projects) can compare system shapes instead of comparing feature bullets.

That is why the evolution story belongs in the docs. It is not repository nostalgia, it is evidence for the current architecture.
