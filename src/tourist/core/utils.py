import json


def to_single_line(script: str, as_json: bool = True) -> str:
    single_line = repr(script)[1:-1]
    single_line = json.dumps(single_line) if as_json else single_line
    return single_line.replace('"', r"\"").replace("'", r"\"")
