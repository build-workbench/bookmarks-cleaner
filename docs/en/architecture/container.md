# DI Container

Bookmarks Cleaner uses **ProcessorContainer** as a dependency injection container, centralizing component lifecycle and dependency management.

## Design Philosophy

Adopting **IoC (Inversion of Control)** pattern with lightweight `dataclass` implementation:

- **Lazy creation**: Components initialized on demand
- **Dependency injection**: Decoupled components for testing
- **Chain replacement**: Runtime component substitution

## Container Structure

```python
@dataclasses.dataclass
class ProcessorContainer:
    """Processor component container"""
    
    # Configuration
    config: Dict[str, Any]
    config_path: Optional[str] = None
    max_workers: int = 4
    
    # Injectable components (lazy)
    _coordinator: Optional["ICoordinator"] = None
    _health_checker: Optional["IHealthChecker"] = None
    _classifier: Optional[Any] = None
    
    @property
    def coordinator(self) -> "ICoordinator":
        """Get coordinator (lazy creation)"""
        if self._coordinator is None:
            from src.pipelines.coordinator import BookmarkProcessorCoordinator
            self._coordinator = BookmarkProcessorCoordinator(
                config=self.config,
                classifier=self.classifier,
            )
        return self._coordinator
```

## Usage Examples

### Default Creation

```python
container = ProcessorContainer(
    config={"category_rules": {...}},
    config_path="config.json",
)
stats = container.coordinator.process_files(["bookmarks.html"])
```

### Dependency Injection (Testing)

```python
from unittest.mock import Mock

mock_coordinator = Mock()
container = ProcessorContainer(
    config={},
    _coordinator=mock_coordinator,
)
```

## Related Docs

- [Pipeline Architecture](/en/architecture/pipeline) - Pipeline design
- [Protocols](/en/architecture/protocols) - Interface definitions
