from utils import time_util


class User:
    def __init__(self):
        self.sender = 0
        self.weight = 0
        self.latest_time = 0
        self.actual_gain = 0
        self.expect_gain = 0


def diff_two_times(lhs, rhs) -> int:
    return abs(time_util.readable_string_to_unix_time(lhs) -
               time_util.readable_string_to_unix_time(rhs))


def computer_gain(user, total_weight, now_time, release_per_second) -> int:
    time_interval = diff_two_times(user.latest_time, now_time)
    gain = time_interval * release_per_second * (user.weight / total_weight)
    return gain


def computer_users(opts, begin_time, release_per_second, multiplier) -> dict:
    total_weight = 0
    users = dict()
    latest_time = begin_time

    for opt in opts:
        sender = opt.get('sender')
        option = opt.get('opt')
        now_time = opt.get('opt_time')
        amount = int(opt.get('amount'))

        # Contribute User object
        if sender not in users:
            user = User()
            user.latest_time = begin_time
            user.sender = sender
        else:
            user = users.get(sender)

        if option == 'stake':
            # Add weight
            user.weight = user.weight + amount
            total_weight = total_weight + amount

        elif option == 'unstake':
            # Add Gain
            new_gain = computer_gain(user, total_weight, now_time, release_per_second)
            user.actual_gain = user.actual_gain + new_gain
            user.expect_gain = user.expect_gain + new_gain * multiplier

            # Remove weight
            total_weight = total_weight - amount
            user.weight = 0
        else:
            latest_time = now_time
            continue

        user.latest_time = now_time
        users[sender] = user
        latest_time = now_time

    # Computer all gain in the end
    for sender, user in users.items():
        new_gain = computer_gain(user, total_weight, latest_time, release_per_second)
        user.actual_gain = user.actual_gain + new_gain
        user.expect_gain = user.expect_gain + new_gain * multiplier
    return users
