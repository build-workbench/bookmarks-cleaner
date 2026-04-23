# Capability: Plugin Architecture

## Overview

Hot-pluggable plugin system for classifiers, exporters, and feature extractors with runtime registration, enable/disable, and priority-based execution.

## ADDED Requirements

### Requirement: Plugin Registration
Register and manage classifier plugins dynamically.

#### Scenario: Register Valid Plugin
- **GIVEN** a ClassifierPlugin implementing required interface
- **WHEN** registered with PluginRegistry
- **THEN** the plugin is immediately available for classification
- **AND** the plugin is in enabled state

#### Scenario: Validate Plugin Interface
- **GIVEN** a plugin candidate
- **WHEN** validation is performed
- **THEN** required methods (classify, metadata) are verified
- **AND** invalid plugins are rejected with descriptive error

### Requirement: Plugin Lifecycle
Manage plugin enable/disable at runtime.

#### Scenario: Disable Plugin
- **GIVEN** an enabled plugin
- **WHEN** disable() is called
- **THEN** the plugin is excluded from classification
- **AND** no system restart is required

#### Scenario: Enable Plugin
- **GIVEN** a disabled plugin
- **WHEN** enable() is called
- **THEN** the plugin is included in classification
- **AND** no system restart is required

### Requirement: Priority-Based Execution
Execute plugins in configured priority order.

#### Scenario: Ordered Execution
- **GIVEN** multiple plugins with different priorities
- **WHEN** classification is invoked
- **THEN** plugins execute in priority order (highest first)
- **AND** execution order is deterministic

### Requirement: Plugin Failure Isolation
Isolate plugin failures from affecting other plugins.

#### Scenario: Failure Isolation
- **GIVEN** a plugin that raises an exception
- **WHEN** the pipeline executes
- **THEN** the exception is logged
- **AND** remaining plugins continue execution
- **AND** a valid result is returned

## Correctness Properties

1. **Plugin Registration Consistency**: Registered plugins are immediately available
2. **Plugin Invocation Order**: Execution follows configured priority
3. **Plugin Failure Isolation**: One failure doesn't cascade to others
4. **Runtime Plugin Toggle**: Enable/disable without restart

## Technical Notes

### Plugin Interface

```python
class ClassifierPlugin(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata (name, version, capabilities)."""
        pass

    @abstractmethod
    def classify(self, features: BookmarkFeatures) -> ClassificationResult:
        """Classify bookmark and return result with confidence."""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass
```

### Configuration

```json
{
  "plugins": {
    "rule_classifier": {
      "enabled": true,
      "priority": 100
    },
    "ml_classifier": {
      "enabled": true,
      "priority": 50
    },
    "embedding_classifier": {
      "enabled": true,
      "priority": 30
    }
  }
}
```

## References

- Implementation: `src/plugins/`
- Tests: `tests/test_plugin_registry_properties.py`, `tests/test_pipeline_properties.py`
