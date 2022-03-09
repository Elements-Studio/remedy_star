#!/bin/bash
import concurrent
import concurrent.futures
import datetime

from starcoin.sdk import client
from starcoin import starcoin_types, starcoin_stdlib

import computer_remedy
from utils import file_util

import starswap_decode_script


class UserOpt:
    def __init__(self, block_num, sender, opt, opt_time, token_x, token_y, amount):
        self.block_num = block_num
        self.token_x = token_x
        self.token_y = token_y
        self.sender = sender
        self.opt = opt
        self.opt_time = opt_time
        self.amount = amount


def parse_module_address(payload) -> str:
    return "0x" + ''.join([hex(i)[2:] for i in payload.value.module.address.value])


class Task:

    def __init__(self, begin_block_num, end_block_num):
        self.cli = client.Client("https://main-seed.starcoin.org")
        self.begin_block_num = begin_block_num
        self.end_block_num = end_block_num

    def parser_txn(self, txn, block_num, block_timestamp):
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
                # print("{} {} 's contract address not `0x8c109349c6bd91411d6bc962e080c4a3, {}::{}`.".format(block_num,
                #                                                                                            txn_hash,
                #                                                                                            module_name,
                #                                                                                            function_name))
                return None

            txn_info = self.cli.get_transaction_info(txn_hash)
            if "status" not in txn_info or txn_info["status"] != "Executed":
                print("Skip: {} {} 's state are not `Executed`. {}::{}".format(block_num, txn_hash, module_name,
                                                                               function_name))
                return None

            function_call = starcoin_stdlib.decode_script_function_payload(payload)
            amount = function_call.get_amount()
            token_x, token_y = function_call.get_x_y()
            opt = ''

            if isinstance(function_call, starswap_decode_script.ScriptFunctionCall__stake):
                opt = "stake"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__unstake):
                opt = "unstake"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__harvest):
                opt = "harvest"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__setFarmMultiplier):
                opt = "multiplier"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__resetFarmActivation):
                opt = "activation"

            block_time = f"{datetime.datetime.fromtimestamp(block_timestamp):%Y-%m-%d %H:%M:%S}"

            print("Ok: {} {} {} {}::{}<{}, {}>".format(block_num, block_time, contract_addr, module_name,
                                                       function_name, token_x, token_y))

            return UserOpt(block_num, sender, opt, block_time, token_x, token_y, amount)

        except Exception as e:
            if "Unknown script" not in e.__str__():
                print("Err: {} {} , txn: {}".format(block_num, e, txn_hash))
            pass

        return None

    def parse_blocks_to_opts(self):
        user_opts = list()
        for i in range(self.begin_block_num, self.end_block_num):
            block = self.cli.get_block_by_number(i)

            if len(block["body"]["Full"]) <= 0:
                continue

            timestamp = block["header"]["timestamp"]
            transactions = block["body"]["Full"]
            # print("block height: {}".format(i))
            for txn in transactions:
                opt = self.parser_txn(txn, i, int(timestamp) / 1000)
                if opt is None:
                    continue

                user_opts.append(opt)
        return user_opts


def do_crawl(begin_block_num, end_block_num):
    task = Task(begin_block_num, end_block_num)
    return task.parse_blocks_to_opts()


BLOCK_NUM_RANGES = [
    {"start": 4520000, "end": 4521000},
    {"start": 4521000, "end": 4522000},
    {"start": 4522000, "end": 4523000},
    {"start": 4523000, "end": 4524000},
    {"start": 4524000, "end": 4525000},
    {"start": 4525000, "end": 4526000},
    {"start": 4526000, "end": 4527000},
    {"start": 4527000, "end": 4528000},
    {"start": 4528000, "end": 4529000},
    {"start": 4529000, "end": 4530000},

    {"start": 4530000, "end": 4531000},
    {"start": 4531000, "end": 4532000},
    {"start": 4532000, "end": 4533000},
    {"start": 4533000, "end": 4534000},
    {"start": 4534000, "end": 4535000},
    {"start": 4535000, "end": 4536000},
    {"start": 4536000, "end": 4537000},
    {"start": 4537000, "end": 4538000},
    {"start": 4538000, "end": 4539000},
    {"start": 4539000, "end": 4540000},
    {"start": 4540000, "end": 4541000},

]


def crawl_from_blocks():
    starswap_decode_script.init_custom_decode_function()

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

    file_util.save_to_file("out.csv", opts)


def computer_from_csv_file():
    # computer STC::STC <-> STAR::STAR pair
    opts = file_util.read_from_file("star.csv")
    star_users = computer_remedy.computer_users(opts, 0.002)
    print(star_users)

    # # computer STC::STC <-> FAI::FAI pair
    # opts = file_util.read_from_file("fai.csv")
    # star_users = computer_remedy.computer_users()

    pass


if __name__ == '__main__':
    # crawl_from_blocks()
    computer_from_csv_file()
