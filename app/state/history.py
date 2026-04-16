"""Completed-match archive schema and stats read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TypedDict

from app.state.models import SECRET_OP_CHOICES, GameState

HISTORY_SCHEMA_VERSION = 1
ARCHIVE_SCHEMA_VERSION = 1
DRAW_OUTCOME = "draw"
WINNER_CHOICES = ("player_one", "player_two", DRAW_OUTCOME)
PLAYER_SLOTS = ("player_one", "player_two")
COMBINED_SCOPE = "combined"
PRIMARY_OP_ORDER = {op_key: index for index, op_key in enumerate(SECRET_OP_CHOICES)}
OP_BUCKETS = {
    "tac_op": {"label": "Tac Op", "score_field": "tactical_vp"},
    "kill_op": {"label": "Kill Op", "score_field": "kill_vp"},
    "crit_op": {"label": "Crit Op", "score_field": "main_mission_vp"},
}
MOST_SUCCESSFUL_TIEBREAK = (
    "win_percentage",
    "wins",
    "average_selected_vp",
    "average_bonus_vp",
    "picks",
    "op_order",
)


def _now_utc_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _coerce_timestamp(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "1970-01-01T00:00:00Z"


def _coerce_winner(value: object) -> str:
    if isinstance(value, str) and value in WINNER_CHOICES:
        return value
    raise ValueError(f"winner must be one of {WINNER_CHOICES}, got {value!r}")


def _determine_winner(final_scores: dict[str, int]) -> str:
    p1_total = final_scores["player_one"]
    p2_total = final_scores["player_two"]
    if p1_total > p2_total:
        return "player_one"
    if p2_total > p1_total:
        return "player_two"
    return DRAW_OUTCOME


def _coerce_int(value: object, field_name: str) -> int:
    try:
        coerced: int = int(value)
        return coerced
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


@dataclass(slots=True)
class CompletedMatchArchive:
    """Archive record for one completed match."""

    archive_schema_version: int
    archived_at: str
    winner: str
    final_scores: dict[str, int]
    game_snapshot: dict[str, object]

    def __post_init__(self) -> None:
        if self.archive_schema_version != ARCHIVE_SCHEMA_VERSION:
            raise ValueError(
                "unsupported archive_schema_version: "
                f"{self.archive_schema_version}; expected {ARCHIVE_SCHEMA_VERSION}"
            )

        if self.winner not in WINNER_CHOICES:
            raise ValueError(
                f"winner must be one of {WINNER_CHOICES}, got {self.winner!r}"
            )

        expected_keys = {"player_one", "player_two"}
        if set(self.final_scores.keys()) != expected_keys:
            raise ValueError("final_scores must contain player_one and player_two")

        for key in expected_keys:
            self.final_scores[key] = _coerce_int(self.final_scores[key], key)

        if not isinstance(self.game_snapshot, dict):
            raise ValueError("game_snapshot must be a dictionary")

        # Validate and normalize to the canonical active-game schema.
        validated = GameState.from_dict(self.game_snapshot)
        self.game_snapshot = validated.to_dict()

    @classmethod
    def from_game_state(
        cls,
        game_state: GameState,
        *,
        archived_at: str | None = None,
    ) -> CompletedMatchArchive:
        final_scores = game_state.final_scores()
        return cls(
            archive_schema_version=ARCHIVE_SCHEMA_VERSION,
            archived_at=archived_at or _now_utc_iso(),
            winner=_determine_winner(final_scores),
            final_scores=final_scores,
            game_snapshot=game_state.to_dict(),
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CompletedMatchArchive:
        if "game_snapshot" not in data:
            # Legacy input support: allow bare GameState payload entries.
            state = GameState.from_dict(data)
            return cls.from_game_state(state, archived_at="1970-01-01T00:00:00Z")

        raw_version = data.get("archive_schema_version", ARCHIVE_SCHEMA_VERSION)
        raw_final_scores = data.get("final_scores")
        if not isinstance(raw_final_scores, dict):
            raise ValueError("final_scores must be a dictionary")

        game_snapshot = data["game_snapshot"]
        if not isinstance(game_snapshot, dict):
            raise ValueError("game_snapshot must be a dictionary")

        return cls(
            archive_schema_version=_coerce_int(
                raw_version,
                "archive_schema_version",
            ),
            archived_at=_coerce_timestamp(data.get("archived_at")),
            winner=_coerce_winner(data.get("winner")),
            final_scores={
                "player_one": _coerce_int(
                    raw_final_scores.get("player_one"),
                    "player_one",
                ),
                "player_two": _coerce_int(
                    raw_final_scores.get("player_two"),
                    "player_two",
                ),
            },
            game_snapshot=game_snapshot,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "archive_schema_version": self.archive_schema_version,
            "archived_at": self.archived_at,
            "winner": self.winner,
            "final_scores": {
                "player_one": self.final_scores["player_one"],
                "player_two": self.final_scores["player_two"],
            },
            "game_snapshot": self.game_snapshot,
        }


def migrate_history_payload(payload: object) -> dict[str, object]:
    """Migrate a decoded JSON payload into canonical history schema v1."""
    if payload is None:
        return {
            "schema_version": HISTORY_SCHEMA_VERSION,
            "matches": [],
        }

    if isinstance(payload, list):
        raw_matches = payload
    elif isinstance(payload, dict):
        raw_version = payload.get("schema_version", HISTORY_SCHEMA_VERSION)
        version = _coerce_int(raw_version, "schema_version")
        if version != HISTORY_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported history schema_version: {version}; "
                f"expected {HISTORY_SCHEMA_VERSION}"
            )
        raw_matches = payload.get("matches", [])
    else:
        raise ValueError("history payload must be a JSON object or list")

    if not isinstance(raw_matches, list):
        raise ValueError("history matches must be a list")

    migrated_matches: list[dict[str, object]] = []
    for index, raw_match in enumerate(raw_matches):
        if not isinstance(raw_match, dict):
            raise ValueError(f"history match at index {index} must be a dictionary")
        archive = CompletedMatchArchive.from_dict(raw_match)
        migrated_matches.append(archive.to_dict())

    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "matches": migrated_matches,
    }


def load_archives_from_payload(payload: object) -> list[CompletedMatchArchive]:
    migrated = migrate_history_payload(payload)
    matches = migrated["matches"]
    assert isinstance(matches, list)
    return [CompletedMatchArchive.from_dict(match) for match in matches]


def _percentage(wins: int, matches: int) -> float:
    if matches == 0:
        return 0.0
    return round((wins / matches) * 100, 2)


def _average(total: int, count: int) -> float:
    if count == 0:
        return 0.0
    return round(total / count, 2)


def _init_outcome_accumulator() -> dict[str, int]:
    return {"wins": 0, "draws": 0, "losses": 0, "matches": 0}


def _record_outcome(
    accumulator: dict[str, int],
    *,
    winner: str,
    slot: str,
) -> None:
    accumulator["matches"] += 1
    if winner == DRAW_OUTCOME:
        accumulator["draws"] += 1
    elif winner == slot:
        accumulator["wins"] += 1
    else:
        accumulator["losses"] += 1


def _build_team_stats(
    team_accumulators: dict[str, dict[str, dict[str, int]]],
) -> dict[str, dict[str, object]]:
    team_stats: dict[str, dict[str, object]] = {}
    for team_name, stats in sorted(team_accumulators.items()):
        team_stats[team_name] = {
            "overall": {
                "wins": stats["overall"]["wins"],
                "draws": stats["overall"]["draws"],
                "losses": stats["overall"]["losses"],
                "matches": stats["overall"]["matches"],
                "win_percentage": _percentage(
                    stats["overall"]["wins"],
                    stats["overall"]["matches"],
                ),
            },
            "player_one": {
                "wins": stats["player_one"]["wins"],
                "draws": stats["player_one"]["draws"],
                "losses": stats["player_one"]["losses"],
                "matches": stats["player_one"]["matches"],
                "win_percentage": _percentage(
                    stats["player_one"]["wins"],
                    stats["player_one"]["matches"],
                ),
            },
            "player_two": {
                "wins": stats["player_two"]["wins"],
                "draws": stats["player_two"]["draws"],
                "losses": stats["player_two"]["losses"],
                "matches": stats["player_two"]["matches"],
                "win_percentage": _percentage(
                    stats["player_two"]["wins"],
                    stats["player_two"]["matches"],
                ),
            },
        }
    return team_stats


class _PrimaryOpScopeAccum(TypedDict):
    player_entries: int
    missing_primary_ops: int
    ops: dict[str, dict[str, int]]


def _build_primary_ops_summary(
    primary_op_accumulators: dict[str, _PrimaryOpScopeAccum],
    *,
    total_matches: int,
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for scope, scope_stats in primary_op_accumulators.items():
        raw_ops = scope_stats["ops"]
        assert isinstance(raw_ops, dict)

        ops: dict[str, dict[str, object]] = {}
        best_score: tuple[float, int, float, float, int] | None = None
        tied_ops: list[str] = []

        for op_key in SECRET_OP_CHOICES:
            op_stats = raw_ops[op_key]
            assert isinstance(op_stats, dict)
            picks = op_stats["picks"]
            wins = op_stats["wins"]
            draws = op_stats["draws"]
            losses = op_stats["losses"]
            total_selected_vp = op_stats["total_selected_vp"]
            total_bonus_vp = op_stats["total_bonus_vp"]

            win_pct = _percentage(wins, picks)
            avg_selected_vp = _average(total_selected_vp, picks)
            avg_bonus_vp = _average(total_bonus_vp, picks)
            finalized = {
                "label": OP_BUCKETS[op_key]["label"],
                "picks": picks,
                "matches": picks,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "win_percentage": win_pct,
                "total_selected_vp": total_selected_vp,
                "average_selected_vp": avg_selected_vp,
                "total_bonus_vp": total_bonus_vp,
                "average_bonus_vp": avg_bonus_vp,
            }
            ops[op_key] = finalized

            if picks == 0:
                continue

            score = (
                win_pct,
                wins,
                avg_selected_vp,
                avg_bonus_vp,
                picks,
            )
            if best_score is None or score > best_score:
                best_score = score
                tied_ops = [op_key]
            elif score == best_score:
                tied_ops.append(op_key)

        chosen_op = None
        if tied_ops:
            chosen_op = min(tied_ops, key=lambda op_key: PRIMARY_OP_ORDER[op_key])

        player_entries = scope_stats["player_entries"]
        missing_primary_ops = scope_stats["missing_primary_ops"]
        summary[scope] = {
            "total_matches": total_matches,
            "player_entries": player_entries,
            "revealed_primary_ops": player_entries - missing_primary_ops,
            "missing_primary_ops": missing_primary_ops,
            "ops": ops,
            "most_successful": {
                "op": chosen_op,
                "label": OP_BUCKETS[chosen_op]["label"] if chosen_op else None,
                "tied_ops": sorted(
                    tied_ops, key=lambda op_key: PRIMARY_OP_ORDER[op_key]
                ),
                "sort_fields": list(MOST_SUCCESSFUL_TIEBREAK),
                "stats": ops[chosen_op] if chosen_op else None,
            },
        }

    return summary


def _build_op_bucket_summary(
    op_bucket_accumulators: dict[str, dict[str, dict[str, int]]],
) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for op_key, scope_stats in OP_BUCKETS.items():
        score_summary: dict[str, object] = {"label": scope_stats["label"]}
        for scope, raw_stats in op_bucket_accumulators[op_key].items():
            matches = raw_stats["matches"]
            selected_as_primary = raw_stats["selected_as_primary"]
            total_vp = raw_stats["total_vp"]
            total_bonus_vp_when_primary = raw_stats["total_bonus_vp_when_primary"]
            score_summary[scope] = {
                "matches": matches,
                "wins": raw_stats["wins"],
                "draws": raw_stats["draws"],
                "losses": raw_stats["losses"],
                "win_percentage": _percentage(raw_stats["wins"], matches),
                "total_vp": total_vp,
                "average_vp": _average(total_vp, matches),
                "selected_as_primary": selected_as_primary,
                "total_bonus_vp_when_primary": total_bonus_vp_when_primary,
                "average_bonus_vp_when_primary": _average(
                    total_bonus_vp_when_primary,
                    selected_as_primary,
                ),
            }
        summary[op_key] = score_summary
    return summary


def build_stats_summary(archives: list[CompletedMatchArchive]) -> dict[str, object]:
    """Build the UI-facing stats summary from archived matches."""
    total_matches = len(archives)
    slot_wins = {"player_one": 0, "player_two": 0}
    slot_draws = {"player_one": 0, "player_two": 0}

    team_accumulators: dict[str, dict[str, dict[str, int]]] = {}
    primary_op_accumulators: dict[str, _PrimaryOpScopeAccum] = {
        scope: {
            "player_entries": 0,
            "missing_primary_ops": 0,
            "ops": {
                op_key: {
                    "picks": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "total_selected_vp": 0,
                    "total_bonus_vp": 0,
                }
                for op_key in SECRET_OP_CHOICES
            },
        }
        for scope in (*PLAYER_SLOTS, COMBINED_SCOPE)
    }
    op_bucket_accumulators: dict[str, dict[str, dict[str, int]]] = {
        op_key: {
            scope: {
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "matches": 0,
                "total_vp": 0,
                "selected_as_primary": 0,
                "total_bonus_vp_when_primary": 0,
            }
            for scope in (*PLAYER_SLOTS, COMBINED_SCOPE)
        }
        for op_key in SECRET_OP_CHOICES
    }

    def ensure_team(team_name: str) -> dict[str, dict[str, int]]:
        if team_name not in team_accumulators:
            team_accumulators[team_name] = {
                "overall": _init_outcome_accumulator(),
                "player_one": _init_outcome_accumulator(),
                "player_two": _init_outcome_accumulator(),
            }
        return team_accumulators[team_name]

    for archive in archives:
        winner = archive.winner
        if winner == DRAW_OUTCOME:
            slot_draws["player_one"] += 1
            slot_draws["player_two"] += 1
        else:
            slot_wins[winner] += 1

        snapshot = GameState.from_dict(archive.game_snapshot)
        teams_by_slot = {
            "player_one": snapshot.player_one_team,
            "player_two": snapshot.player_two_team,
        }
        players_by_slot = {
            "player_one": snapshot.player_one,
            "player_two": snapshot.player_two,
        }

        for slot, team_name in teams_by_slot.items():
            if team_name is None:
                continue
            stats = ensure_team(team_name)
            _record_outcome(stats["overall"], winner=winner, slot=slot)
            _record_outcome(stats[slot], winner=winner, slot=slot)

        for slot, scores in players_by_slot.items():
            primary_op = scores.secret_op
            scopes = (slot, COMBINED_SCOPE)

            for scope in scopes:
                scope_summary = primary_op_accumulators[scope]
                scope_summary["player_entries"] += 1
                if primary_op is None:
                    scope_summary["missing_primary_ops"] += 1
                else:
                    score_field = str(OP_BUCKETS[primary_op]["score_field"])
                    selected_vp = getattr(scores, score_field)
                    op_stats = scope_summary["ops"][primary_op]
                    assert isinstance(op_stats, dict)
                    op_stats["picks"] += 1
                    op_stats["total_selected_vp"] += selected_vp
                    op_stats["total_bonus_vp"] += scores.bonus_vp
                    if winner == DRAW_OUTCOME:
                        op_stats["draws"] += 1
                    elif winner == slot:
                        op_stats["wins"] += 1
                    else:
                        op_stats["losses"] += 1

                for op_key, op_meta in OP_BUCKETS.items():
                    bucket_stats = op_bucket_accumulators[op_key][scope]
                    score_field = str(op_meta["score_field"])
                    bucket_stats["matches"] += 1
                    bucket_stats["total_vp"] += getattr(scores, score_field)
                    if winner == DRAW_OUTCOME:
                        bucket_stats["draws"] += 1
                    elif winner == slot:
                        bucket_stats["wins"] += 1
                    else:
                        bucket_stats["losses"] += 1

                    if primary_op == op_key:
                        bucket_stats["selected_as_primary"] += 1
                        bucket_stats["total_bonus_vp_when_primary"] += scores.bonus_vp

    draws = slot_draws["player_one"]
    slot_stats = {
        "player_one": {
            "wins": slot_wins["player_one"],
            "draws": slot_draws["player_one"],
            "losses": total_matches
            - slot_wins["player_one"]
            - slot_draws["player_one"],
            "matches": total_matches,
            "win_percentage": _percentage(slot_wins["player_one"], total_matches),
        },
        "player_two": {
            "wins": slot_wins["player_two"],
            "draws": slot_draws["player_two"],
            "losses": total_matches
            - slot_wins["player_two"]
            - slot_draws["player_two"],
            "matches": total_matches,
            "win_percentage": _percentage(slot_wins["player_two"], total_matches),
        },
    }

    return {
        "total_matches": total_matches,
        "draws": draws,
        "player_slots": slot_stats,
        "teams": _build_team_stats(team_accumulators),
        "primary_ops": _build_primary_ops_summary(
            primary_op_accumulators,
            total_matches=total_matches,
        ),
        "op_buckets": _build_op_bucket_summary(op_bucket_accumulators),
    }


def build_win_rate_summary(archives: list[CompletedMatchArchive]) -> dict[str, object]:
    """Compatibility wrapper for consumers using the original summary builder."""
    return build_stats_summary(archives)
