# -*- coding: utf-8 -*-
#
# This file is part of items.
# Copyright (C) 2018 RERO.
#

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from __future__ import absolute_import, print_function

import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, \
    request, url_for
from flask_babelex import gettext as _
from flask_login import current_user
from flask_menu import register_menu
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.resolver import Resolver
from invenio_records_rest.utils import obj_or_import_string
from reroils_record_editor.permissions import record_edit_permission

from reroils_data.items.api import Item
from reroils_data.transactions.models import CircTransactions

from ..documents_items.api import DocumentsWithItems
from ..patrons.api import Patrons

blueprint = Blueprint(
    'reroils_data_items',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@blueprint.route("/items/loan", methods=['POST'])
@record_edit_permission.require()
def loan():
    """HTTP request for Item loan action."""
    try:
        data = request.get_json()
        pid_value = data.pop('pid')
        item_resolver = Resolver(pid_type='item',
                                 object_type='rec',
                                 getter=Item.get_record)
        pid, item = item_resolver.resolve(pid_value)
        doc = DocumentsWithItems.get_record_by_itemid(item.id)
        item.loan_item(**data)
        item.commit()
        db.session.commit()
        # TODO
        # RecordIndexer().index(item)
        RecordIndexer().index(doc)
        RecordIndexer().client.indices.flush()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error: %s' % e})


@blueprint.route("/items/return", methods=['POST'])
@record_edit_permission.require()
def return_item():
    """HTTP request for Item return action."""
    try:
        data = request.get_json()
        pid_value = data.pop('pid')
        item_resolver = Resolver(pid_type='item',
                                 object_type='rec',
                                 getter=Item.get_record)
        pid, item = item_resolver.resolve(pid_value)
        doc = DocumentsWithItems.get_record_by_itemid(item.id)
        item.return_item()
        item.commit()
        db.session.commit()
        # TODO
        # RecordIndexer().index(item)
        RecordIndexer().index(doc)
        RecordIndexer().client.indices.flush()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error: %s' % e})


@blueprint.route("/items/request/<pid_value>/<member>", methods=['GET'])
def get_request_item(pid_value, member):
    """HTTP GET request for Item request action."""
    # TODO: enhance the code of this function after applying task503
    try:
        patron = Patrons.get_patron_by_email(current_user.email)
        patron_barcode = patron['barcode']
        current_date = datetime.date.today()
        start_date = current_date.isoformat()
        end_date = (current_date + datetime.timedelta(days=45)).isoformat()
        item_resolver = Resolver(pid_type='item',
                                 object_type='rec',
                                 getter=Item.get_record)
        pid, item = item_resolver.resolve(pid_value)
        doc = DocumentsWithItems.get_record_by_itemid(item.id)
        item.request_item(
                patron_barcode=patron_barcode,
                member_pid=member,
                start_date=start_date,
                end_date=end_date
        )
        item.commit()
        db.session.commit()
        # TODO
        # RecordIndexer().index(item)
        RecordIndexer().index(doc)
        RecordIndexer().client.indices.flush()
        flash(_('The item %s has been requested.' % pid_value), 'success')
        return redirect(
            url_for('invenio_records_ui.doc', pid_value=doc['pid'])
        )
    except Exception as e:
        return jsonify({'status': 'error: %s' % e})
        flash(_('Something went wrong'), 'danger')


@blueprint.route("/items/request", methods=['POST'])
@record_edit_permission.require()
def post_request_item():
    """HTTP POST request for Item request action."""
    # TODO: recreate this function after applying task503
    try:
        data = request.get_json()
        pid_value = data.pop('pid')
        patron = Patrons.get_patron_by_email(current_user.email)
        data['patron_barcode'] = patron['barcode']
        current_date = datetime.date.today()
        start_date = current_date.isoformat()
        end_date = (current_date + datetime.timedelta(days=45)).isoformat()
        item_resolver = Resolver(pid_type='item',
                                 object_type='rec',
                                 getter=Item.get_record)
        pid, item = item_resolver.resolve(pid_value)
        doc = DocumentsWithItems.get_record_by_itemid(item.id)
        item.request_item(
                patron_barcode=patron_barcode,
                member_pid=member,
                start_date=start_date,
                end_date=end_date
        )
        item.commit()
        db.session.commit()
        # TODO
        # RecordIndexer().index(item)
        RecordIndexer().index(doc)
        RecordIndexer().client.indices.flush()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error: %s' % e})


@blueprint.route("/items/circulation")
@record_edit_permission.require()
@register_menu(
    blueprint,
    'main.manage.circulation',
    _('%(icon)s Circulation', icon='<i class="fa fa-barcode fa-fw"></i>'),
    order=-1
)
def circulation_ui():
    """Angular circulation application."""
    return render_template('reroils_data/circulation_ui.html')
