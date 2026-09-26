"""The closed pre-v0.2 corpus behind L05 and REQ-defaults-off-regression.

Every hand-written GearParams set from `tests/` and `README.md` as it existed at the end
of v0.1 (commit b3ca789) -- the shareable links that must still build the same part after
every v0.2 feature. This corpus never tracks later test edits: a source line that changes
after v0.2 lands does not change its entry here, because the whole point is proving v0.2
did not move the pre-v0.2 part. Do not narrow, shorten or re-pick it -- a record that
disappears is a guarantee that disappears (`bench/corpus.py`'s own rule, D-05).

Sources are `tests/` and `README.md` only (D-08); `docker/smoke.py` and `bench/corpus.py`
stay out on purpose. Only hand-written literal parameter sets enter -- parametrize lists,
inline `GearParams(...)` calls, `TestClient` `params=` dicts, `cli.main([...])` argument
lists, and the README's own examples (D-09). Machine-generated grids (the centre-distance
solver's cross-check) and sets that fail validation cannot enter by construction.
"""

from __future__ import annotations

from typing import NamedTuple

from spur.params import GearParams


class Entry(NamedTuple):
    """One hand-written parameter set as its source wrote it, tagged by where it lives."""

    tag: str
    params: dict[str, object]
    mate: int | None = None


# Named dicts several sources repeat verbatim -- kept once here, spread into each entry's
# params exactly like the sources that inline them (tests/test_api.py's own SMALL_GEAR).
README_TEETH_24: dict[str, object] = {
    "teeth": 24, "module": 1, "pressure_angle": 20, "bore_flat": 0,
}
SMALL_GEAR: dict[str, object] = {
    "teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6,
    "bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none",
}

