  
from odoo import models, fields, exceptions,api, _
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
        for sale_order in self:
            partner_id = sale_order.partner_id.id
            if partner_id:
                sale_order.nhis_number = self.env['res.partner']._get_nhis_number(partner_id)
    
    @api.onchange('partner_id')
    def _get_nhis_status(self):
        _logger.info("Inside _get_nhis_status")
        for sale_order in self:
            partner_id = sale_order.partner_id.id
            if partner_id:
                sale_order.InsuranceActive = self.env['res.partner']._get_nhis_status(partner_id)

    @api.onchange('payment_type')
    def _change_payment_type(self):
        _logger.info("Inside _change_payment_type")
        for sale_order in self:
            for sale_order_line in sale_order.order_line:
                if sale_order.payment_type == 'cash' :
                    sale_order_line.update({
                        'payment_type': sale_order.payment_type,
                        'price_unit':sale_order_line.product_id.list_price

                        })
                if sale_order.payment_type == 'free' :
                    sale_order_line.update({
                        'payment_type': sale_order.payment_type,
                        'price_unit':0
                        })
                if sale_order.payment_type == 'insurance':
                    if self.nhis_number:
                        sale_order_line.update({
                            'payment_type': sale_order.payment_type,
                            'price_unit':sale_order_line.product_id.list_price

                            })
                    else:
                            return {'warning': {'title':'Warning Main!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}
                

    @api.onchange("order_line")
    def on_change_state(self):
        cash =False
        insurance = False
        free = False
        for sale_order in self:
            for sale_order_line in sale_order.order_line:
                if sale_order_line.payment_type == 'cash':
                    cash =True
                if sale_order_line.payment_type == 'free':
                    free =True
                if sale_order_line.payment_type == 'insurance':
                    if self.nhis_number:
                        insurance =True
                        sale_order.update({'payment_type': 'partial'})
                    else:
                        return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}
        if(cash and insurance and free):
            return {'value': {'payment_type': 'partial'}}
        elif(cash and free):
            return {'value': {'payment_type': 'partial'}}
        elif(cash and insurance):
            return {'value': {'payment_type': 'partial'}}
        elif(free and insurance):
            return {'value': {'payment_type': 'partial'}}
        elif(cash):
            return {'value': {'payment_type': 'cash'}}
        elif(free):
            return {'value': {'payment_type': 'free'}}
        elif(insurance):
            if self.nhis_number:
                return {'value': {'payment_type': 'insurance'}}
            else:
                 return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}

    nhis_number = fields.Char(string='NHIS Number', compute=_get_nhis_number)
    InsuranceActive = fields.Boolean('Insurance Status', compute=_get_nhis_status)
    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('partial', 'Partial'), ('free', 'FREE')], default='cash', string="Payment Type", required="True")
class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    payment_type = fields.Selection([('insurance', 'INSURANCE'), ('cash', 'CASH'), ('free', 'FREE')], default='cash', string="Payment Type", required=True)
    
    def getInsuranceCost(self,productData):
        # resData = self.env('insurance.odoo.product.map').search(self._cr, self._uid, [( 'odoo_product_id', 'in', productData.id) ])
        resData =self.env['insurance.odoo.product.map'].search([('odoo_product_id', '=', productData.id)], limit=10)
        # raise UserError(_('getting insurance cost of '+ str(len(resData))))
        if len(resData) == 0:
            raise UserError(_('Product not found in mapping. Please contact admin.'))
        else:
            return resData[0].insurance_price
    
    @api.onchange('payment_type')
    def _change_payment_type(self):
        _logger.info("Inside _change_payment_type")
        for sale_order_line in self:
            if sale_order_line.payment_type == 'cash':
                return {'value': {'price_unit': sale_order_line.product_id.list_price}}
            if sale_order_line.payment_type == 'free' :
                return {'value': {'price_unit':0}}
            if sale_order_line.payment_type == 'insurance' :
                if self.order_id.nhis_number:
                    insurance_cost = self.getInsuranceCost(sale_order_line.product_id)
                    return {'value': {'price_unit':insurance_cost}}
                    # return {'value': {'price_unit': sale_order_line.product_id.list_price}}
                else:
                    return {'warning': {'title':'Warning!!!','message':'Payment type \'Insurance\' can be selected for patient with valid insuree id only.'},'value': {'payment_type': 'cash'}}