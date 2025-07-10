
import json
from pathlib import Path
import typing as t

# Define a type for a generation dictionary for clarity
Generation = t.Dict[str, t.Any]

class GenerationManager:
    """Handles all operations related to generations.json."""

    def __init__(self, generations_path: Path):
        self.path = generations_path
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text('{"generations": []}')

    def _read_data(self) -> t.Dict[str, t.List[Generation]]:
        """Reads the raw data from the JSON file."""
        with open(self.path) as f:
            return json.load(f)

    def get_all(self) -> t.List[Generation]:
        """Returns a list of all generations, sorted by ID."""
        data = self._read_data()
        return sorted(data.get("generations", []), key=lambda g: g["id"])

    def find_by_id(self, generation_id: int) -> t.Optional[Generation]:
        """Finds a single generation by its ID."""
        for gen in self.get_all():
            if gen["id"] == generation_id:
                return gen
        return None

# We can create a default instance to use across the application
# This assumes the generations.json is in the project root for now.
GENERATIONS_FILE = Path(__file__).parent.parent / "generations.json"
gen_manager = GenerationManager(GENERATIONS_FILE)
