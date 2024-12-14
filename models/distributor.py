from odoo import models, fields

class Distributor(models.Model):
    _name = 'medical.distributor'
    _description = 'Distributor'

    name = fields.Char('Distributor Name', )
    contact_info = fields.Char('Contact Information')
    address = fields.Text('Address')
    created_at = fields.Datetime('Created At', default=fields.Datetime.now)

