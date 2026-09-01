from pff_fa_ai.memory.states import MemoryCategory


def test_should_define_exactly_the_ten_documented_memory_categories() -> None:
    assert len(MemoryCategory) == 10
    assert {category.value for category in MemoryCategory} == {
        "CONVERSATION",
        "SESSION",
        "WORKING",
        "WORKFLOW",
        "AGENT_RUN",
        "USER_PREFERENCE",
        "ORGANIZATIONAL_CONTEXT",
        "ERC_REFERENCE",
        "DECISION",
        "SUMMARY",
    }
