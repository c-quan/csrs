from calsim_scenario_server.models import MetricValueModel

EXPECTED_COLUMNS = {
    "path_id": int,
    "run_id": int,
    "metric_id": int,
    "index": int,
    "units": str,
    "value": float,
}


def test_columns():
    columns = [c.key for c in MetricValueModel.__table__.columns]
    missing = list()
    for c in EXPECTED_COLUMNS:
        if c not in columns:
            missing.append(c)
    assert len(missing) == 0, f"model is missing expected columns: {missing}"
    extra = list()
    for c in columns:
        if c not in EXPECTED_COLUMNS:
            extra.append(c)
    assert len(extra) == 0, f"model has unexpected columns: {extra}"


def test_column_types():
    columns = {c.key: c.type.python_type for c in MetricValueModel.__table__.columns}
    bad_types = list()
    for c in EXPECTED_COLUMNS:
        if EXPECTED_COLUMNS[c] != EXPECTED_COLUMNS[c]:
            bad_types.append((c, columns[c]))
    assert len(bad_types) == 0, f"bad types: {bad_types}"
