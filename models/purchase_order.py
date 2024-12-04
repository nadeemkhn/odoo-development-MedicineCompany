from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = 'medical.purchase.order'
    _description = 'Purchase Order'
    _rec_name = 'total_amount'

    supplier_id = fields.Many2one('medical.supplier', string='Supplier')
    medicine_line_ids = fields.One2many('medical.purchase.order.line', 'purchase_order_id', string='Medicine Lines')
    purchase_date = fields.Datetime('Purchase Date', default=fields.Datetime.now)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    sequence_purchase = fields.Char(string='Purchase Sequence', required=True, copy=False,
                                    default=lambda self: _('New'))

    state = fields.Selection([
        ('done', 'Done'),
        ('draft', 'Draft'),
        ('cancel', 'Cancelled')
    ], default='draft', string='Status', tracking=True)

    def action_done(self):
        for record in self:
            for line in record.medicine_line_ids:
                medicine = line.medicine_id
                medicine.cost_price = line.price  # Update the cost price
                medicine.stock += line.quantity
            record.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        for record in self:
            for line in record.medicine_line_ids:
                medicine = line.medicine_id
                medicine.stock -= line.quantity
            record.state = 'cancel'

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_purchase'] = self.env['ir.sequence'].next_by_code('medical.purchase.order') or _("New")
        return super(PurchaseOrder, self).create(vals)

    @api.depends('medicine_line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(rec.subtotal for rec in record.medicine_line_ids)


class PurchaseOrderLine(models.Model):
    _name = 'medical.purchase.order.line'
    _description = 'Purchase Order Line'

    purchase_order_id = fields.Many2one('medical.purchase.order', string='Purchase Order', )
    medicine_id = fields.Many2one('medical.medicine', string='Medicine', )
    quantity = fields.Integer('Quantity', default=1)
    price = fields.Float('Price', related='medicine_id.cost_price', )
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', )

    @api.onchange('medicine_id')
    def _onchange_medicine(self):
        if self.medicine_id:
            self.price = self.medicine_id.cost_price

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price
