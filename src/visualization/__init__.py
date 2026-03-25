"""
Shared visualization exports for the China institutes analysis.

This package includes publication-oriented plotting and table helpers as well as
dashboard-specific typology builders. Some functions write files, while others
return in-memory Plotly figures, pandas tables, or summary dictionaries for app use.
"""
from visualization.spectrum_plots import (   # noqa: F401
    plot_institute_spectrum,
    plot_2d_map,
)
from visualization.topic_heatmaps import (   # noqa: F401
    plot_topic_institute_heatmap,
    plot_sensitive_topic_heatmap,
)
from visualization.temporal_trends import (  # noqa: F401
    plot_institute_trends,
    plot_topic_trends,
)
from visualization.export_tables import (    # noqa: F401
    export_main_results_table,
    export_method_comparison_table,
    export_sensitive_coverage_table,
)
from visualization.typology_dashboard_charts import (  # noqa: F401
    build_dominant_domain_composition_chart,
    build_institute_domain_salience_chart,
    build_institute_drilldown_summary,
    build_institute_vs_peer_comparison_chart,
    build_institute_within_domain_orientation_chart,
    build_typology_field_map,
    build_typology_kpis,
    build_typology_member_table,
    build_typology_profile_heatmap,
)

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
