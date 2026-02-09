import yaml
from pathlib import Path


def load_registry(tenant: str) -> dict:
    """Load a tool registry YAML file for a given tenant."""
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    registry_path = tools_dir / f"{tenant}.yaml"

    if not registry_path.exists():
        return {"tools": []}

    with open(registry_path, "r") as f:
        return yaml.safe_load(f)


def list_registries() -> list[str]:
    """List all available tool registries (tenant names)."""
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    if not tools_dir.exists():
        return []
    return [f.stem for f in tools_dir.glob("*.yaml")]
