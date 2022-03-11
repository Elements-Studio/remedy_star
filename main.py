#!/bin/bash
import concurrent
import concurrent.futures
import datetime

from starcoin.sdk import client, utils
from starcoin import starcoin_types, starcoin_stdlib

import cal_rem_harvest, cal_rem_addliq
from utils import file_util, time_util

import starswap_decode_script


class UserOpt:
    def __init__(self, block_num, txn_hash, sender, opt, opt_time, token_x, token_y, amount):
        self.block_num = block_num
        self.txn_hash = txn_hash
        self.token_x = token_x
        self.token_y = token_y
        self.sender = sender
        self.opt = opt
        self.opt_time = opt_time
        self.amount = amount


def parse_module_address(payload) -> str:
    return "0x" + ''.join([hex(i)[2:] for i in payload.value.module.address.value])


class CrawlTask:

    def __init__(self, begin_block_num, end_block_num):
        self.cli = client.Client("https://main-seed.starcoin.org")
        self.begin_block_num = begin_block_num
        self.end_block_num = end_block_num

    def parse_deposit_amount_from_remove_liquidity_txn(self, txn_hash):
        result = list()
        events = self.cli.get_events_by_txn_hash(txn_hash)
        for event in events:
            type_tag = event["type_tag"]
            if "DepositEvent" not in type_tag:
                continue

            event_data = event["data"][2:]
            data = starcoin_types.DepositEvent.bcs_deserialize(
                bytes.fromhex(event_data))
            result.append(int(data.amount))
        return result

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
            token_x_tag, token_y_tag = function_call.get_x_y()
            opt = ''

            # if isinstance(function_call, starswap_decode_script.ScriptFunctionCall__stake):
            #     opt = "stake"
            # elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__unstake):
            #     opt = "unstake"
            # elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__harvest):
            #     opt = "harvest"
            # elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__unstake):
            #     opt = "unstake"
            # elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__harvest):
            #     opt = "harvest"

            if isinstance(function_call, starswap_decode_script.ScriptFunctionCall__resetFarmActivation):
                opt = "activation"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__addLiquidity):
                opt = "add_liquidity"
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__removeLiquidity):
                opt = "remove_liquidity"
                amount = self.parse_deposit_amount_from_remove_liquidity_txn(txn_hash)
            elif isinstance(function_call, starswap_decode_script.ScriptFunctionCall__setFarmMultiplier):
                opt = "multiplier"
            else:
                return None

            block_time_str = time_util.unix_time_to_readable_string(block_timestamp)

            print(
                "Ok: {} {} {} {} {}::{}<{}, {}>".format(block_num, txn_hash, block_time_str, contract_addr, module_name,
                                                        function_name, token_x_tag, token_y_tag))

            return UserOpt(block_num, txn_hash, sender, opt, block_time_str, token_x_tag, token_y_tag, amount)

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
    task = CrawlTask(begin_block_num, end_block_num)
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

LIQUIDITY_CRAWL_FILE = 'datas/addliq-download-data.csv'


def crawl_from_blocks():
    starswap_decode_script.init_custom_decode_function()

    opts = list()
    cnt = len(BLOCK_NUM_RANGES)
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=cnt) as executor:
        # Start the load operations and mark each future with its URL
        threads = {executor.submit(do_crawl, r.get('start'), r.get('end')): r for r in BLOCK_NUM_RANGES}
        for future in concurrent.futures.as_completed(threads):
            th = threads[future]
            try:
                data = future.result()
                opts.extend(data)
            except Exception as exc:
                print('thread %r generated an exception: %s' % (th, exc))
            else:
                print('%r data count is %d' % (th, len(data)))

    file_util.save_to_file(LIQUIDITY_CRAWL_FILE, opts=opts)


def computer_harvest_model_from_csv_file():
    # computer STC::STC <-> STAR::STAR pair
    opts = file_util.read_from_file("datas/star-1.csv")
    star_users = cal_rem_harvest.computer_users(opts, begin_time="2022-03-05 09:37:39", end_time="2022-03-05 14:21:00",
                                                release_per_second=0.02, multiplier=30)
    file_util.save_to_file("datas/star-result.csv", list(star_users.values()))

    # computer STC::STC <-> FAI::FAI pair
    opts = file_util.read_from_file("datas/fai-1.csv")
    fai_users = cal_rem_harvest.computer_users(opts, begin_time="2022-03-05 09:37:00", end_time="2022-03-05 14:21:25",
                                               release_per_second=0.02, multiplier=10)
    file_util.save_to_file("datas/fai-result.csv", list(fai_users.values()))


def computer_addliq_model_from_csv_file():
    opts = file_util.read_from_file(LIQUIDITY_CRAWL_FILE)

    # computer STC::STC <-> FAI::FAI pair
    result_data = cal_rem_addliq.computer_users(opts, 'FAI::FAI', 100, 2)
    file_util.save_to_file("datas/addliq-fai-result.csv", list(result_data.values()))

    # computer STC::STC <-> STAR::STAR pair
    result_data = cal_rem_addliq.computer_users(opts, 'STAR::STAR', 1, 10)
    file_util.save_to_file("datas/addliq-star-result.csv", list(result_data.values()))


if __name__ == '__main__':
    crawl_from_blocks()
    # computer_from_csv_file()
    # computer_addliq_model_from_csv_file()
