from odoo import models, fields

class Customer(models.Model):
    _name = 'medical.customer'
    _description = 'Customer'

    name = fields.Char('Customer Name')
    contact_info = fields.Char('Contact Information')
    address = fields.Text('Address')
    created_at = fields.Datetime('Created At', default=fields.Datetime.now)