ENTRIES: tuple[Entry, ...] = (
    # --- README.md -----------------------------------------------------------------
    Entry("README:export-defaults", {}),
    Entry("README:export-teeth-24", README_TEETH_24),
    Entry("README:info-mate-40", {"teeth": 19}, 40),
    Entry("README:curl-step", {"teeth": 19, "module": 1.75, "pressure_angle": 25}),
    # --- tests/test_api.py -----------------------------------------------------------
    Entry("test_api.py::test_info_reports_the_mate", {"teeth": 21}, 40),
    Entry("test_api.py::test_model_download", {"teeth": 21}),
    Entry("test_api.py::test_impossible_mate_is_a_warning_not_a_number", SMALL_GEAR, 40),
    Entry("test_api.py::test_a_gear_too_small_for_the_stock_recess_is_still_served",
         README_TEETH_24),
    Entry("test_api.py::test_a_saturated_service_refuses_instead_of_queueing", {}),
    Entry("test_api.py::"
         "test_a_saturated_service_emits_queue_refused_naming_the_gear_and_the_ceiling",
         {"teeth": 72}),
    Entry("test_api.py::test_a_second_identical_download_is_served_from_the_byte_cache",
         {"teeth": 22}),
    Entry("test_api.py::"
         "test_a_gzip_client_gets_compressed_bytes_an_identity_client_gets_the_raw_file",
         {"teeth": 31}),
    Entry("test_api.py::test_a_gear_is_compressed_once_per_cache_fill_not_once_per_download",
         {"teeth": 32}),
    Entry("test_api.py::"
         "test_a_cache_hit_that_still_needs_compressing_goes_through_admission_control",
         {"teeth": 33}),
    Entry("test_api.py::test_an_already_compressed_download_needs_no_slot_at_all",
         {"teeth": 33}),
    Entry("test_api.py::"
         "test_a_fresh_build_emits_build_started_then_export_served_with_source_built",
         {"teeth": 61}),
    Entry("test_api.py::"
         "test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started",
         {"teeth": 62}),
    Entry("test_api.py::test_a_gzip_request_after_an_identity_download_emits_source_compressed",
         {"teeth": 63}),
    Entry("test_api.py::test_an_all_default_gear_logs_params_as_an_empty_object_not_omitted",
         {}),
    Entry("test_api.py::test_two_requests_for_one_gear_get_two_different_request_ids",
         {"teeth": 64}),
    Entry("test_api.py::test_a_failed_build_emits_build_failed_naming_the_class_and_the_level",
         {"teeth": 71}),
    Entry("test_api.py::"
         "test_an_unclassified_exception_still_emits_build_failed_and_is_not_swallowed",
         {"teeth": 73}),
    # --- tests/test_calc.py -----------------------------------------------------------
    Entry("test_calc.py::test_default_dimensions", {}),
    Entry("test_calc.py::test_a_derived_dimensions_result_cannot_be_changed", {}),
    Entry("test_calc.py::test_caliper_reading_is_short_for_odd_tooth_counts[teeth=19]",
         {"teeth": 19}),
    Entry("test_calc.py::test_caliper_reading_is_short_for_odd_tooth_counts[teeth=20]",
         {"teeth": 20}),
    Entry("test_calc.py::test_span_measurement[0]",
         {"module": 1.75, "pressure_angle": 20, "bore_d": 0, "recess_sides": "none"}),
    Entry("test_calc.py::test_span_measurement[1]",
         {"module": 1.75, "pressure_angle": 25, "bore_d": 0, "recess_sides": "none"}),
    Entry("test_calc.py::test_span_measurement[2]",
         {"module": 1.0, "pressure_angle": 20, "bore_d": 0, "recess_sides": "none"}),
    Entry("test_calc.py::"
         "test_higher_pressure_angle_gives_finer_tips_and_thicker_roots[pa=20]",
         {"pressure_angle": 20}),
    Entry("test_calc.py::"
         "test_higher_pressure_angle_gives_finer_tips_and_thicker_roots[pa=25]",
         {"pressure_angle": 25}),
    Entry("test_calc.py::test_centre_distance_unshifted_and_shifted[unshifted]", {}, 40),
    Entry("test_calc.py::test_centre_distance_unshifted_and_shifted[shifted]",
         {"profile_shift": 0.3}, 40),
    Entry("test_calc.py::test_root_fillet_is_capped_with_a_warning",
         {"teeth": 80, "module": 0.5, "bore_d": 5, "bore_flat": 0}),
    Entry("test_calc.py::test_no_bore_ignores_d_flat", {"bore_d": 0}),
    Entry("test_calc.py::test_tooth_thickness_and_gap_are_measured_on_the_same_circle[teeth=19]",
         {"teeth": 19}),
    Entry("test_calc.py::test_tooth_thickness_and_gap_are_measured_on_the_same_circle[teeth=40]",
         {"teeth": 40}),
    Entry("test_calc.py::test_oversized_recess_is_narrowed_to_fit_and_says_so",
         {"recess_width": 12}),
    Entry("test_calc.py::test_small_gear_keeps_the_stock_bore_and_recess", README_TEETH_24),
    Entry("test_calc.py::test_recess_is_dropped_when_there_is_no_room_at_all",
         {"teeth": 16, "module": 1, "bore_d": 9, "bore_flat": 8}),
    Entry("test_calc.py::test_recess_fillet_is_capped_to_the_narrowed_groove",
         {"recess_width": 12, "recess_fillet": 3}),
    Entry("test_calc.py::test_impossible_pairs_have_no_centre_distance[0]", SMALL_GEAR, 40),
    Entry("test_calc.py::test_impossible_pairs_have_no_centre_distance[1]",
         {**SMALL_GEAR, "profile_shift": -0.5}, 12),
    # --- tests/test_cli.py -----------------------------------------------------------
    Entry("test_cli.py::test_info_reports_the_mate_it_was_asked_about", {"teeth": 19}, 40),
    Entry("test_cli.py::test_cli_and_api_print_the_same_document[teeth-21]", {"teeth": 21}),
    Entry("test_cli.py::test_cli_and_api_print_the_same_document[teeth-21-mate]",
         {"teeth": 21}, 40),
    Entry("test_cli.py::test_cli_and_api_print_the_same_document[impossible]", SMALL_GEAR, 40),
    Entry("test_cli.py::test_readme_export_examples_run[defaults]", {}),
    Entry("test_cli.py::test_readme_export_examples_run[teeth-24]", README_TEETH_24),
    # --- tests/test_model.py -----------------------------------------------------------
    Entry("test_model.py::test_builds_one_valid_solid[0]", {}),
    Entry("test_model.py::test_builds_one_valid_solid[1]", {"pressure_angle": 20}),
    Entry("test_model.py::test_builds_one_valid_solid[2]", {"bore_flat": 0}),
    Entry("test_model.py::test_builds_one_valid_solid[3]", {"bore_d": 0}),
    Entry("test_model.py::test_builds_one_valid_solid[4]", {"recess_sides": "none"}),
    Entry("test_model.py::test_builds_one_valid_solid[5]", {"recess_sides": "top"}),
    Entry("test_model.py::test_builds_one_valid_solid[6]",
         {"root_fillet": 0, "recess_fillet": 0, "bore_chamfer": 0}),
    Entry("test_model.py::test_builds_one_valid_solid[7]",
         {"teeth": 8, "module": 1.5, "bore_d": 3, "bore_flat": 0, "recess_sides": "none"}),
    Entry("test_model.py::test_builds_one_valid_solid[8]",
         {"teeth": 40, "module": 2, "profile_shift": 0.4, "pressure_angle": 20,
          "face_width": 12, "bore_d": 12, "bore_flat": 11, "recess_depth": 4}),
    Entry("test_model.py::test_recess_removes_expected_volume[no-recess]",
         {"recess_sides": "none", "recess_fillet": 0}),
    Entry("test_model.py::test_recess_removes_expected_volume[recess]", {"recess_fillet": 0}),
    Entry("test_model.py::test_exports", {}),
    Entry("test_model.py::test_a_gear_too_small_for_the_stock_recess_still_builds",
         README_TEETH_24),
    Entry("test_model.py::test_exported_stl_is_a_closed_consistently_oriented_shell", {}),
    Entry("test_model.py::test_exporting_leaves_the_cached_solid_exact", {}),
    Entry("test_model.py::test_an_stl_export_matches_a_first_export_whatever_came_before", {}),
    # --- tests/test_pool.py -----------------------------------------------------------
    Entry("test_pool.py::test_a_real_worker_builds_and_downloads", {"teeth": 21}),
    Entry("test_pool.py::test_the_same_gear_always_reaches_the_same_worker", {"teeth": 21}),
    Entry("test_pool.py::test_preview_fine_and_step_share_one_worker", {"teeth": 21}),
    Entry("test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced",
         {"teeth": 21}),
    Entry("test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced",
         {"teeth": 21}),
    Entry("test_pool.py::test_each_build_failure_mode_maps_to_its_own_status_and_type",
         {"teeth": 43}),
    Entry("test_pool.py::test_the_four_failure_types_are_pairwise_distinct", {"teeth": 44}),
    Entry("test_pool.py::test_health_queue_available_falls_while_a_slot_is_held", {}),
    Entry("test_pool.py::"
         "test_health_workers_replaced_increases_after_a_forced_termination",
         {"teeth": 21}),
    Entry("test_pool.py::test_four_same_slot_requests_all_refuse_without_cancellation",
         {"teeth": 21}),
    Entry("test_pool.py::"
         "test_two_same_slot_deaths_from_one_incident_replace_the_worker_once",
         {"teeth": 21}),
    # --- tests/test_records.py -----------------------------------------------------------
    Entry("test_records.py::"
         "test_a_model_request_emits_one_export_served_line_that_json_loads_round_trips",
         {"teeth": 41}),
    Entry("test_records.py::test_build_failed_helper_never_carries_a_traceback_field", {}),
)


