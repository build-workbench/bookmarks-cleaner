import importlib
from types import SimpleNamespace

import pytest


@pytest.mark.parametrize(
    "deprecated_module",
    [
        "src.url_analyzer",
        "src.utils.url",
        "src.taxonomy_standardizer",
        "src.user_profiler",
    ],
)
def test_duplicate_modules_are_not_importable(deprecated_module):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(deprecated_module)


def test_url_analyzer_survives_at_engine_seam():
    from src.engines.url import URLAnalyzer

    analysis = URLAnalyzer().analyze("https://github.com/octocat/hello-world")

    assert analysis.site_type == "github"
    assert analysis.content_type == "repo"
    assert analysis.repo_owner == "octocat"
    assert analysis.repo_name == "hello-world"


def test_taxonomy_standardizer_normalizes_variants_at_utils_seam(tmp_path):
    from src.utils.standardizer import TaxonomyStandardizer

    subjects_file = tmp_path / "subjects.yaml"
    subjects_file.write_text(
        "subjects:\n" "  - preferred: Python\n" "    variants:\n" "      - py\n",
        encoding="utf-8",
    )
    resource_types_file = tmp_path / "resource_types.yaml"
    resource_types_file.write_text(
        "resource_types:\n" "  documentation:\n" "    variants:\n" "      - docs\n",
        encoding="utf-8",
    )

    standardizer = TaxonomyStandardizer(
        {
            "taxonomy": {
                "subjects_file": str(subjects_file),
                "resource_types_file": str(resource_types_file),
            }
        }
    )

    assert standardizer.normalize_subject("!py") == "Python"
    assert standardizer.normalize_resource_type("*docs") == "documentation"


def test_bookmark_organizer_uses_taxonomy_standardizer_surviving_contract(tmp_path):
    from src.processing.bookmark_organizer import BookmarkOrganizer
    from src.utils.standardizer import TaxonomyStandardizer

    subjects_file = tmp_path / "subjects.yaml"
    subjects_file.write_text(
        "subjects:\n" "  - preferred: Python\n" "    variants:\n" "      - py\n",
        encoding="utf-8",
    )
    resource_types_file = tmp_path / "resource_types.yaml"
    resource_types_file.write_text(
        "resource_types:\n" "  documentation:\n" "    variants:\n" "      - docs\n",
        encoding="utf-8",
    )

    standardizer = TaxonomyStandardizer(
        {
            "taxonomy": {
                "subjects_file": str(subjects_file),
                "resource_types_file": str(resource_types_file),
            }
        }
    )
    organizer = BookmarkOrganizer()

    organized = organizer.organize(
        [{"title": "Guide", "subject": "!py", "resource_type": "*docs"}],
        taxonomy_standardizer=standardizer,
    )

    assert list(organized) == ["Python"]
    assert list(organized["Python"]) == ["documentation"]


def test_user_profiler_classifies_from_saved_preferences(tmp_path):
    from src.utils.profiler import UserProfiler

    profile_file = tmp_path / "profile.json"
    profiler = UserProfiler(profile_file=str(profile_file))
    features = SimpleNamespace(
        url="https://github.com/octocat/hello-world",
        title="Python project guide",
        domain="github.com",
    )

    profiler.update_preferences(features, "编程/开发", confidence=1.0)
    reloaded = UserProfiler(profile_file=str(profile_file))

    result = reloaded.classify(features)

    assert result is not None
    assert result["category"] == "编程/开发"
    assert result["method"] == "user_profiler"
    assert result["confidence"] >= 0.2
