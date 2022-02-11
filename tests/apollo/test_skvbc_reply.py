# Concord
#
# Copyright (c) 2019 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the Apache 2.0 license (the "License").
# You may not use this product except in compliance with the Apache 2.0 License.
#
# This product may include a number of subcomponents with separate copyright
# notices and license terms. Your use of these subcomponents is subject to the
# terms and conditions of the subcomponent's license, as noted in the LICENSE
# file.

import sys
import os.path
import random
import unittest
import trio

from util.test_base import ApolloTest

sys.path.append(os.path.abspath("../../util/pyclient"))

from util import skvbc as kvbc
from util.bft import with_trio, with_bft_network, KEY_FILE_PREFIX
import bft_msgs

SKVBC_INIT_GRACE_TIME = 2

def start_replica_cmd(builddir, replica_id):
    """
    Return a command that starts an skvbc replica when passed to
    subprocess.Popen.

    Note each arguments is an element in a list.
    """
    statusTimerMilli = "500"
    viewChangeTimeoutMilli = "10000"
    path = os.path.join(builddir, "tests", "simpleKVBC", "TesterReplica", "skvbc_replica")
    return [path,
            "-k", KEY_FILE_PREFIX,
            "-i", str(replica_id),
            "-s", statusTimerMilli,
            "-v", viewChangeTimeoutMilli,
            "-e", str(True)
            ]

class SkvbcReplyTest(ApolloTest):

    @with_trio
    @with_bft_network(start_replica_cmd, selected_configs=lambda n, f, c: c == 0 and n > 6)
    async def test_expected_replies_from_replicas(self, bft_network):

        """
        1. Launch a cluster
        2. Select a random client
        3. Send write request with an expected reply
        4. Expected result: The reply should be same as the expected reply sent with write client request message
        """

        bft_network.start_all_replicas()
        await trio.sleep(SKVBC_INIT_GRACE_TIME)
        client = bft_network.random_client()
        skvbc = kvbc.SimpleKVBCProtocol(bft_network)
        
        key = skvbc.random_key()
        value = skvbc.random_value()
        kv_pair = [(key, value)]

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.INVALID_REQUEST)
        assert reply[1] == bft_msgs.OperationResult.INVALID_REQUEST, \
                        f"Expected Reply={bft_msgs.OperationResult.INVALID_REQUEST}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.NOT_READY)
        print (reply)
        self.assertEqual(reply[1], bft_msgs.OperationResult.NOT_READY)
        assert reply[1] == bft_msgs.OperationResult.NOT_READY, \
                        f"Expected Reply={bft_msgs.OperationResult.NOT_READY}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.TIMEOUT)
        assert reply[1] == bft_msgs.OperationResult.TIMEOUT, \
                        f"Expected Reply={bft_msgs.OperationResult.TIMEOUT}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.EXEC_DATA_TOO_LARGE)
        assert reply[1] == bft_msgs.OperationResult.EXEC_DATA_TOO_LARGE, \
                        f"Expected Reply={bft_msgs.OperationResult.EXEC_DATA_TOO_LARGE}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.EXEC_DATA_EMPTY)
        assert reply[1] == bft_msgs.OperationResult.EXEC_DATA_EMPTY, \
                        f"Expected Reply={bft_msgs.OperationResult.EXEC_DATA_EMPTY}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.CONFLICT_DETECTED)
        assert reply[1] == bft_msgs.OperationResult.CONFLICT_DETECTED, \
                        f"Expected Reply={bft_msgs.OperationResult.CONFLICT_DETECTED}; actual={reply[1]}"

        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.OVERLOADED)
        assert reply[1] == bft_msgs.OperationResult.OVERLOADED, \
                        f"Expected Reply={bft_msgs.OperationResult.OVERLOADED}; actual={reply[1]}"
    
        reply = await client.write_with_result(skvbc.write_req([], kv_pair, 0), pre_process=True, result=bft_msgs.OperationResult.INTERNAL_ERROR)
        assert reply[1] == bft_msgs.OperationResult.INTERNAL_ERROR, \
                        f"Expected Reply={bft_msgs.OperationResult.INTERNAL_ERROR}; actual={reply[1]}"


if __name__ == '__main__':
    unittest.main()