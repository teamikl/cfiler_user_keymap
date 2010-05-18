# -*- coding: utf-8 -*-

使い方

----
# configure.py
    def configure(window):
        import user_keymap

        # 準備
        register_command = user_keymap.set_command_decorator(window)
        

        @register_command
        def command_ForceQuit():
            window.quit()
            

        # register_commandデコレータが自動的にwindowの属性に関数をセットします。
        # 関数の名前は、必ず 'command_' で始めること。
        # -> window.command_ForceQuit = command_ForceQuit



        # 登録した [key] = command の情報表示(debug用)
        # user_keymap.logger.setLevel(10)

        # キー定義ファイルを読み込む。(省略時は u'./extension/user_keymap.rc')
        user_keymap.install(window, u'./extension/user_keymap.rc')
        
        # 登録されているコマンド=キーの一覧をファイルに出力。
        # コンソールに出力させる場合は、sys.stdout等を第一引数へ渡す。
        # key=は、コマンド名順にソートする為のオプション。（省略可能） 
        #
        # user_keymap.dump(open('keymap.dump.txt','w'), window.keymap,
        #                  key=lambda x:window.keymap[x].__name__)

    
# ./extension/user.keymap

    # -> window.keymap[KeyEvent(ord('Q'), MODKEY_CTRL|MODKEY_ALT)] = command_ForceQuit

    ForceQuit = Ctrl+Alt Q


----
# User defined keymap resource. (sample)

ForceQuit                 = Ctrl + Alt + Q
SwapPane                  = Ctrl+X
Iconify                   = Ctrl Z
Console                   = F3

# Cursor
CursorTop                 = Home
CursorBottom              = End
CursorDown                = J
CursorUp                  = K
FocusLeftOrGotoParentDir  = H
FocusRightOrGotoParentDir = L


----
サンプルのため複数の方法で記述しています。

構文は適当。'#' で始まる行はコメント。
今の所はKeyEventのみサポート。キーの表記は '+' と空白文字区切り。
リテラルは、VK_HOME, VK_J 等も使えます。

ChrEventをサポートするときに変更もしくは拡張する予定。

注意
バージョン0.0.2 現在
user_keymap.dumpで出力した一覧は、user_keymap.installで取り込むことはできません。
バージョン0.0.3 で対応予定。

----
簡易キー登録デコレータ

    import user_keymap
    bindkey = user_keymap.set_keyevent_decorator(window.keymap)
    
    @bindkey('Ctrl + J')
    def command_Foo():
        ...

