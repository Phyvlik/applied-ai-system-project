from src.guardrails import validate_user_prefs, check_output_confidence


def test_valid_prefs_returns_no_errors():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    assert validate_user_prefs(prefs) == []


def test_unknown_genre_returns_error():
    prefs = {"genre": "polka", "mood": "happy", "energy": 0.5}
    errors = validate_user_prefs(prefs)
    assert len(errors) == 1
    assert "polka" in errors[0]


def test_unknown_mood_returns_error():
    prefs = {"genre": "pop", "mood": "melancholy", "energy": 0.5}
    errors = validate_user_prefs(prefs)
    assert len(errors) == 1
    assert "melancholy" in errors[0]


def test_energy_out_of_range_returns_error():
    prefs = {"genre": "pop", "mood": "happy", "energy": 1.5}
    errors = validate_user_prefs(prefs)
    assert len(errors) == 1
    assert "1.5" in errors[0]


def test_multiple_errors_returned_together():
    prefs = {"genre": "polka", "mood": "melancholy", "energy": 2.0}
    errors = validate_user_prefs(prefs)
    assert len(errors) == 3


def test_empty_genre_and_mood_are_allowed():
    prefs = {"genre": "", "mood": "", "energy": 0.5}
    assert validate_user_prefs(prefs) == []


def test_confidence_warning_when_score_is_low():
    fake_recs = [({}, 1.5, ""), ({}, 1.0, ""), ({}, 0.5, "")]
    warning = check_output_confidence(fake_recs)
    assert warning is not None
    assert "Low confidence" in warning


def test_no_confidence_warning_when_score_is_high():
    fake_recs = [({}, 5.0, ""), ({}, 4.0, ""), ({}, 3.0, "")]
    warning = check_output_confidence(fake_recs)
    assert warning is None


def test_confidence_check_with_empty_recommendations():
    warning = check_output_confidence([])
    assert warning is not None
