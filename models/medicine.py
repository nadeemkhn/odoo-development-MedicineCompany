from odoo import models, fields, api, _
from pkg_resources import require


class Medicine(models.Model):
    _name = 'medical.medicine'
    _description = 'Medicine'

    name = fields.Char('Medicine Name', required=True)
    description = fields.Text('Description')
    cost_price = fields.Float('Purchase Price')
    margin = fields.Float(string='Margin (%)', default=10.0)
    sale_price = fields.Float(string='Sale Price', compute='_compute_sale_price', store=True)
    created_at = fields.Datetime('Created At', )
    stock = fields.Integer('Stock', default=0)
    medicine_seq = fields.Char(string='Medicine ID', required=True, copy=False,
                               default=lambda self: _('New'))

    @api.depends('cost_price', 'margin')
    def _compute_sale_price(self):
        for record in self:
            record.sale_price = int(record.cost_price * (1 + record.margin / 100))

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'name' in val:
                val['name'] = val['name'].title()

            val['medicine_seq'] = self.env['ir.sequence'].next_by_code('medical.medicine') or _("New")

        return super(Medicine, self).create(vals)
