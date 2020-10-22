from __future__ import unicode_literals

from frappe import _


def get_data():
	return {
		'fieldname': 'party',
		'transactions': [
			{
				'label': _('Sell'),
				'items': ['Sales Invoice']
			},
			{
				'label': _('Buy'),
				'items': ['Purchase Invoice']
			}
		],
		'reports': [
			{
				'label': _('Reports'),
				'items': ['General Ledger']
			}
		]
	}
