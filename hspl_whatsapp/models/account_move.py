import base64
import json

import html2text

from odoo import Command, _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    """Inherited the module for adding a button that helps to send WhatsApp
    message to the customer."""

    _inherit = "account.move"

    whatsapp_enable_account_invoice = fields.Boolean(
        related="company_id.whatsapp_enable_account_invoice", readonly=False
    )
    whatsapp_enable_account_bill = fields.Boolean(
        related="company_id.whatsapp_enable_account_bill", readonly=False
    )

    def action_send_on_whatsapp(self):
        """
        This method is invoked when the 'send_on_whatsapp' button is clicked.
        It opens a wizard containing the message to be sent to the WhatsApp
        web page."""
        if not self.partner_id.mobile:
            raise ValidationError(_("Add a WhatsApp mobile number to the partner!"))
        (
            report,
            mail_template_values,
            body_html,
            whatsapp_message,
            report_attachment,
        ) = self.get_whatsapp_message_data()
        return {
            "type": "ir.actions.act_window",
            "name": _("WhatsApp Message"),
            "res_model": "send.whatsapp.message",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_whatsapp_message": whatsapp_message,
                "default_attachment_ids": [Command.link(report_attachment.id)],
                "html_whatsapp_message": body_html,
                "error": True,
            },
        }

    def get_whatsapp_message_data(self):
        template_id = self.env.ref("hspl_whatsapp.account_move_whatsapp_template").id
        mail_template_values = (
            self.env["mail.template"]
            .with_context(tpl_partners_only=True)
            .browse(template_id)
            .generate_email([self.id], fields=["body_html"])
        )
        body_html = mail_template_values[self.id].pop("body_html", "")
        whatsapp_message = html2text.html2text(body_html)
        report = self.env["ir.actions.report"]._render_qweb_pdf(
            "account.account_invoices", self.id
        )
        report_attachment = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": str(self.name + ".pdf")
                    if self.name and self.name != "/"
                    else "Invoice Report.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(report[0]),
                    "store_fname": str(self.name + ".pdf") or "Invoice Report.pdf",
                    "mimetype": "application/pdf",
                    "res_model": "account.move",
                }
            )
        )
        report_attachment.public = True
        return (
            report,
            mail_template_values,
            body_html,
            whatsapp_message,
            report_attachment,
        )

    def account_move_payload(self, file_link, user_mobile_number):
        if (
            self.company_id.whatsapp_enable_account_invoice
            or self.company_id.whatsapp_enable_account_bill
        ):
            payload = {
                "messaging_product": "whatsapp",
                "to": user_mobile_number,
                "type": "template",
                "template": {
                    "name": "invoices",
                    "language": {"code": "en_US"},
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "document",
                                    "document": {
                                        "filename": self.name,
                                        "link": file_link,
                                    },
                                }
                            ],
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": self.partner_id.name,
                                },
                                {
                                    "type": "text",
                                    "text": str(self.currency_id.symbol)
                                    + str(self.amount_total),
                                },
                                {"type": "text", "text": self.env.company.name},
                            ],
                        },
                    ],
                },
            }
            payload = json.dumps(payload)
            return payload

    def action_send_by_whatsapp(self):
        for rec in self:
            (
                report,
                mail_template_values,
                body_html,
                whatsapp_message,
                report_attachment,
            ) = rec.get_whatsapp_message_data()

            context = {
                "active_model": "account.move",
                "active_id": rec.id,
                "html_whatsapp_message": body_html,
                "error": False,
            }
            whatsapp_message_data = (
                rec.env["send.whatsapp.message"]
                .with_context(**context)
                .create(
                    {
                        "partner_id": rec.partner_id.id,
                        "whatsapp_mobile_number": rec.partner_id.mobile,
                        "whatsapp_message": whatsapp_message,
                        "attachment_ids": [Command.link(report_attachment.id)],
                    }
                )
            )

            whatsapp_message_data.action_send_custom_message()
