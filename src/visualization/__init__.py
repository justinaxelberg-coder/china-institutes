"""
Shared visualization exports for the China institutes analysis.

This package exposes plotting and export helpers while keeping optional plotting
dependencies lazy. That lets the Streamlit dashboard import its Plotly-only
modules without eagerly importing the older matplotlib/seaborn stack.
"""

from __future__ import annotations

from importlib import import_module


_EXPORTS = {
    "plot_institute_spectrum": ("visualization.spectrum_plots", "plot_institute_spectrum"),
    "plot_2d_map": ("visualization.spectrum_plots", "plot_2d_map"),
    "plot_topic_institute_heatmap": ("visualization.topic_heatmaps", "plot_topic_institute_heatmap"),
    "plot_sensitive_topic_heatmap": ("visualization.topic_heatmaps", "plot_sensitive_topic_heatmap"),
    "plot_institute_trends": ("visualization.temporal_trends", "plot_institute_trends"),
    "plot_topic_trends": ("visualization.temporal_trends", "plot_topic_trends"),
    "export_main_results_table": ("visualization.export_tables", "export_main_results_table"),
    "export_method_comparison_table": ("visualization.export_tables", "export_method_comparison_table"),
    "export_sensitive_coverage_table": ("visualization.export_tables", "export_sensitive_coverage_table"),
    "build_dominant_domain_composition_chart": (
        "visualization.typology_dashboard_charts",
        "build_dominant_domain_composition_chart",
    ),
    "build_institute_domain_salience_chart": (
        "visualization.typology_dashboard_charts",
        "build_institute_domain_salience_chart",
    ),
    "build_institute_drilldown_summary": (
        "visualization.typology_dashboard_charts",
        "build_institute_drilldown_summary",
    ),
    "build_institute_vs_peer_comparison_chart": (
        "visualization.typology_dashboard_charts",
        "build_institute_vs_peer_comparison_chart",
    ),
    "build_institute_within_domain_orientation_chart": (
        "visualization.typology_dashboard_charts",
        "build_institute_within_domain_orientation_chart",
    ),
    "build_typology_field_map": ("visualization.typology_dashboard_charts", "build_typology_field_map"),
    "build_typology_kpis": ("visualization.typology_dashboard_charts", "build_typology_kpis"),
    "build_typology_member_table": ("visualization.typology_dashboard_charts", "build_typology_member_table"),
    "build_typology_profile_heatmap": ("visualization.typology_dashboard_charts", "build_typology_profile_heatmap"),
}

_SUBMODULES = {
    "export_tables",
    "spectrum_plots",
    "temporal_trends",
    "topic_heatmaps",
    "typology_dashboard_charts",
    "typology_dashboard_data",
    "typology_snapshot",
}


def __getattr__(name: str):
    if name in _SUBMODULES:
        return import_module(f"visualization.{name}")
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = _EXPORTS[name]
    module = import_module(module_name)
    return getattr(module, attr_name)


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + list(_EXPORTS.keys()))

__all__ = [
    "plot_institute_spectrum", "plot_2d_map",
    "plot_topic_institute_heatmap", "plot_sensitive_topic_heatmap",
    "plot_institute_trends", "plot_topic_trends",
    "export_main_results_table", "export_method_comparison_table",
    "export_sensitive_coverage_table",
    "build_dominant_domain_composition_chart",
    "build_institute_domain_salience_chart",
    "build_institute_drilldown_summary",
    "build_institute_vs_peer_comparison_chart",
    "build_institute_within_domain_orientation_chart",
    "build_typology_field_map",
    "build_typology_kpis",
    "build_typology_member_table",
    "build_typology_profile_heatmap",
]
