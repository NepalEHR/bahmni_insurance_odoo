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