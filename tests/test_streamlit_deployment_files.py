from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_streamlit_deployment_files_exist_with_required_dependencies():
    requirements_path = REPO_ROOT / "requirements.txt"
    config_path = REPO_ROOT / ".streamlit" / "config.toml"

    assert requirements_path.exists(), "requirements.txt is required for Streamlit deployment"
    assert config_path.exists(), ".streamlit/config.toml is required for Streamlit deployment"

    requirements = {
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    for package in {"streamlit", "plotly", "pandas", "numpy"}:
        assert package in requirements, f"{package} must be declared in requirements.txt"


def test_readme_includes_streamlit_cloud_instructions():
    readme_text = (REPO_ROOT / "README.md").read_text()

    assert "Streamlit Community Cloud" in readme_text
    assert "app/results_dashboard.py" in readme_text
    assert "typology_dashboard_snapshot.html" in readme_text
