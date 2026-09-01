from pff_fa_ai.cache.states import CacheCategory


def test_should_define_exactly_the_ten_documented_cache_categories() -> None:
    assert len(CacheCategory) == 10
    assert {category.value for category in CacheCategory} == {
        "ENTERPRISE_API_RESPONSE",
        "REFERENCE_DATA",
        "CONFIGURATION",
        "PROMPT",
        "MODEL_METADATA",
        "RAG_RETRIEVAL",
        "EMBEDDING",
        "SESSION",
        "CONTEXT_PROJECTION",
        "PORTAL_LINK",
    }
