from dataclasses import dataclass
from typing import List, Optional, Set, Dict


@dataclass
class ProcessingConfig:
    normal_values: Dict
    skip_keys: Set[str]
    genes_list: Optional[List[str]] = None
