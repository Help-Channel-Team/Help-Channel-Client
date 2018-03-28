# Run 'dispycosnode.py' program to start processes to execute computations sent
# by this client, along with this program.

# This example illustrates in-memory processing with 'node_setup' to read date
# in to memory. Remote tasks ('compute' in this case) then process data in
# memory. This example works with POSIX (Linux, OS X etc.), but not Windows. See
# 'dispycos_client9_server.py' which initializes each server to read data in to
# memory for processing in computations.

import pycos.netpycos as pycos
from pycos.dispycos import *

def node_available(avail_info, data_file, task=None):
    import os
    # 'node_available' is executed locally (at client) when a node is
    # available. 'location' is Location instance of node. When this task is
    # executed, 'depends' of computation would've been transferred.

    # data_file could've been sent with the computation 'depends'; however, to
    # illustrate how files can be sent separately (e.g., to transfer different
    # files to different nodes), file is transferred with 'node_available'.

    print('  Sending %s to %s' % (data_file, avail_info.location.addr))
    sent = yield pycos.Pycos().send_file(avail_info.location, data_file,
                                         overwrite=True, timeout=5)
    if (sent < 0):
        print('Could not send data file "%s" to %s' % (data_file, avail_info.location))
        raise StopIteration(-1)

    # value of task (last value yield'ed or value of 'raise StopIteration') will
    # be passed to node_setup as argument(s).
    yield computation.enable_node(avail_info.location.addr, data_file)

def node_setup(data_file):
    # 'node_setup' is executed on a node with the arguments returned by
    # 'node_available'. This task should return 0 to indicate successful
    # initialization.

    # variables declared as 'global' will be available (as read-only) in tasks.
    global os, hashlib, data, file_name
    import os, hashlib
    # note that files transferred to node are in parent directory of cwd where
    # each computation is run (in case such files need to be accessed in
    # computation).
    print('data_file: "%s"' % data_file)
    with open(data_file, 'rb') as fd:
        data = fd.read()
    os.remove(data_file)  # data_file is not needed anymore
    file_name = data_file
    yield 0  # task must have at least one 'yield' and 0 indicates success

# 'compute' is executed at remote server process repeatedly to compute checksum
# of data in memory, initialized by 'node_setup'
def compute(alg, n, task=None):
    global data, hashlib
    yield task.sleep(n)
    checksum = getattr(hashlib, alg)()
    checksum.update(data)
    raise StopIteration((file_name, alg, checksum.hexdigest()))

# local task to process status messages from scheduler
def status_proc(task=None):
    task.set_daemon()
    i = 0
    while 1:
        msg = yield task.receive()
        if not isinstance(msg, DispycosStatus):
            continue
        if msg.status == Scheduler.NodeDiscovered:
            pycos.Task(node_available, msg.info.avail_info, data_files[i])
            i += 1

def client_proc(computation, task=None):
    if (yield computation.schedule()):
        raise Exception('Could not schedule computation')

    # execute 10 jobs (tasks) and get their results. Note that number of jobs
    # created can be more than number of server processes available; the
    # scheduler will use as many processes as necessary/available, running one
    # job at a server process
    yield task.sleep(2)
    algorithms = ['md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512']
    args = [(algorithms[i % len(algorithms)], random.uniform(1, 3)) for i in range(15)]
    results = yield computation.run_results(compute, args)
    for i, result in enumerate(results):
        if isinstance(result, tuple) and len(result) == 3:
            print('   %ssum for %s: %s' % (result[1], result[0], result[2]))
        else:
            print('  rtask failed for %s: %s' % (args[i][0], str(result)))

    yield computation.close()


if __name__ == '__main__':
    import logging, random, functools, sys, os, glob
    # pycos.logger.setLevel(pycos.Logger.DEBUG)
    if os.path.dirname(sys.argv[0]):
        os.chdir(os.path.dirname(sys.argv[0]))
    # if scheduler is not already running (on a node as a program),
    # start private scheduler:
    Scheduler()

    data_files = glob.glob('dispycos_client*.py')

    # Since this example doesn't work with Windows, 'node_allocations' feature
    # is used to filter out nodes running Windows.
    node_allocations = [DispycosNodeAllocate(node='*', platform='Windows', cpus=0)]
    computation = Computation([compute], node_allocations=node_allocations,
                              status_task=pycos.Task(status_proc), node_setup=node_setup,
                              disable_nodes=True)
    pycos.Task(client_proc, computation)
