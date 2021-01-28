  
from odoo import models, fields, api, _
from odoo.exceptions import UserError,Warning
from odoo.tools import float_is_zero
from datetime import datetime as dt
import logging
_logger = logging.getLogger(__name__)

class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    @api.onchange('partner_id')
    def _get_nhis_number(self):
        _logger.info("Inside _get_nhis_number")
        partner_id = self.partner_id.id
        if partner_id:
            self.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
    
    @api.onchange('partner_id')
    def _get_nhis_status(self):
        _logger.info("Inside _get_nhis_status")
        partner_id = self.partner_id.id
        if partner_id:
            self.InsuranceActive = self.env['res.partner']._get_nhis_status(partner_id)

    nhis_number = fields.Char(string='NHIS Number', compute=_get_nhis_number)
    InsuranceActive = fields.Boolean('Insurance Status', compute=_get_nhis_status)