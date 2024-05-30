import json
import logging
import re
import traceback

import requests

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SendWhatsappMessage(models.TransientModel):
    """This function helps to send a message to a user."""

    _name = "send.whatsapp.message"
    _description = "Helps to send messages using different way"

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner Name",
        default=lambda self: self.env[self._context.get("active_model")]
        .browse(self.env.context.get("active_ids"))
        .partner_id,
        help="Select the partner associated with " "the sale.",
    )
    whatsapp_mobile_number = fields.Char(
        related="partner_id.mobile",
        required=True,
        help="The mobile number associated" " with the selected partner.",
    )
    whatsapp_message = fields.Text(
        string="Message",
        help="Enter the message to be sent via " "WhatsApp.",
        readonly=True,
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "whatsapp_attachment_rel",
        "email_template_id",
        "attachment_id",
        string="Attachments",
        help="Attachments to include in the" " WhatsApp message.",
        readonly=True,
    )

    def action_send_custom_message(self):
        """This function helps to send a message to a user."""
        base_url = self.get_base_url()
        # gateways = self.env["mail.gateway"].search([("gateway_type", "=", "whatsapp")])
        active_model = self._context.get("active_model")
        record_id = self.env[active_model].browse(self._context.get("active_id"))
        if active_model == "sale.order":
            gateways = self.env.company.whatsapp_mail_gateway_for_so
        elif active_model == "purchase.order":
            gateways = self.env.company.whatsapp_mail_gateway_for_po
        elif active_model == "account.move" and record_id.move_type == "out_invoice":
            gateways = self.env.company.whatsapp_mail_gateway_for_ci
        elif active_model == "account.move" and record_id.move_type == "in_invoice":
            gateways = self.env.company.whatsapp_mail_gateway_for_vb
        channel = self.partner_id._whatsapp_get_channel("mobile", gateways)
        channel.message_post(
            body=self._context.get("html_whatsapp_message"),
            attachment_ids=self.attachment_ids.ids,
            subtype_xmlid="mail.mt_comment",
            message_type="comment",
        )
        gateway = self.partner_id.gateway_channel_ids.gateway_id
        attachment = self.env["ir.attachment"].browse(self.attachment_ids.ids[0])

        file_link = base_url + (
            f"/web/content/?model=ir.attachment&id={attachment.id}&download=true"
        )
        _logger.info(file_link)
        active_model_payload_method = active_model.replace(".", "_") + "_payload"
        url = (
            f"https://graph.facebook.com/v{gateway.whatsapp_version}/"
            f"{gateway.whatsapp_from_phone}/messages"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {gateway.token}",
        }
        attachment.public = True
        user_mobile_number = self.clean_phone_number(self.partner_id.mobile)
        error = False
        try:
            if active_model_payload_method:
                payload = getattr(record_id, active_model_payload_method)(
                    file_link, user_mobile_number
                )
                response = requests.request(
                    "POST", url, headers=headers, data=payload, timeout=20
                )
                _logger.info(response.text)
                if response.status_code == 200:
                    self.env["whatsapp.errors"].sudo().create(
                        {
                            "model": self._context.get("active_model"),
                            "request": payload,
                            "url": url,
                            "response": json.loads(response.text),
                            "record_id": record_id.id,
                            "status_code": response.status_code,
                            "status": "success",
                        }
                    )
                elif response.status_code != 200:
                    self.env["whatsapp.errors"].sudo().create(
                        {
                            "model": self._context.get("active_model"),
                            "request": payload,
                            "url": url,
                            "response": json.loads(response.text),
                            "record_id": record_id.id,
                            "status_code": response.status_code,
                            "status": "error",
                        }
                    )
                if json.loads(response.text).get("error"):
                    error = _(json.loads(response.text)["error"]["message"])

        except Exception:
            traceback_str = traceback.format_exc()
            self.env["whatsapp.errors"].sudo().create(
                {
                    "model": self._context.get("active_model"),
                    "url": url,
                    "record_id": record_id.id,
                    "status": "error",
                    "trace_back_error": traceback_str,
                }
            )
        if error and self._context.get("error"):
            raise ValidationError(error)

    def clean_phone_number(self, phone_number):
        """Removes "+" sign and spaces from a phone number."""
        return re.sub(r"[^\d]", "", phone_number)
