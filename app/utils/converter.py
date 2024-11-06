from datetime import datetime


def time_to_integer(time_str: str) -> int:
    try:
        hours, minutes, seconds = time_str.split(':')
        return int(hours)
    except ValueError:
        raise ValueError("El formato de la hora debe ser HH:MM:SS")

def sort_time(lista):

    # Sort the list of time objects
    sorted_times = sorted(lista)

    # Get the lowest and highest times
    lowest_time = sorted_times[0]
    highest_time = sorted_times[-1]


    return lowest_time, highest_time