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
import os.path
import random
import unittest
import trio
from enum import IntEnum

from util import skvbc as kvbc
from util.bft import with_trio, with_bft_network, KEY_FILE_PREFIX

class OperationResult(IntEnum):
    SUCCESS = 0
    UNKNOWN = 1
    INVALID_REQUEST = 2
    NOT_READY = 3
    TIMEOUT = 4
    EXEC_DATA_TOO_LARGE = 5
    EXEC_DATA_EMPTY = 6
    CONFLICT_DETECTED = 7
    OVERLOADED = 8
    INTERNAL_ERROR = 9

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

class SkvbcBftErrorTest(unittest.TestCase):
    @with_trio
    @with_bft_network(start_replica_cmd)
    async def test_results_from_replicas(self, bft_network):
        """
        Test that a replica succeeds to ask for missing info from the former window

        1. Start all replicas but the primary
        2. Make sure that eventually we are able to add blocks
        """

        bft_network.start_all_replicas()
        client = bft_network.random_client()
        skvbc = kvbc.SimpleKVBCProtocol(bft_network)
        
        key = skvbc.random_key()
        value = skvbc.random_value()
        kv_pair = [(key, value)]

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.SUCCESS)
        print("SS-- raw reply", reply[0], "OperationResult.SUCCESS(0) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.UNKNOWN)
        print("SS-- raw reply", reply[0], "OperationResult.UNKNOWN(1) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.INVALID_REQUEST)
        print("SS-- raw reply", reply[0], "OperationResult.INVALID_REQUEST(2) Result: ",reply[1])   

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.NOT_READY)
        print("SS-- raw reply", reply[0], "OperationResult.NOT_READY(3) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.TIMEOUT)
        print("SS-- raw reply", reply[0], "OperationResult.TIMEOUT(4) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.EXEC_DATA_TOO_LARGE)
        print("SS-- raw reply", reply[0], "OperationResult.EXEC_DATA_TOO_LARGE(5) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.EXEC_DATA_EMPTY)
        print("SS-- raw reply", reply[0], "OperationResult.EXEC_DATA_EMPTY(6) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.CONFLICT_DETECTED)
        print("SS-- raw reply", reply[0], "OperationResult.CONFLICT_DETECTED(7) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.OVERLOADED)
        print("SS-- raw reply", reply[0], "OperationResult.OVERLOADED(8) Result: ",reply[1])

        reply = await client.write(skvbc.write_req([], kv_pair, 0), result=OperationResult.INTERNAL_ERROR)
        print("SS-- raw reply", reply[0], "OperationResult.INTERNAL_ERROR(9) Result: ",reply[1])

if __name__ == '__main__':
    unittest.main()