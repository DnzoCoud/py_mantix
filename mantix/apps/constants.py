from enum import Enum


class EventStatusEnum(Enum):
    PROGRAMADO = 1
    EN_EJECUCION = 2
    COMPLETADO = 3
    REPROGRAMADO = 4
    PETICION_REPROGRAMADO = 5


def str_to_bool(s):
    if s.lower() in ["true", "1", "yes", "y"]:
        return True
    elif s.lower() in ["false", "0", "no", "n"]:
        return False
    else:
        raise ValueError(f"Cannot convert {s} to boolean")
