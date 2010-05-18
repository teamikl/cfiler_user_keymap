# -*- coding: utf-8 -*-
"""Read keymap from User's resource file."""

__all__ = ['install', 'set_command_decorator', 'set_keyevent_decorator',
           'compile_key', 'iter_keymap', 'dump']
__version__ = '0.0.2'
#-------------------------------------------------------------------------------
import os
import shlex
import string
import logging

from cfiler_misc import KeyEvent, ChrEvent
from cterm import cterm_const as key_constants
#-------------------------------------------------------------------------------
DEFAULT_KEYMAP_PATH = u'./extension/user.keymap'
LOGGER_NAME = __file__

class TOKEN:
    COMMENT = u'#'
    ASSIGN = u'='
    PLUS = u'+'
    
class ATTR:
    IGNORE = u'ignore'
    SELECTED = u'selected'
    NOSELECT = u'noselect'
    
class MSGFMT:
    ERROR = u'行: %d 理由: %s'
    BIND_CMD = u'[%-16s]: command_%s'
    KEY_ASSIGN = u"%-40s = %s%s"
    
class PREFIX:
    COMMAND = u'command_'
    VK = u'VK_'
    MODKEY = u'MODKEY_'

KEY_SEP = TOKEN.PLUS
#-------------------------------------------------------------------------------
class ResourceError(Exception):
    @property
    def reason(self):
        return self.message % self.args
class ParserError(ResourceError):
    message = u'構文が間違っています。'
class CommandNotFound(ResourceError):
    message = u'コマンド(%s)が定義されていません。'
class InvalidKeyError(ResourceError):
    message = u'無効なキー定義です。(%s)'
#-------------------------------------------------------------------------------
logger = logging.getLogger(LOGGER_NAME)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)
#-------------------------------------------------------------------------------
_strcat = u' '.join
_ignore_empty = lambda xs: (x for x in xs if x)
_compose = lambda *xs: lambda arg: reduce(lambda x,f:f(x), xs, arg)

def _rc_reader(stream):
    for i,line in enumerate(stream):
        yield i+1, line.strip()

def _get_vk_or_ord(key):
    if len(key) == 1 and key in string.letters:
        return ord(key)
    _key = key.upper()
    if _key.startswith(PREFIX.VK) and hasattr(key_constants, _key):
        return getattr(key_constants, _key)
    if hasattr(key_constants, PREFIX.VK+_key):
        return getattr(key_constants, PREFIX.VK+_key)
    raise InvalidKeyError(key)

def _get_modkey(keys):
    mod = 0
    for key in keys:
        keyname = PREFIX.MODKEY + key.upper()
        if not hasattr(key_constants, keyname):
            raise InvalidKeyError(key)
        mod |= getattr(key_constants, keyname)
    return mod

def _compile_key_event(keys):
    vk = _get_vk_or_ord(keys[-1])
    mod = _get_modkey(keys[:-1])
    return KeyEvent(vk, mod)

def _scan_keys(keys):
    return [x for key in keys for x in key.split(TOKEN.PLUS) if x]

def _parse_tokens(tokens):
    assert isinstance(tokens, list)
    if not tokens or tokens[0] == TOKEN.COMMENT:
        return
    if len(tokens) >= 3 and tokens[1] == TOKEN.ASSIGN:
        return tokens[0], tokens[2:] # return command_name, key_tokens
    raise ParserError

def _parse_args(args):
    # Currently, KeyEvent only.
    # TODO: parse ChrEvent and item selected attr (ignore,selected,noselect)
    return args

compile_key = _compose(shlex.split,_parse_args,_scan_keys,_compile_key_event)
#-------------------------------------------------------------------------------
def install(target, rcfile=DEFAULT_KEYMAP_PATH):
    u"install(target : window object, rcfile : filepath of filelike object)"
    assert hasattr(target, 'keymap')
    rcfile = open(rcfile) if isinstance(rcfile,(str,unicode)) else rcfile
    assert hasattr(rcfile, '__iter__')

    for lineno,line in _rc_reader(rcfile):
        try:
            tokens = shlex.split(line)
            result = _parse_tokens(tokens)
            if not result:
                continue
            name,args = result
            keys = _parse_args(args)
            keys = _scan_keys(keys)
            key_evt = _compile_key_event(keys)
            command = getattr(target, PREFIX.COMMAND+name, None)
            if not command:
                raise CommandNotFound(name)
            target.keymap[key_evt] = command
            logger.debug(MSGFMT.BIND_CMD % (KEY_SEP.join(keys),name))
        except ResourceError as e:
            logger.error(MSGFMT.ERROR % (lineno, e.reason))    
#-------------------------------------------------------------------------------    
def _make_key_table(obj, prefix):
    return dict((getattr(obj,k) ,k) for k in dir(obj) if k.startswith(prefix))

_vk_map = _make_key_table(key_constants, PREFIX.VK)
_mod_map = _make_key_table(key_constants, PREFIX.MODKEY)
_vk_name = _vk_map.__getitem__
def _mod_name(v):
    return KEY_SEP.join(_mod_map[x] for x in sorted(_mod_map.keys()) if x&v)

def _select_repr(v):
    return ATTR.IGNORE if v is None else ATTR.SELECTED if v else ATTR.NOSELECT

def _key_repr(key):
    # TODO: repr ChrEvent and item selected attribute.
    _key = key.input_event
    if isinstance(_key, KeyEvent):
        return _mod_name(_key.mod), _vk_name(_key.vk), _select_repr(key.select)
    elif isinstance(_key, ChrEvent):
        logger.error(u'Sorry, ChrEvent is not supported, yet')
    return repr(_key)

del _make_key_table
#-------------------------------------------------------------------------------
def iter_keymap(keymap, **sort_options):
    logger.warn(u'Not support ChrEvent and item select arrtibute, yet')
    for k in sorted(keymap, **sort_options):
        yield keymap[k].__name__, k

def dump(out, keymap, **sort_options):
    for command_name,keys in iter_keymap(keymap,**sort_options):
        key = _strcat(_ignore_empty(_key_repr(keys)))
        out.write(MSGFMT.KEY_ASSIGN % (command_name, key, os.linesep))
#-------------------------------------------------------------------------------
def set_command_decorator(target):
    return lambda x: (setattr(target,x.__name__,x), x)[-1]

def set_keyevent_decorator(keymap):
    return lambda k: lambda x: (keymap.__setitem__(compile_key(k),x), x)[-1]
#-------------------------------------------------------------------------------