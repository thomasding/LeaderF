#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
from .utils import *
from .explorer import *
from .manager import *


#*****************************************************
# AnyExplorer
#*****************************************************
class AnyExplorer(Explorer):
    def __init__(self):
        pass

    def getContent(self, *args, **kwargs):
        pass

    def getStlCategory(self):
        return 'Buffer'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return True

"""
g:Lf_
"""
#*****************************************************
# AnyExplManager
#*****************************************************
class AnyExplManager(Manager):
    def __init__(self):
        super(AnyExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return AnyExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Any#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
        lfCmd("hide buffer %d" % buf_number)

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ''
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return line[prefix_len:]
        elif mode == 1:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            return basename if basename else "[No Name]"
        else:
            start_pos = line.find(' "')
            return line[start_pos+2 : -1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if not line:
            return 0
        prefix_len = self._getExplorer().getPrefixLength()
        if mode == 0:
            return prefix_len
        elif mode == 1:
            return prefix_len
        else:
            buf_number = int(re.sub(r"^.*?(\d+).*$", r"\1", line))
            basename = getBasename(vim.buffers[buf_number].name)
            space_num = self._getExplorer().getMaxBufnameLen() \
                        - int(lfEval("strdisplaywidth('%s')" % escQuote(basename)))
            return prefix_len + lfBytesLen(basename) + space_num + 2

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" d : wipe out buffer under cursor')
        help.append('" D : delete buffer under cursor')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(AnyExplManager, self)._afterEnter()
        id = int(lfEval("matchadd('Lf_hl_bufNumber', '^\s*\zs\d\+')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufIndicators', '^\s*\d\+\s*\zsu\=\s*[#%]\=...')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufModified', '^\s*\d\+\s*u\=\s*[#%]\=.+\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_bufNomodifiable', '^\s*\d\+\s*u\=\s*[#%]\=..-\s*\zs.*$')"))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_bufDirname', ' \zs".*"$')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(AnyExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []




#*****************************************************
# anyExplManager is a singleton
#*****************************************************
anyExplManager = AnyExplManager()

__all__ = ['anyExplManager']
