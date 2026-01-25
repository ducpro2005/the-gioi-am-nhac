from typing import List, Dict
from functools import lru_cache

@lru_cache(maxsize=1)
def get_nav_items(template_dir: str = None) -> List[Dict[str, str]]:
    """Return a fixed list of nav items."""
    return [
        {'href': '/library/', 'text': 'Library'},
        {'href': '/vnmap', 'text': 'VnMap'},
        {'href': '/thesis', 'text': 'Thesis'},
        {'href': '/quiz/', 'text': 'Quiz'},
        {'href': '/music_world/', 'text': 'Music World'},
    ]