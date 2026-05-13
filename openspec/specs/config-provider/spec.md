# Capability: Config Provider

## Overview

统一的配置加载入口，消除两个配置入口（EnhancedConfigManager 和 load_json_config）。提供验证、环境变量展开、文件监控等完整功能。

## Requirements

### Requirement: Single entry point for configuration
所有组件通过 ConfigProvider 获取配置。

#### Scenario: Load configuration from file
- **GIVEN** a valid config.json path
- **WHEN** ConfigProvider(path) is initialized
- **THEN** configuration is loaded and validated

#### Scenario: Get value by dot notation
- **GIVEN** configuration with nested structure
- **WHEN** provider.get("ai_settings.confidence_threshold", 0.7) is called
- **THEN** the nested value or default is returned

### Requirement: Configuration validation
配置加载时进行验证。

#### Scenario: Invalid configuration rejected
- **GIVEN** a config with missing required fields
- **WHEN** ConfigProvider tries to load it
- **THEN** a ValidationError is raised with clear message

#### Scenario: Valid configuration accepted
- **GIVEN** a valid config
- **WHEN** ConfigProvider loads it
- **THEN** no exception is raised

### Requirement: Environment variable expansion
支持环境变量展开。

#### Scenario: Expand env vars in config
- **GIVEN** config value "${HOME}/bookmarks"
- **WHEN** ConfigProvider loads the config
- **THEN** value is expanded to actual home directory path

### Requirement: Optional file monitoring
可选的配置文件变更监控。

#### Scenario: Monitor config changes
- **GIVEN** file_monitoring=True
- **WHEN** config file is modified on disk
- **THEN** configuration is reloaded automatically

### Requirement: Backward compatibility
保持与现有 load_json_config 的兼容性。

#### Scenario: Existing code path works
- **GIVEN** code using load_json_config()
- **WHEN** migration is complete
- **THEN** same behavior is preserved through ConfigProvider

## Correctness Properties

1. **Single Source of Truth**: Only one configuration loading implementation
2. **Validation Always On**: Configuration is validated before use
3. **Immutable After Load**: Configuration does not change unless file monitoring is enabled
4. **Thread Safe**: Concurrent reads are safe
