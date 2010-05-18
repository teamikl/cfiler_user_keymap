# -*- coding: utf-8 -*

from cStringIO import StringIO
from unittest import TestCase

from cfiler_misc import KeyEvent, ChrEvent
import user_keymap

class TestPublicFunctions(TestCase):
    # TODO: install, dump, iter_keymap, compile_key
    pass

class TestPublicDecorators(TestCase):
    # TODO: set_command_decorator, set_keyevent_decorator
    pass

class TestKeyMapTable(TestCase):
    def test_vk(self):
        # TODO
        pass
    
    def test_modkey(self):
        modkey_map = user_keymap._mod_map
        self.assertEquals(4, len(modkey_map))
        self.assertEquals(u'MODKEY_ALT', modkey_map[1])
        self.assertEquals(u'MODKEY_CTRL', modkey_map[2])
        self.assertEquals(u'MODKEY_SHIFT', modkey_map[4])
        self.assertEquals(u'MODKEY_WIN', modkey_map[8])

class TestParser(TestCase):
    def test_rc_reader(self):
        # NOTE: cStringIO.StringIO(unicode) doesn't pass this test.
        # Python3.0 io.StringIO(bytes) raises TypeError.
        rc_reader = user_keymap._rc_reader
        stream = StringIO("#comment\n\ncommand_Foo = Shift+J")
        lines = list(rc_reader(stream))
        self.assertEquals(1,                        lines[0][0])
        self.assertEquals(u'#comment',              lines[0][1])
        self.assertEquals(2,                        lines[1][0])
        self.assertEquals(u'',                      lines[1][1])
        self.assertEquals(3,                        lines[2][0])
        self.assertEquals(u'command_Foo = Shift+J', lines[2][1])
        self.assertEquals(3, len(lines))
    
    def test_parse_tokens(self):
        ParserError = user_keymap.ParserError
        parse_tokens = user_keymap._parse_tokens
        self.assertEquals(None, parse_tokens(u'# comment is ignored'))
        self.assertEquals(None, parse_tokens(u''))
        self.assertEquals((u'command_H', [u'Shift+H']),
                            parse_tokens([u'command_H',u'=',u'Shift+H']))
        self.assertRaises(ParserError, lambda: parse_tokens(u'!'))
        
    def test_scan_keys(self):
        InvalidKeyError = user_keymap.InvalidKeyError
        scan_keys = user_keymap._scan_keys
        self.assertEquals([u'Alt',u'J'], scan_keys([u'Alt+J']))
        self.assertEquals([u'Alt',u'J'], scan_keys([u'Alt',u'+',u'J']))
        self.assertEquals([u'Alt',u'J'], scan_keys([u'Alt',u'J']))
        
    def test_compile_key_event(self):
        # TODO
        pass
    
class TestUtilityFunctions(TestCase):
    def test_strcat(self):
        strcat = user_keymap._strcat
        self.assertEquals(u'a b', strcat([u'a', u'b']))
        self.assertRaises(TypeError, lambda: strcat([1,2]))
        
    def test_ignore_empty(self):
        ignore_empty = user_keymap._ignore_empty
        self.assertEquals([1,2], list(ignore_empty([1,0,2])))
        
    def test_compose(self):
        compose = user_keymap._compose
        func = compose(lambda x:x+5, lambda x:x*10)
        self.assertEquals(100, func(5))

class TestResourceException(TestCase):
    def test_subclass(self):
        func = lambda x: issubclass(x, user_keymap.ResourceError)
        self.assertTrue(func(user_keymap.InvalidKeyError))
        self.assertTrue(func(user_keymap.CommandNotFound))
        self.assertTrue(func(user_keymap.ParserError))
        self.assertFalse(func(StandardError))
        
class TestConstantTable(TestCase):
    def test_check_value(self):
        from user_keymap import TOKEN, MSGFMT, ATTR, PREFIX
        self.assertEquals(u'#', TOKEN.COMMENT)
        self.assertEquals(u'=', TOKEN.ASSIGN)
        self.assertEquals(u'+', TOKEN.PLUS)
        self.assertEquals(u'selected', ATTR.SELECTED)
        self.assertEquals(u'noselect', ATTR.NOSELECT)
        self.assertEquals(u'ignore', ATTR.IGNORE)
        self.assertEquals(u'command_', PREFIX.COMMAND)
        self.assertEquals(u'VK_', PREFIX.VK)
        self.assertEquals(u'MODKEY_', PREFIX.MODKEY)
        # No need to check MSGFMT
        
def main():
    import sys
    if 'xconsole' in sys.modules:
        MyScintilla = getattr(sys.modules['xconsole'], 'MyScintilla', None)
        if MyScintilla and not hasattr(MyScintilla, 'flush'):
            MyScintilla.flush = lambda self:None
    
    from unittest import makeSuite, TestSuite, TextTestRunner
    TextTestRunner(verbosity=2).run(TestSuite(
        makeSuite(v) for k,v in globals().items() if k.startswith('Test')
    ))
    