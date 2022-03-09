import unittest

import starswap_decode_script
from main import Task


class MyTestCase(unittest.TestCase):
    def test_parse_block(self):
        starswap_decode_script.init_custom_decode_function()
        # 4534899
        task = Task(4534899, 4534901)
        opts = task.parse_blocks_to_opts()
        self.assertTrue(len(opts) > 0)


if __name__ == '__main__':
    unittest.main()
