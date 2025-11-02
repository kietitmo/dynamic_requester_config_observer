import re

def get_nested_key(data: dict, path: str, default=None):
    """Truy cập an toàn dict lồng nhau, hỗ trợ cả list index như 'a.b[0].c'."""
    keys = re.split(r'\.(?![^\[]*\])', path)  # tách theo dấu . nhưng không tách trong [ ]
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k, default)
        elif isinstance(data, list):
            match = re.match(r'\[(\d+)\]', k)
            if match:
                idx = int(match.group(1))
                data = data[idx] if idx < len(data) else default
            else:
                return default
        else:
            return default
    return data
