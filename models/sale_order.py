from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _name = 'medical.sale.order'
    _description = 'Sale Order'

    customer_id = fields.Many2one('medical.customer', string='Customer')
    medicine_line_ids = fields.One2many('medical.sale.order.line', 'sale_order_id', string='Medicine Lines')
    sale_date = fields.Datetime('Sale Date', default=fields.Datetime.now)
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    sequence_sale = fields.Char(string='Sale Sequence', copy=False, default=lambda self: _('New'))
    state = fields.Selection([
        ('done', 'Done'),
        ('draft', 'Draft'),
        ('cancel', 'cancelled')

    ],
        default='draft', string='status', tracking=True)

    def action_done(self):
        for record in self:
            for line in record.medicine_line_ids:
                medicine = line.medicine_id
                if medicine.stock < line.quantity:
                    raise ValidationError(f"Not enough stock for {medicine.name}. Available: {medicine.stock}")
                medicine.stock -= line.quantity
            record.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        for record in self:
            for line in record.medicine_line_ids:
                medicine = line.medicine_id
                medicine.stock += line.quantity
            record.state = 'cancel'

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_sale'] = self.env['ir.sequence'].next_by_code('medical.sale.order') or _("New")

        return super(SaleOrder, self).create(vals)

    @api.depends('medicine_line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.medicine_line_ids)




class SaleOrderLine(models.Model):
    _name = 'medical.sale.order.line'
    _description = 'Sale Order Line'

    sale_order_id = fields.Many2one('medical.sale.order', string='Sale Order', )
    medicine_id = fields.Many2one('medical.medicine', string='Medicine', )
    quantity = fields.Integer('Quantity', default=1)
    price = fields.Float('Price', related='medicine_id.sale_price', readonly=True)
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)



    @api.depends('price', 'quantity')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price
