from odoo import fields, models


class MailTemplate(models.Model):
    """Inherited this model for adding some fields that help to check the
    message template is a delivery, invoice, purchase, or sale order
    template"""

    _inherit = "mail.template"

    is_sale_template = fields.Boolean(
        string="Sale Template",
        help="To check the message template for" "sending sale order to whatsapp",
    )
    is_invoice_template = fields.Boolean(
        string="Invoice Template",
        help="To check the message template " "for sending delivery " "to whatsapp",
    )
    is_purchase_template = fields.Boolean(
        string="Purchase Template",
        help="To check the message template " "sending purchase order to" " whatsapp",
    )
