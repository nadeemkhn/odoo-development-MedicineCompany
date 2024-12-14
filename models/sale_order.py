from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _name = 'medical.sale.order'
    _description = 'Sale Order'
    _rec_name = 'sequence_sale'

    customer_id = fields.Many2one('medical.customer', string='Customer')
    medicine_line_ids = fields.One2many('medical.sale.order.line', 'sale_order_id', string='Medicine Lines')
    sale_date = fields.Datetime('Sale Date', default=fields.Datetime.now)
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    sequence_sale = fields.Char(string='Sale Sequence', copy=False, default='New')
    delivery_id = fields.Many2one('stock.delivery', string='Delivery', readonly=True)
    delivery_count = fields.Integer(string='Delivery Count' ,compute='_compute_delivery_count')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation sent'),
        ('sale', 'Sale Order'),
        ('cancel', 'cancelled'),
        ('done', 'Locked'),


    ],
        default='draft', string='status', tracking=True)

    @api.depends('delivery_id')

    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = self.env['stock.delivery'].search_count(
                [('partner_id', '=', record.customer_id.id)])

    def action_sent(self):
        self.state = 'sent'

    def acton_done(self):
        self.state = 'done'

    def action_sale(self):
        for order in self:
            stock_delivery_vals = {
                'partner_id': order.customer_id.id,
                'Schedule_date': fields.Date.context_today(self),
                 'confirm_date': fields.Date.context_today(self),
                'state': 'draft',
                'picking_type': 'sale',
                'sequence': self.env['ir.sequence'].next_by_code('stock.delivery.sale'),
                'stock_delivery': [
                    (0, 0, {
                        'product_id': line.medicine_id.id,
                        'demand_qty': line.quantity,
                        'done_qty': 0,
                        'price': line.medicine_id.sale_price,
                    }) for line in order.medicine_line_ids
                ]
            }
            delivery = self.env['stock.delivery'].create(stock_delivery_vals)
            order.delivery_id = delivery.id

            order.state = 'sale'

    def action_view_delivery(self):
        self.ensure_one()
        if not self.delivery_id:
            raise ValidationError(_("No delivery record associated with this sale order."))

        return {
            'name': _('Delivery'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.delivery',
            'res_id': self.delivery_id.id,
            'target': 'current',
        }

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        for line in self.medicine_line_ids:
            medicine = line.medicine_id
            medicine.stock += line.quantity
        if self.delivery_id:
            self.delivery_id.state = 'cancel'
        self.state = 'cancel'

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_sale'] = self.env['ir.sequence'].next_by_code('medical.sale.order') or _("New")

        return super(SaleOrder, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'sale':
                raise ValidationError('you cant delete this because it already confirm')

        return super(SaleOrder, self).unlink()

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
