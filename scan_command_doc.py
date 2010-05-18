#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import token
from tokenize import COMMENT, generate_tokens
from cStringIO import StringIO
    
def _load_yaml_dict(stream):
    # XXX: not YAML compatible
    data = {}
    key = None
    value = StringIO()
    def update_dict(key,value):
        if key and value.tell():
            data[key] = value.getvalue()
            value.truncate(0)
    for line in stream:
        line = line.rstrip()
        if not line:
            continue
        elif line[-1] == ':':
            update_dict(key, value)
            key = line[:-1]
        elif line.startswith(' '):
            value.write(line + os.linesep)
    else:
        update_dict(key, value)
    return data

def _dump_yaml_dict(stream, data):
    # XXX: not YAML compatible
    for key,value in data.iteritems():
        stream.write(key + ':' + os.linesep)
        for line in value.splitlines():
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                line = "#" + line
            line += os.linesep
            stream.write("  %s" % line)
        stream.write(os.linesep)

def scan_doc(filepath):
    is_def_next = False
    comment = StringIO()
    for tok in generate_tokens(open(filepath).readline):
        t_type, t_data, t_begin, t_end, line = tok
        if t_type == COMMENT:
            line = t_data.strip('# ').strip()
            if not line:
                continue
            # Skip thise unexpected comments.
            if line[0] == line[-1] == '-':
                continue
            if line[0] == '"':
                continue
            line = line.replace('-#', '-')
            comment.write(line + os.linesep)
        elif t_type == token.NAME:
            if t_data == 'def':
                is_def_next = True
                continue
            if is_def_next:
                is_def_next = False
                if t_data.startswith('command_'):
                    yield t_data, comment.getvalue()
                comment.truncate(0)
        elif t_type == token.NEWLINE:
            comment.truncate(0)
    
def update_doc(srcpath, outfile):
    from pprint import pprint
    from glob import glob
    
    docs = {}
    for filepath in glob(srcpath + '/*.py'):
        data = scan_doc(filepath)
        docs.update(data)
    try:
        import yaml
        #yaml.safe_dump(docs,
        #                stream=open(outfile,'wb'),
        #                allow_unicode=True,
        #                default_flow_style=False)
        _dump_yaml_dict(open(outfile,'wb'), docs)
        docs = yaml.safe_load(open(outfile))
    except ImportError:
        _dump_yaml_dict(open(outfile,'wb'), docs)
        docs = _load_yaml_dict(open(outfile))
        pprint((docs))

def main(srcdir, outfile):
    update_doc(srcdir, outfile)

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])
    