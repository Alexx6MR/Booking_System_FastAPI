def time_to_integer(time_str: str) -> int:
    try:
        hours, minutes, seconds = time_str.split(':')
        return int(hours)
    except ValueError:
        raise ValueError("El formato de la hora debe ser HH:MM:SS")
