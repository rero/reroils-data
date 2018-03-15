# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 RERO.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, RERO does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""API for manipulating items associated to a document."""

from copy import deepcopy

from invenio_circulation.api import Item
from invenio_records.api import Record

from .models import DocumentsItemsMetadata


class ItemsMixin(object):
    """Implement items attribute for Document models.

    .. note::
       This is a prototype.
    """

    def add_item(self, item):
        """Add an Item."""
        DocumentsItemsMetadata.create(document=self.model, item=item.model)

    @property
    def itemslist(self):
        """Return an array of Item."""
        if self.model is None:
            raise MissingModelError()

        documents_items = DocumentsItemsMetadata.query.filter_by(
            document_id=self.id)
        to_return = []
        for doc_item in documents_items:
            item = Item.get_record(doc_item.item.id)
            to_return.append(item)
        return to_return


class DocumentsWithItems(Record, ItemsMixin):
    """Define API for files manipulation using ``ItemsMixin``."""

    def dumps(self, **kwargs):
        """Return pure Python dictionary with record metadata."""
        data = deepcopy(dict(self))
        data['itemslist'] = self.itemslist
        return data