import json
from dataclasses import dataclass
from datetime import datetime

from starcoin import bcs, serde_types as st, starcoin_types


@dataclass(frozen=True)
class TokenCode:
    addr: starcoin_types.AccountAddress
    module_name: bytes
    name: bytes


@dataclass(frozen=True)
class BuyBackEvent:
    sell_token_code: TokenCode
    buy_token_code: TokenCode
    sell_amount: st.uint128
    buy_amount: st.uint128
    user: starcoin_types.AccountAddress

    def bcs_serialize(self) -> bytes:
        return bcs.serialize(self, BuyBackEvent)

    @staticmethod
    def bcs_deserialize(input_s: bytes) -> 'BuyBackEvent':
        v, buffer = bcs.deserialize(input_s, BuyBackEvent)
        if buffer:
            raise st.DeserializationError("Some input bytes were not read")
        return v


def main(file_name, start_time, end_time):
    with open(file_name, 'r') as f:
        data = json.load(f)
        hits_array = data['hits']['hits']
        print("Array length: {} ".format(len(hits_array)))

        total_stc_amount = 0
        total_star_amount = 0
        total_count = 0
        for hits in hits_array:
            source = hits["_source"]
            timestamp = source['timestamp'] / 1000
            try:
                payload = source['data']
                payload = bytes.fromhex(payload[2:])
                payload = BuyBackEvent.bcs_deserialize(payload)
                if start_time <= timestamp <= end_time:
                    total_stc_amount = total_stc_amount + int(payload.buy_amount)
                    total_star_amount = total_star_amount + int(payload.sell_amount)
                    total_count += 1
            except Exception as e:
                print("Err: {}".format(e))

        print("Start time: {}, end time: {}, Total STC amount: {}, Total STAR amount: {}, Total count: {}".format(
            datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
            datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'),
            total_stc_amount / 1e9,
            total_star_amount / 1e9,
            total_count)
        )


if __name__ == '__main__':
    main("~/Downloads/buyback-events.json", 1672502400, 1673280000)
