from utils import time_util


class User:
    def __init__(self):
        self.sender = 0
        self.token_x = 0
        self.token_y = 0
        self.remedy_amount = 0


def convert_list_string_to_amount(s) -> (int, int):
    s = s.strip("(")
    s = s.strip(")")
    a = s.split(",")
    return int(a[0]), int(a[1])


def computer_users(opts, multiplier, apy) -> dict:
    users = dict()
    for opt in opts:
        sender = opt.get('sender')

        if opt.get('opt') != "add_liquidity":
            continue

        token_x, token_y = convert_list_string_to_amount(opt.get('amount'))
        token_x = token_x / 1e9
        token_y = token_y / 1e9

        if sender not in users:
            user = User()
            user.sender = sender
            user.token_x = token_x
            user.token_y = token_y
        else:
            user = users.get(sender)
            user.token_x = user.token_x + token_x
            user.token_y = user.token_x + token_y
        users[sender] = user

    for k, v in users.items():
        v.remedy_amount = v.token_y * multiplier * apy * 16_200 / 31_536_000

    return users
