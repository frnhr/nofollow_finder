# coding=utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import threading
import os
import sys

# There is a bug in subprocess: https://bugs.python.org/issue20318
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


log = logging.getLogger(__name__)


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target(pipeline):
            log.debug('Thread started')
            log.debug('cmd: %s', self.cmd)
            self.process = subprocess.Popen(
                self.cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            log.debug('child pid: %d', self.process.pid)
            out, err = self.process.communicate()
            pipeline.append(self.process.returncode)
            pipeline.append(out)
            pipeline.append(err)
            log.debug('Thread finished')

        results = []
        thread = threading.Thread(target=target, args=(results,))
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            log.warning('Terminating process')
            self.process.terminate()
            thread.join()
            results = (1, '', '')
        return results  # (returncode, out, err)


def run(cmd, timeout=None):
    return Command(cmd).run(timeout=timeout)
