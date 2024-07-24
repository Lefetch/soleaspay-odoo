# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('soleaspay', 'Soleaspay Payments')],
        ondelete={"soleaspay": "set default"}
    )
    soleaspay_api_key = fields.Char(
        'API Key',
        required_if_provider='soleaspay',
        groups='base.group_user'
    )
    soleaspay_endpoint = fields.Char(
        string="Soleaspay Endpoint",
        default='https://checkout.soleaspay.com'
    )

    def _soleaspay_get_api_url(self):
        self.ensure_one()
        return self.soleaspay_endpoint

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'soleaspay':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_soleaspay.payment_method_soleaspay').id
