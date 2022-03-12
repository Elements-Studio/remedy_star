from utils import time_util
from ast import literal_eval as make_tuple

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


def computer_users(opts, token_y_tag, multiplier, apy) -> dict:
    users = dict()
    for opt_obj in opts:
        sender = opt_obj.get('sender')
        opt = opt_obj.get('opt')
        if opt not in ['add_liquidity', 'remove_liquidity']:
            continue

        if opt_obj.get('token_y') != token_y_tag:
            continue

        amount = opt_obj.get('amount')
        amount_x = 0
        amount_y = 0
        if "(" in amount:
            amount_x, amount_y = make_tuple(opt_obj.get('amount'))

        amount_x = amount_x / 1e9
        amount_y = amount_y / 1e9

        if sender not in users:
            user = User()
            user.sender = sender
            user.token_x = amount_x
            user.token_y = amount_y
        else:
            user = users.get(sender)
            user.token_x = user.token_x + amount_x
            user.token_y = user.token_y + amount_y
        users[sender] = user


    for k, v in users.items():
        v.remedy_amount = v.token_y * multiplier * apy * 16_200 / 31_536_000

    return users
