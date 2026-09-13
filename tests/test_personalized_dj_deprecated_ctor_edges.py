"""PersonalizedDJ deprecated llm_model/api_key ctor warning edges."""

import logging

from qfzz.dj.personalized_dj import PersonalizedDJ


def test_deprecated_ctor_params_log_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="qfzz.dj.personalized_dj"):
        dj = PersonalizedDJ(
            llm_model="other-model",
            api_key="sk-test",
            enable_ai_dj=False,
        )
    assert dj is not None
    assert any("deprecated" in r.message.lower() for r in caplog.records)


def test_default_ctor_skips_deprecated_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="qfzz.dj.personalized_dj"):
        PersonalizedDJ(enable_ai_dj=False)
    assert not any("deprecated" in r.message.lower() for r in caplog.records)
