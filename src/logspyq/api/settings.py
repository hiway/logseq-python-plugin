from dataclasses import asdict, dataclass, field
from typing import Any

PY_JS_TYPES = {
    str: "string",
    float: "number",
    int: "number",
    dict: "object",
    bool: "boolean",
}


def setting(
    default: Any,
    description: str,
):
    return field(
        default=default,
        metadata=dict(
            description=description,
            default=default,
        ),
    )


def settings_schema(_cls=None):
    def wrap(cls):
        wrapped_cls = dataclass(cls)
        setattr(wrapped_cls, "schema", schema_as_dict)
        return wrapped_cls

    if _cls is None:
        return wrap

    return wrap(_cls)


def schema_as_dict(settings):
    if not settings:
        return {}
    sett = asdict(settings)
    for key, value in sett.items():
        meta = dict(getattr(settings, "__dataclass_fields__")[key].metadata)
        py_type = getattr(settings, "__dataclass_fields__")[key].type
        try:
            js_type = PY_JS_TYPES[py_type]
        except KeyError:
            raise Exception(
                f"Expected type for setting {key} to be one of {', '.join([str(k) for k in PY_JS_TYPES.keys()])}, got: {type(value)}"
            )
        meta.update(
            {"default": value, "key": key, "title": key.replace("_", " ").title(), "type": js_type}
        )
        sett[key] = meta
    return [s for s in sett.values()]
