"""Load the modules of a skill folder as plugins, one module per piece or per check."""
import importlib.util
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover(folder):
    """Yield (id, module) for each module in the folder; the id is the file name with hyphens."""
    for path in sorted((SKILL_DIR / folder).glob("*.py")):
        yield path.stem.replace("_", "-"), load(path)
