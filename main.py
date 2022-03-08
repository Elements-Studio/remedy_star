#!/bin/bash
import concurrent
import csv
import datetime

from starcoin.sdk import client
from starcoin import starcoin_types, starcoin_stdlib

import starswap_decode_script

cli = client.Client("https://main-seed.starcoin.org")


class UserOpt:
    def __init__(self, block_num, sender, opt, opt_time, amount):
        self.block_num = block_num
        self.sender = sender
        self.opt = opt
        self.opt_time = opt_time
        self.amount = amount


def parse_module_address(payload) -> str:
    return "0x" + ''.join([hex(i)[2:] for i in payload.value.module.address.value])


def parser_txn(txn, block_num, block_timestamp):
    raw_txn = txn["raw_txn"]
    txn_hash = txn["transaction_hash"]

    sender = raw_txn["sender"]
    payload = raw_txn["payload"]
    payload = bytes.fromhex(payload[2:])
    try:
        payload = starcoin_types.TransactionPayload.bcs_deserialize(payload)

        script = payload.value
        module_name = script.module.name.value,
        function_name = script.function.value

        contract_addr = parse_module_address(payload)
        if contract_addr != "0x8c109349c6bd91411d6bc962e080c4a3":
            print("{} {} 's contract address not `0x8c109349c6bd91411d6bc962e080c4a3, {}::{}`.".format(block_num,
                                                                                                       txn_hash,
                                                                                                       module_name,
                                                                                                       function_name))
            return None

        txn_info = cli.get_transaction_info(txn_hash)
        if "status" not in txn_info or txn_info["status"] != "Executed":
            print("{} {} 's state are not `Executed`. {}::{}".format(block_num, txn_hash, module_name,
                                                                     function_name))
            return None

        function_call = starcoin_stdlib.decode_script_function_payload(payload)
        amount = 0
        opt = ''

        if isinstance(function_call, starswap_decode_script.ScriptFunctionCall__stake):
            amount = function_call.get_amount()
            opt = "stake"
        elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__unstake):
            amount = function_call.get_amount()
            opt = "unstake"
        elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__harvest):
            amount = function_call.get_amount()
            opt = "harvest"
        elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__setFarmMultiplier):
            amount = function_call.get_amount()
            opt = "multiplier"

        block_time = f"{datetime.datetime.fromtimestamp(int(block_timestamp)):%Y-%m-%d %H:%M:%S}"

        print("{} {} {} {}::{}".format(block_num, block_time, contract_addr, module_name,
                                       function_name))

        return UserOpt(block_num, sender, opt, block_time, amount)

    except Exception as e:
        if not isinstance(e, ValueError):
            print("{} {} parse error".format(block_num, txn_hash))

    return None


def parse_blocks(start_num, end_num):
    user_opts = list()
    for i in range(start_num, end_num):
        block = cli.get_block_by_number(i)

        if len(block["body"]["Full"]) <= 0:
            continue

        timestamp = block["header"]["timestamp"]
        transactions = block["body"]["Full"]
        # print("block height: {}".format(i))
        for txn in transactions:
            opt = parser_txn(txn, i, timestamp)
            if opt is None:
                continue

            user_opts.append(opt)
    return user_opts


def get_transactions_between(start_num, end_num) -> list:
    if start_num > end_num:
        raise RuntimeError("Invalid parameter")

    return parse_blocks(start_num, end_num)


def save_to_file(file_name, opts):
    csv_columns = ["block_num", "sender", "opt", "opt_time", "amount"]
    csv_file = file_name
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in opts:
                writer.writerow(data.__dict__)
    except IOError:
        print("I/O error")


def do_crawl(begin_block_num, end_block_num):
    return get_transactions_between(begin_block_num, end_block_num)
    # save_to_file("output.csv", opts)


BLOCK_NUM_RANGES = [
    {"start": 4530000, "end": 4532000},
    {"start": 4532000, "end": 4534000},
    {"start": 4534000, "end": 4536000},
    {"start": 4534800, "end": 4540000},
    {"start": 4540000, "end": 4542000},
]


def main():
    opts = list()
    cnt = len(BLOCK_NUM_RANGES)
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=cnt) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(do_crawl, r.get('start'), r.get('end')): r for r in BLOCK_NUM_RANGES}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                opts.extend(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                print('%r page is %d bytes' % (url, len(data)))

    save_to_file("out.csv", opts)


if __name__ == '__main__':
    starswap_decode_script.init_custom_decode_function()
    main()
    # crawl_all_user_options(begin_block_num=4535000, end_block_num=4540000)
    # do_crawl(begin_block_num=4530000, end_block_num=4540000)
