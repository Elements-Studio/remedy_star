from utils import time_util


def diff_two_times(start, end) -> int:
    return time_util.readable_string_to_unix_time(end) - time_util.readable_string_to_unix_time(start)


class User:
    def __init__(self):
        self.sender = 0
        self.asset_weight = 0
        self.harvest_index = 0
        self.actual_gain = 0
        self.expect_gain = 0
        self.remedy_gain = 0

    def add_new_gain(self, new_acutal_gain, multiplier):
        self.actual_gain = self.actual_gain + new_acutal_gain

        new_expect_gain = new_acutal_gain * multiplier
        self.expect_gain = self.expect_gain + new_expect_gain

        new_remedy_gain = new_expect_gain - new_acutal_gain
        self.remedy_gain = self.remedy_gain + new_remedy_gain

    def add_weight(self, weight):
        self.asset_weight = self.asset_weight + weight

    def remove_weight(self, weight):
        self.asset_weight = self.asset_weight - weight


class AssetPool:
    def __init__(self, begin_time, release_per_second):
        self.harvest_index = 0
        self.total_weight = 0
        self.last_update = begin_time
        self.release_per_second = release_per_second

    def refresh_new_harvest_index(self, now_seconds):
        time_period = diff_two_times(self.last_update, now_seconds)
        if self.total_weight <= 0:
            self.harvest_index = self.harvest_index + (time_period * self.release_per_second)
        else:
            self.harvest_index = self.harvest_index + (time_period * self.release_per_second / self.total_weight)
        self.last_update = now_seconds

    def computer_gain(self, user) -> int:
        if self.total_weight <= 0:
            return self.harvest_index - user.harvest_index
        return user.asset_weight * (self.harvest_index - user.harvest_index)

    def add_weight(self, weight):
        self.total_weight = self.total_weight + weight

    def remove_weight(self, weight):
        self.total_weight = self.total_weight - weight


def computer_users(opts, begin_time, end_time, release_per_second, multiplier) -> dict:
    pool = AssetPool(begin_time=begin_time, release_per_second=release_per_second)
    users = dict()

    for opt in opts:
        sender = opt.get('sender')
        option = opt.get('opt')
        now_seconds = opt.get('opt_time')
        asset_weight = int(opt.get('amount'))

        if option not in ['stake', 'unstake']:
            continue

        # Contribute User object
        if sender not in users:
            user = User()
            user.sender = sender
        else:
            user = users.get(sender)

        if pool.total_weight <= 0:
            pool.refresh_new_harvest_index(now_seconds)

        if option == 'stake':
            new_gain = pool.computer_gain(user)
            user.add_new_gain(new_gain, multiplier)
            user.add_weight(asset_weight)

            pool.add_weight(asset_weight)
            pool.refresh_new_harvest_index(now_seconds)

        elif option == 'unstake':
            new_gain = pool.computer_gain(user)
            user.add_new_gain(new_gain, multiplier)
            user.remove_weight(asset_weight)

            pool.remove_weight(asset_weight)
            pool.refresh_new_harvest_index(now_seconds)

        user.harvest_index = pool.harvest_index
        users[sender] = user

    # Computer all gain in the end
    for sender, user in users.items():
        pool.refresh_new_harvest_index(end_time)
        new_gain = pool.computer_gain(user)
        user.add_new_gain(new_gain, multiplier)

    return users
