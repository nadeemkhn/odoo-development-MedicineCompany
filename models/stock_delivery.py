from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockDelivery(models.Model):
    _name = 'stock.delivery'
    _rec_name = 'sequence'

    sequence = fields.Char(string='Delivery Sequence', copy=False, )
    partner_id = fields.Many2one(
        'medical.customer' , string='Customer',
    )
    supplier_id = fields.Many2one('medical.supplier', string='Supplier')
    stock_delivery = fields.One2many('stock.delivery.line', 'stock_id')
    Schedule_date = fields.Date(string="Schedule Date")
    confirm_date = fields.Date(string="Confirm Date")
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('sent', 'Ready'),
                   ('done', 'Done'),
                   ('sale', 'Sale Order'),
                   ('cancel', 'cancelled'),
                   ('validate', 'Validate')
                   ],
        required=False, default="draft")
    picking_type = fields.Selection(
        [('purchase', 'Purchase'), ('sale', 'Sale')],
        string="Picking Type", readonly=True)



    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    def action_waiting(self):
        self.state = 'sent'

    def action_done(self):
        self.state = 'done'

    def action_sale(self):
        self.state = 'sale'

    def action_validate(self):
        if self.picking_type == 'sale':
            for line in self.stock_delivery:
                if line.done_qty <= 0:
                    raise ValidationError('Done quantity is not update')
                if line.done_qty > line.demand_qty:
                    raise ValidationError('done Quantity greater then demand')
                product = line.product_id
                product.stock -= line.done_qty
        elif self.picking_type == 'purchase':
            for rec in self.stock_delivery:
                if rec.done_qty > rec.demand_qty:
                    raise ValidationError('done Quantity greater then demand')
                product = rec.product_id
                product.stock += rec.done_qty

        self.state = 'validate'


    @api.model
    def create(self, vals):
        if vals.get('picking_type') == 'purchase':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('stock.delivery.purchase')
        elif vals.get('picking_type') == 'sale':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('stock.delivery.sale')
        return super(StockDelivery, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'validate':
                raise ValidationError('you cant delete this because it already done')

        return super(StockDelivery, self).unlink()


class StockOrder(models.Model):
    _name = 'stock.delivery.line'

    stock_id = fields.Many2one('stock.delivery')
    product_id = fields.Many2one('medical.medicine', string='Product')
    demand_qty = fields.Integer(string='Demand Quantity')
    done_qty = fields.Integer(string='Done Quantity')
    price = fields.Float(string='unit price')
    sub_total = fields.Float(string='Sub Total', compute='_compute_sub_total')

    @api.depends('done_qty', 'price')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.done_qty * rec.price
