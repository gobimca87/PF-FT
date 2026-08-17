from pf_ft_ai.configuration.hashing import compute_configuration_hash


def test_should_produce_stable_hash_for_equivalent_input_regardless_of_key_order() -> None:
    first = compute_configuration_hash({"a": 1, "b": 2})
    second = compute_configuration_hash({"b": 2, "a": 1})

    assert first == second
    assert len(first) == 64


def test_should_produce_different_hash_when_configuration_drifts() -> None:
    baseline = compute_configuration_hash({"runtime": {"request_timeout_seconds": 60}})
    drifted = compute_configuration_hash({"runtime": {"request_timeout_seconds": 45}})

    assert baseline != drifted