class Case(NamedTuple):
    """A deduplicated corpus entry: one GearParams (or one (GearParams, mate) pair),
    plus every source tag that produced it."""

    params: dict[str, object]
    mate: int | None
    sources: list[str]


def cases() -> dict[str, Case]:
    """Deduplicate ENTRIES by GearParams equality (and by (GearParams, mate) for mated
    sets), in listing order.

    The first entry whose GearParams is new opens a base case keyed by its own tag; a
    later entry with an equal GearParams only appends its tag to that case's sources. An
    entry that also names a mate opens or extends a second, mate-keyed case the same way,
    for the (GearParams, mate) pair. Insertion order in the returned dict is the order
    each case first appeared in ENTRIES.
    """
    result: dict[str, Case] = {}
    seen_tags: set[str] = set()
    base_keys: dict[GearParams, str] = {}
    mate_keys: dict[tuple[GearParams, int], str] = {}

    for entry in ENTRIES:
        if entry.tag in seen_tags:
            raise ValueError(f"duplicate corpus tag: {entry.tag}")
        seen_tags.add(entry.tag)

        p = GearParams.model_validate(entry.params)
        base_key = base_keys.get(p)
        if base_key is None:
            base_keys[p] = entry.tag
            result[entry.tag] = Case(params=entry.params, mate=None, sources=[entry.tag])
        else:
            result[base_key].sources.append(entry.tag)

        if entry.mate is not None:
            mate_key = mate_keys.get((p, entry.mate))
            if mate_key is None:
                case_key = f"{entry.tag}+mate={entry.mate}"
                if case_key in result:
                    raise ValueError(f"corpus key collision: {case_key}")
                mate_keys[(p, entry.mate)] = case_key
                result[case_key] = Case(params=entry.params, mate=entry.mate,
                                        sources=[entry.tag])
            else:
                result[mate_key].sources.append(entry.tag)

    return result
