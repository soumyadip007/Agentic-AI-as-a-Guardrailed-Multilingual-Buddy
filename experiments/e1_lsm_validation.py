"""E1-style Scaffold Map compliance smoke checks."""

from __future__ import annotations

from tl_guard.config_loader import list_courses, load_scaffold_map
from tl_guard.decide.lsm_engine import LSMEngine
from tl_guard.models import ScaffoldTier


def main() -> None:
    total = 0
    ok = 0
    for course in list_courses():
        cfg = load_scaffold_map(course["course_id"])
        engine = LSMEngine(cfg)
        for lang in cfg.languages:
            for tier in ScaffoldTier:
                total += 1
                authorized = engine.authorize(lang, tier)
                max_t = engine.max_tier(lang)
                from tl_guard.models import TIER_RANK

                if authorized:
                    assert TIER_RANK[tier] <= TIER_RANK[max_t]
                clamped = engine.clamp(lang, tier)
                assert TIER_RANK[clamped] <= TIER_RANK[max_t]
                ok += 1
    print(f"Scaffold Map consistency checks: {ok}/{total} passed ({100 * ok / total:.1f}%)")


if __name__ == "__main__":
    main()
