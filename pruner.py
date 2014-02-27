#!/usr/bin/env python

from __future__ import print_function
import sys
import argparse
import re
import os.path
import mimetypes

def strip_and_write(src_fp, dest_filepath):
    with open(dest_filepath, 'w') as dest_fp:
        src_fp.seek(0)
        for line in src_fp:
            line = re.sub(r'[\t]+', '    ', line.rstrip())
            dest_fp.write( line + '\n' )
#end strip_and_write

def contains_bad_whitespace(file_p):
    for line in file_p:
        if re.search(r"[ \t\f\r]+$", line):
            return True
        elif re.search(r"[\t]", line):
            return True

    return False
#end contains_bad_whitespace

class action_prune_whitespace:

    def __init__(self, verbose = False):
        self.verbose = verbose

    def __call__(self, input_file):
        with open(input_file, 'r') as in_file:
            (file_type, file_encoding) = mimetypes.guess_type(input_file)
            if not file_type:
                if self.verbose:
                    print('WARNING: Ignoring file ' + input_file + ' because it\'s type cannot be determined.', file=sys.stderr)
            elif file_type.split('/')[0] == 'text':
                if contains_bad_whitespace(in_file):
                    tmp_filepath = os.path.dirname(input_file) + "." + os.path.basename(input_file) + '_tmp'
                    strip_and_write(in_file, tmp_filepath)
                    os.rename(tmp_filepath, input_file)
            elif self.verbose:
                print('WARNING: Ignoring file ' + input_file + ' because appears to be a non-text type (' + file_type.split('/')[0] + ')', file=sys.stderr)
# end action_prune_whitespace

class action_print_if_contains_whitespace:

    def __init__(self, verbose = False):
        self.verbose = verbose

    def __call__(self, input_file):
        with open(input_file, 'r') as in_file:
            (file_type, file_encoding) = mimetypes.guess_type(input_file)
            # definitely avoid non-text files!
            if not file_type:
                if self.verbose:
                    print('WARNING: Ignoring file ' + input_file + ' because it\'s type cannot be determined.', file=sys.stderr)
            elif file_type.split('/')[0] == 'text':
                if contains_bad_whitespace(in_file):
                    print(input_file)
            elif self.verbose:
                print('WARNING: Ignoring file ' + input_file + ' because appears to be a non-text type (' + file_type.split('/')[0] + ')', file=sys.stderr)
#end action_print_if_contains_whitespace

def process(input_file_list, action, verbose = False):
    for input_file in input_file_list:
        if not os.path.exists(input_file):
            if verbose:
                print('WARNING: File ' + input_file + ' does not exist or is inaccessible, so it was ignored!', file=sys.stderr)
            continue

        if os.path.islink(input_file):
            if verbose:
                print('WARNING: Not following link: ' + input_file + '!', file=sys.stderr)
            continue

        if os.path.isdir(input_file):
            (dirpath, dirs, files) = os.walk(input_file).next()
            filepaths = [ os.path.join(dirpath, filename) for filename in files ]
            dirpaths = [ os.path.join(dirpath, dirname) for dirname in dirs ]
            process(filepaths + dirpaths, action)
        else:
            action(input_file)
#end process

def main():
    parser = argparse.ArgumentParser('Whitespace Remover')
    parser.add_argument('-D', '--detect', action='store_true', help='Print the names of any files containing undesired whitespace')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print any warnings normally suppressed (such as about ignored files or directories)')
    parser.add_argument('input_files', nargs='+')

    args = parser.parse_args()

    if args.detect:
        action = action_print_if_contains_whitespace(args.verbose)
    else:
        action = action_prune_whitespace(args.verbose)

    process(args.input_files, action, args.verbose)

    return 0
# end main()

if __name__ == '__main__':
    sys.exit( main() )
