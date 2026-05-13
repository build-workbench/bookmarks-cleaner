# Capability: Taxonomy Unified

## Overview

统一的分类体系服务，合并 TaxonomyService（CRUD）和 TaxonomyStandardizer（标准化）的职责。提供分类体系的完整生命周期管理。

## Requirements

### Requirement: CRUD operations for taxonomy
管理分类体系的增删改查。

#### Scenario: List all subjects
- **GIVEN** a loaded taxonomy
- **WHEN** taxonomy.list_subjects() is called
- **THEN** all subject categories are returned

#### Scenario: Add new subject
- **GIVEN** a new subject name
- **WHEN** taxonomy.add_subject(name, variants) is called
- **THEN** subject is added to taxonomy and file is saved

#### Scenario: Rename subject
- **GIVEN** an existing subject
- **WHEN** taxonomy.rename_subject(old_name, new_name) is called
- **THEN** subject is renamed and all references updated

### Requirement: Normalization functions
提供分类名称标准化功能。

#### Scenario: Normalize subject name
- **GIVEN** a subject name or variant
- **WHEN** taxonomy.normalize_subject(name) is called
- **THEN** the preferred form is returned

#### Scenario: Normalize resource type
- **GIVEN** a resource type or variant
- **WHEN** taxonomy.normalize_resource_type(type) is called
- **THEN** the canonical form is returned

### Requirement: Derive subject and type from category
从分类字符串推导主题和资源类型。

#### Scenario: Parse category string
- **GIVEN** category "技术/文档"
- **WHEN** taxonomy.derive_from_category(category) is called
- **THEN** returns (subject="技术", resource_type="文档")

### Requirement: Single YAML loading
只加载一次 subjects.yaml 文件。

#### Scenario: Cache taxonomy data
- **GIVEN** multiple calls to taxonomy methods
- **WHEN** taxonomy is initialized
- **THEN** subjects.yaml is loaded only once

### Requirement: Migration from split classes
提供从旧类迁移的兼容层。

#### Scenario: TaxonomyStandardizer behavior preserved
- **GIVEN** existing code using TaxonomyStandardizer
- **WHEN** migration is complete
- **THEN** same normalization behavior through TaxonomyService

## Correctness Properties

1. **Single Load**: Taxonomy YAML loaded once per instance
2. **Consistent Normalization**: Same input always produces same output
3. **Variant Resolution**: All variants resolve to preferred form
4. **CRUD Persistence**: Changes are persisted to YAML file
