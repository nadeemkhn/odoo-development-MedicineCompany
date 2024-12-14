from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = 'medical.purchase.order'
    _description = 'Purchase Order'
    _rec_name = 'sequence_purchase'

    supplier_id = fields.Many2one('medical.supplier', string='Supplier')
    medicine_line_ids = fields.One2many('medical.purchase.order.line', 'purchase_order_id', string='Medicine Lines')
    purchase_date = fields.Datetime('Purchase Date', default=fields.Datetime.now)
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')], string='Priority')
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    sequence_purchase = fields.Char(string='Purchase Sequence', required=True, copy=False,
                                    default=lambda self: _('New'))
    delivery_id = fields.Many2one('stock.delivery', string='Delivery', readonly=True)
    delivery_count = fields.Integer(string='Delivery Count', compute='_compute_delivery_count' )



    state = fields.Selection([
        ('done', 'Done'),
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm','Purchase Order')
    ], default='draft', string='Status', tracking=True)

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        for recs in self.medicine_line_ids:
            medicine = recs.medicine_id
            medicine.stock -=  recs.quantity
        if self.delivery_id:
            self.delivery_id.state = 'cancel'
        self.state = 'cancel'
    def action_confirm(self):
        for order in self:
            stock_delivery_vals = {
                'supplier_id': order.supplier_id.id,
                'Schedule_date': fields.Date.context_today(self),
                 'confirm_date': fields.Date.context_today(self),
                'sequence': self.env['ir.sequence'].next_by_code('stock.delivery.purchase'),
                'state': 'draft',
                'picking_type': 'purchase',
                'stock_delivery': [
                    (0, 0, {
                        'product_id': line.medicine_id.id,
                        'demand_qty': line.quantity,
                        'done_qty': 0,
                        'price': line.medicine_id.cost_price
                    }) for line in order.medicine_line_ids
                ]
            }
            delivery = self.env['stock.delivery'].create(stock_delivery_vals)
            order.delivery_id = delivery.id
            order.state = 'confirm'

    @api.depends('delivery_id')
    def _compute_delivery_count(self):
        for record in self:
            record.delivery_count = self.env['stock.delivery'].search_count(
                [('supplier_id', '=', record.supplier_id.id)])

    def action_view_delivery(self):
        self.ensure_one()
        if not self.delivery_id:
            raise ValidationError(_("No delivery record associated with this sale order."))

        return {
            'name': _('Receipt'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.delivery',
            'res_id': self.delivery_id.id,
            'target': 'current',
        }




    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            val['sequence_purchase'] = self.env['ir.sequence'].next_by_code('medical.purchase.order') or _("New")
        return super(PurchaseOrder, self).create(vals)


    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise ValidationError('you cant delete this because it already done')

        return super(PurchaseOrder, self).unlink()

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



    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price
