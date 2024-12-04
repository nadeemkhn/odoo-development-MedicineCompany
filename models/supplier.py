from odoo import models, fields

class Supplier(models.Model):
    _name = 'medical.supplier'
    _description = 'Supplier'

    name = fields.Char('Supplier Name', )
    contact_info = fields.Char('Contact Information')
    address = fields.Text('Address')
    created_at = fields.Datetime('Created At', default=fields.Datetime.now)
