# Test Datasets

Golden evaluation datasets (doc 21) live at [`config/evaluation/golden/`](../../config/evaluation/golden/)
— see that directory's own README for why it currently ships empty and how a real case
gets added. They are not duplicated here: `config/` is the single canonical location a
running deployment reads from (`pf_ft_ai.evaluation.dataset.load_golden_dataset()`), and
`tests/regression/test_golden_dataset_regression.py` reads from that same real path so
test behavior and production behavior never diverge.

This directory is reserved for datasets that are test-only and never shipped as
deployable configuration — e.g. large-scale synthetic performance corpora or adversarial
payload sets too large to inline in a test file — once those exist.
