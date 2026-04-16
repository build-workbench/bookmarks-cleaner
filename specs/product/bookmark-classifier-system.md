# Product Requirements: CleanBook Intelligent Bookmark Classification System

## Introduction

This document defines the product requirements for the CleanBook intelligent bookmark classification system. The system uses AI technology to automatically analyze, classify, and organize browser bookmarks.

## System Overview

The CleanBook system provides:
- **Rule-based Classification**: Fast classification based on keyword matching
- **Machine Learning Classification**: Intelligent classification using scikit-learn
- **AI-powered Classification**: Ensemble system coordinating multiple classification methods
- **Batch Processing**: Bulk processing of bookmark files
- **CLI Interface**: User-friendly command-line interface

## User Stories

### US-1: Bookmark Processing
**As a** user, **I want** to process my browser bookmark HTML files, **so that** my bookmarks are automatically organized into meaningful categories.

**Acceptance Criteria:**
- System accepts HTML bookmark file as input
- System extracts bookmark titles, URLs, and metadata
- System processes bookmarks in parallel using multi-threading
- System outputs results in HTML, JSON, and Markdown formats

### US-2: Classification Configuration
**As a** user, **I want** to customize classification rules and categories, **so that** the classification matches my personal organization style.

**Acceptance Criteria:**
- Configuration file (config.json) defines category rules
- Users can add/modify/remove classification rules
- Category hierarchy supports parent-child relationships
- Title cleaning rules normalize bookmark titles

### US-3: Performance Optimization
**As a** user, **I want** fast bookmark processing with intelligent caching, **so that** repeated processing is efficient.

**Acceptance Criteria:**
- LRU cache for classification results
- Multi-threaded parallel processing
- Batch processing mechanism
- Lazy initialization of components

### US-4: Output Formats
**As a** user, **I want** multiple output formats for my classified bookmarks, **so that** I can use them in different contexts.

**Acceptance Criteria:**
- HTML output importable to browsers
- JSON output with detailed classification metadata
- Markdown output as readable classification report
- Statistics summary in all output formats

## Glossary

- **RuleEngine**: Keyword-based fast classification engine
- **MLClassifier**: Machine learning classifier using scikit-learn
- **AIClassifier**: AI main classifier coordinating multiple methods
- **BookmarkProcessor**: Batch bookmark processing processor
- **CLIInterface**: Command-line user interface
- **EnhancedClassifier**: Main classifier integrating rule engine, ML classifier, LLM classifier

## Performance Requirements

- **Processing Speed**: Handle typical bookmark files (100-1000 bookmarks) within seconds
- **Memory Usage**: Efficient memory usage with LRU caching
- **Scalability**: Support processing large bookmark files via configurable thread count
- **Accuracy**: High classification accuracy through ensemble methods

## Technical Constraints

- Follow PEP8 Python coding standards
- Use type hints throughout codebase
- Complete docstrings for functions and classes
- Configuration in JSON format
- Machine learning features require additional dependencies (scikit-learn, jieba, etc.)
