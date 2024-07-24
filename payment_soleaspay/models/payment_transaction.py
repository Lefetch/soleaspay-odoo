# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging

from werkzeug import urls

from odoo import _, api, models
from odoo.exceptions import ValidationError

from odoo.addons.payment_soleaspay.controllers.main import SoleaspayController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super(PaymentTransaction, self)._get_specific_rendering_values(processing_values)
        if self.provider != 'soleaspay':
            return res

        # base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return_url = urls.url_join(self.acquirer_id.get_base_url(), SoleaspayController._return_url)

        # secret_key = str(self.reference) + str(self.amount) + str(self.acquirer_id.remotepassword)
        # secret_key_hash = hashlib.md5(secret_key.encode('utf-8')).hexdigest()
        # api_url = self.acquirer_id._get_enet_urls(self.acquirer_id.state)['enet_form_url']
        rendering_values = {
            'api_key': self.acquirer_id.soleaspay_api_key,
            'amount': self.amount,
            'api_url': self.acquirer_id._soleaspay_get_api_url(),
            'currency': self.company_id.currency_id.name,
            'orderId': self.reference,
            'description': self.partner_name,
            'shopName': self.company_id.name,
            'successUrl': return_url,
            'failureUrl': return_url,
        }
        return rendering_values

    @api.model
    def _get_tx_from_feedback_data(self, provider, data):
        """ Override of payment to find the transaction based on Soleaspay data.

        :param str provider: The provider of the acquirer that handled the transaction
        :param dict data: The feedback data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        :raise: ValidationError if the signature can not be verified
        """
        tx = super()._get_tx_from_feedback_data(provider, data)
        if provider != 'soleaspay':
            return tx

        parsed_data = json.loads(data.get('soleaspay_data'))
        if parsed_data.get('status') != 'SUCCESS':
            raise ValidationError(
                "Soleaspay: " + parsed_data.get('message')
            )

        reference = parsed_data.get('orderId')
        tx = self.search([('reference', '=', reference), ('provider', '=', 'soleaspay')])
        if not tx:
            raise ValidationError(
                "Soleaspay: " + _("No transaction found matching reference %s.", reference)
            )

        return tx

    def _process_feedback_data(self, data):
        """ Override of payment to process the transaction based on Soleaspay data.

        Note: self.ensure_one()

        :param dict data: The feedback data sent by the provider
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_feedback_data(data)
        if self.provider != 'soleaspay':
            return

        parsed_data = json.loads(data.get('soleaspay_data'))
        # transaction_keys = parsed_data.get('data')
        if not parsed_data:
            raise ValidationError("Soleaspay: " + _("Received data with missing transaction keys"))

        result = self.write({
            'acquirer_reference': parsed_data.get('ref'),
        })

        status = parsed_data.get('status')
        if status == 'SUCCESS':
            self._set_done()
            return True
        # elif not status:
        #     if parsed_data.get('status') == 'FAILED':
        #         self._set_error(str(parsed_data.get('message')))
        #     else:
        #         self._set_error(str(parsed_data.get('message')))
        else:
            _logger.warning(f"Soleaspay: {parsed_data.get('message')}")
            self._set_error(parsed_data.get('message'))
