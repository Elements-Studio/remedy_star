from utils import time_util


class User:
    def __init__(self):
        self.sender = 0
        self.stake_amount = 0
        self.remedy_amount = 0


def convert_list_string_to_amount(s) -> int:
    s = s.strip("(")
    s = s.strip(")")
    return int(s.split(",")[1])


def computer_users(opts, multiplier, apy) -> dict:
    users = dict()
    for opt in opts:
        sender = opt.get('sender')

        if opt.get('opt') != "add_liquidity":
            continue

        stake_amount = convert_list_string_to_amount(opt.get('amount'))
        if sender not in users:
            user = User()
            user.sender = sender
            user.stake_amount = stake_amount
        else:
            user = users.get(sender)
            user.stake_amount = user.stake_amount + stake_amount

        user.remedy_amount = user.stake_amount * multiplier * apy * 16_200 / 31_536_000
        users[sender] = user

    return users
