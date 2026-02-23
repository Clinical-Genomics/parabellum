from dataclasses import dataclass
from typing import List, Optional, Set, Dict, Any


@dataclass
class ProcessingConfig:
    """
    Configuration for how to process paraphase JSONs.

    - skip_keys: keys under each gene that should be ignored entirely.
    - genes_list: optional list of genes to keep; if None, keep all.
    - rules: optional per-gene classification rules YAML structure.
    """

    skip_keys: Set[str]
    genes_list: Optional[List[str]] = None
    rules: Optional[Dict[str, Any]] = None
