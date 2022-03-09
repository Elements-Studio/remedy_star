from utils import time_util


class User:
    def __init__(self):
        self.weight = 0
        self.latest_time = 0
        self.actual_gain = 0


def diff_two_times(lhs, rhs) -> int:
    return abs(time_util.readable_string_to_unix_time(lhs) -
               time_util.readable_string_to_unix_time(rhs))


def computer_gain(user, total_weight, now_time, release_per_second) -> int:
    time_interval = diff_two_times(user.latest_time, now_time)
    gain = time_interval * release_per_second * (user.weight / total_weight)
    return gain


def computer_users(opts, release_per_second) -> dict:
    total_weight = 0
    users = dict()
    latest_time = ""

    for opt in opts:
        sender = opt.sender

        # Contribute User object
        if sender not in users:
            user = User()
        else:
            user = users.get(sender)

        if opt.opt == 'stake':
            # Add weight
            user.weight = user.weight + opt.amount
            total_weight = total_weight + opt.amont
        elif opt.opt == 'unstake':
            # Add Gain
            gain = computer_gain(user, total_weight, opt.time, release_per_second)
            user.actual_gain = user.actual_gain + gain

            # Remove weight
            total_weight = total_weight - opt.amont
            user.weight = user.weight - opt.amount

        users[sender] = user
        latest_time = opt.time

    # Computer all gain in the end
    for u in users:
        u.actual_gain = u.actual_gain + computer_gain(u, total_weight, latest_time, release_per_second)
    return users
