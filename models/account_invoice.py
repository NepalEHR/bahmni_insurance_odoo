from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class account_invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH')], default='cash', string="Payment Type", required="True", help="Payment type accepted for this invoice", states={'draft': [('readonly', False)]})    


class account_invoice(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    @api.multi
    @api.onchange('amount')
    def onchange_sale_orders_add_claim(self):
        """
        Trigger the change of sale order to add claims for associated sale orders
        """
        _logger.info("onchange_sale_orders_add_claim") 
        paymentType = self.invoice_ids.payment_type
        wt = self.env['payment.journal.mapping']
        id_needed = wt.search([('payment_type', '=', paymentType)]).journal_id
        if id_needed:
            for payment in self:                
                payment.update({
                    'journal_id': id_needed
                })    
                payment.currency_id = payment.journal_id.currency_id or payment.company_id.currency_id
                # Set default payment method (we consider the first to be the default one)
                payment_methods = payment.payment_type == 'inbound' and payment.journal_id.inbound_payment_method_ids or payment.journal_id.outbound_payment_method_ids
                payment.payment_method_id = payment_methods and payment_methods[0] or False
                # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
                payment_type = payment.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
                return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}