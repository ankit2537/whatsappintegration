from odoo import fields, models


class MailGateway(models.Model):
    _inherit = "mail.gateway"

    whatsapp_version = fields.Char(default="19.0")
