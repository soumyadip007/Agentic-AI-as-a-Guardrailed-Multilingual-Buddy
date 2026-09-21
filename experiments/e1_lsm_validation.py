"""E1-style LSM policy compliance smoke checks."""

from __future__ import annotations

from tl_guard.config_loader import list_courses, load_lsm
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier


def main() -> None:
    total = 0
    ok = 0
    for course in list_courses():
        lsm = load_lsm(course["course_id"])
        engine = LSMEngine(lsm)
        for lang in lsm.languages:
            for tier in ScaffoldTier:
                total += 1
                authorized = engine.authorize(lang, tier)
                max_t = engine.max_tier(lang)
                # Consistency: if authorized, tier rank <= max
                from tl_guard.models import TIER_RANK

                if authorized:
                    assert TIER_RANK[tier] <= TIER_RANK[max_t]
                # clamp never exceeds max
                clamped = engine.clamp(lang, tier)
                assert TIER_RANK[clamped] <= TIER_RANK[max_t]
                ok += 1
    print(f"LSM consistency checks: {ok}/{total} passed ({100 * ok / total:.1f}%)")


if __name__ == "__main__":
    main()
