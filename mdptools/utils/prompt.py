from .highlight import highlight as _h


def fail(message, code) -> str:
    return (
        f"[{_h[_h.fail, 'Failed']}] {_h[_h.note, message]}\n{' '*9}>> {code}"
    )


def error(error_message, tip, code) -> str:
    return f"{_h[_h.error, error_message]}\n{' '*11}{tip}\n{' '*11}>> {code}"


def dist_wrong_value(s, a, value):
    from .stringify import literal_string

    return error(
        "Set is not allowed as a distribution value.",
        "Please use a Dictionary instead.",
        f"{_h[_h.function, 'Dist']}({_h[_h.state, s]}, {_h[_h.action, a]}) -> {literal_string(value)}",
    )
