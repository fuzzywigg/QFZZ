"""PersonalizedDJ empty candidate tracks prompt copy edge."""

from qfzz.dj.personalized_dj import PersonalizedDJ
from qfzz.dj.profiles import UserProfile


def test_build_llm_recommendation_prompt_empty_tracks():
    dj = PersonalizedDJ(enable_ai_dj=False)
    profile = UserProfile(user_id="u-empty")
    prompt = dj._build_llm_recommendation_prompt(
        message="  ",
        user_id="u-empty",
        profile=profile,
        tracks=[],
    )
    assert "No tracks currently available." in prompt
    assert "Recommend tracks for my current vibe." in prompt
    assert "mixed" in prompt  # no genres → mixed
