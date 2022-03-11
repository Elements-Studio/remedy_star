import unittest

import starswap_decode_script
from main import CrawlTask


class MyTestCase(unittest.TestCase):
    def test_parse_block(self):
        starswap_decode_script.init_custom_decode_function()
        # 4534899
        task = CrawlTask(4534899, 4534901)
        opts = task.parse_blocks_to_opts()
        self.assertTrue(len(opts) > 0)

    def test_parse_event(self):
        txn_hash = '0x5ff72c21809fc171f4a74fafefbe7c802bb983d7f824e5e911775e3b58668554'
        task = CrawlTask(4534899, 4534901)
        x_amount, y_amount = task.parse_deposit_amount_from_remove_liquidity_txn(txn_hash)
        print(x_amount, y_amount)
        self.assertTrue(x_amount > 0, 'x amount is not equal 0')
        self.assertTrue(y_amount > 0, 'y amount is not equal 0')


if __name__ == '__main__':
    unittest.main()
