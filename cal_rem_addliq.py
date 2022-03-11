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


def computer_users(opts, token_y_tag, multiplier, apy) -> dict:
    users = dict()
    for opt_obj in opts:
        sender = opt_obj.get('sender')
        opt = opt_obj.get('opt')
        if opt not in ['add_liquidity', 'remove_liquidity']:
            continue

        if opt_obj.get('token_y') != token_y_tag:
            continue

        token_x, token_y = convert_list_string_to_amount(opt_obj.get('amount'))
        token_x = token_x / 1e9
        token_y = token_y / 1e9

        if sender not in users:
            user = User()
            user.sender = sender
            user.token_x = token_x
            user.token_y = token_y
        else:
            user = users.get(sender)
            user.token_x = user.token_x + token_x if opt == 'add_liquidity' else user.token_x - token_x
            user.token_y = user.token_x + token_y if opt == 'add_liquidity' else user.token_y - token_y
        users[sender] = user

    for k, v in users.items():
        v.remedy_amount = v.token_y * multiplier * apy * 16_200 / 31_536_000

    return users
