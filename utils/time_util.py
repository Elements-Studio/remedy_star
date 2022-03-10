import datetime


def unix_time_to_readable_string(timestamp):
    return f"{datetime.datetime.fromtimestamp(timestamp):%Y-%m-%d %H:%M:%S}"


def readable_string_to_unix_time(str):
    return int(datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S').strftime("%s"))


def diff_two_times(start, end) -> int:
    return readable_string_to_unix_time(end) - readable_string_to_unix_time(start)
