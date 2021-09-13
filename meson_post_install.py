#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (C) 2021 Iñigo Martinez <inigomartinez@gmail.com>

import os
import subprocess
import sys

prefix = os.environ['MESON_INSTALL_DESTDIR_PREFIX']

bindir = os.path.join(prefix, sys.argv[1])
subprocess.check_call(['chmod', '755', os.path.join(bindir, 'mbim-network')])

bash_completion_completionsdir = sys.argv[2]
if bash_completion_completionsdir:
    if not os.path.isabs(bash_completion_completionsdir):
        bash_completion_completionsdir = os.path.join(prefix, bash_completion_completionsdir)
    os.rename(os.path.join(bash_completion_completionsdir, 'mbimcli-completion'),
              os.path.join(bash_completion_completionsdir, 'mbimcli'))
