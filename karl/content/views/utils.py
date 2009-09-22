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

import re

from lxml.etree import XMLSyntaxError
from lxml.html import document_fromstring

from repoze.lemonade.content import create_content
from repoze.bfg.url import model_url

from zope.component import getMultiAdapter

from karl.content.interfaces import ICommunityFile
from karl.content.views.interfaces import IFileInfo

from karl.views.utils import basename_of_filepath
from karl.views.utils import make_unique_name
from karl.views.utils import check_upload_size

def fetch_attachments(attachments_folder, request):
    return [getMultiAdapter((attachment, request), IFileInfo)
                   for attachment in attachments_folder.values()]

def store_attachments(attachments_folder, params, creator):
    """Given some request data, pick apart and store attachments"""

    # Get the attachments out of the form data.  We do iteritems
    # becauser there might be multiple with the name prefixed by
    # attachment.
    new_attachments = []
    for key, value in params.iteritems():
        if key.startswith('attachment') and value != '':
            new_attachments.append(value)

    # Iterate through the new attachments and create content to store in
    # the attachments folder.
    for attachment in new_attachments:
        filename = make_unique_name(attachments_folder,
                                    basename_of_filepath(attachment.filename))
        attachments_folder[filename] = obj = create_content(
            ICommunityFile,
            title = filename,
            stream = attachment.file,
            mimetype = attachment.type,
            filename = filename,
            creator = creator,
            )
        check_upload_size(attachments_folder, obj, 'attachment')


def get_previous_next(context, request):

    # Reference Manual sections have inter-item navigation, which
    # means (sigh) that files and pages do as well.

    # Only works on resources whose parents are orderable
    parent = context.__parent__
    ordering = getattr(parent, 'ordering', None)
    if ordering is None:
        return None, None

    # Be a chicken and sync
    ordering.sync(parent.keys())

    # Find the prev/next names, then flatten some info about them for
    # the ZPT
    current_name = context.__name__
    previous = parent.get(ordering.previous_name(current_name))
    next = parent.get(ordering.next_name(current_name))

    if previous:
        previous = {'title': previous.title,
                    'href': model_url(previous, request)}
    if next:
        next = {'title': next.title,
                    'href': model_url(next, request)}

    return previous, next


from karl.content.views.interfaces import IShowIsPrivate
from zope.component import queryMultiAdapter

def get_show_is_private(context, request, form=None):
    # Get the policy, if any, on whether to hide the "Is Private"
    # field (for OSI, inside private communities.)
    adapter = queryMultiAdapter((context, request), IShowIsPrivate)
    if adapter is not None:
        show_is_private = adapter()
    else:
        show_is_private = True
    if show_is_private and form is not None:
        # Add a field to the form
        from karl.views.baseforms import sharing
        form.add_field('sharing', sharing)
    return show_is_private

def add_security_state_field(context, request, form=None):
    # Get the policy, if any, on whether to hide the security state
    # field
    adapter = queryMultiAdapter((context, request), IShowIsPrivate)
    if adapter is not None:
        show_field = adapter()
    else:
        show_field = True
    if show_field and form is not None:
        # Add a field to the form
        from karl.views.baseforms import security_state
        form.add_field('security_state', security_state)
    return show_field
    
def extract_description(htmlstring):
    """ Get a summary-style description from the HTML in text field """
    # XXX This gets called from other units, and therefore gets tested
    #     indirectly, but a unit test for this guy couldn't hurt.

    # Lots of resources don't have a user-visible description field,
    # which is good, as it is one less field for authors to be
    # confronted with.  We still need a description to show in blog
    # listing and search results, for example.  So extract a
    # description from the HTML text.

    summary_limit = 50 # number of "words"

    try:
        doc = document_fromstring(htmlstring)
    except XMLSyntaxError:
        return u''

    words = []
    for node in doc.xpath("//text()"):
        clean_node = node.strip()
        # strip wiki links
        clean_node = re.sub(r'[(][(]([^)]+)[)][)]', r'\1', clean_node)
        # simplify whitespace
        if clean_node:
            for word in clean_node.split():
                clean_word = word.strip()
                if clean_word:
                    words.append(clean_word)
    summary_list = words[0:summary_limit]
    summary = " ".join(summary_list)
    if len(words) > summary_limit:
        summary = summary + "..."

    return summary