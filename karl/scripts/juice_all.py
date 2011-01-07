# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

""" Concatenate the javascript resources  """

import sys
import os
import karl.views
import subprocess

def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def module_path(mod, *rnames):
    return _concat_path(mod.__file__, *rnames)

def run_juicer(resource, output="min/"):
    attrs = ('juicer', 'merge', '-i', '--force', 
        '-o', os.path.join(os.path.dirname(resource), output), resource)
    print '##### Will run: ' + ' '.join(attrs) 
    subprocess.call(attrs)

def main(argv=sys.argv):
    if len(argv) > 1:
        raise RuntimeError, 'juice_all accepts no parameters.'
    static_dir = module_path(karl.views, 'static')
    tinymce_dir = module_path(karl.views, 'static', 'tinymce')

    run_juicer(os.path.join(static_dir, 'karl-ui.js')) 
    run_juicer(os.path.join(static_dir, 'karl-ui.css'))  

    run_juicer(os.path.join(tinymce_dir, 'tinymce-3.3.9.2.karl.js')) 
    run_juicer(os.path.join(tinymce_dir, 'tinymce-3.3.9.2.karl.css')) 

if __name__ == '__main__':
    main()
