from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    whatsapp_enable_sale_order = fields.Boolean()
    whatsapp_enable_account_invoice = fields.Boolean()
    whatsapp_enable_account_bill = fields.Boolean()
    whatsapp_enable_purchase_order = fields.Boolean()
    whatsapp_mail_gateway_for_so = fields.Many2one("mail.gateway", readonly=False)
    whatsapp_mail_gateway_for_po = fields.Many2one("mail.gateway", readonly=False)
    whatsapp_mail_gateway_for_vb = fields.Many2one("mail.gateway", readonly=False)
    whatsapp_mail_gateway_for_ci = fields.Many2one("mail.gateway", readonly=False)
