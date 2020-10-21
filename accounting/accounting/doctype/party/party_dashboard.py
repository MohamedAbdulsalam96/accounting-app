from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'party',
		'transactions': [
			{
				'label': _('Invoices'),
				'items': ['Sales Invoice', 'Purchase Invoice', 'Payment Entry']
			}
		]
	}
