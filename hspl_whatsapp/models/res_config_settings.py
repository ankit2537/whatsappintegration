# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_enable_sale_order = fields.Boolean(
        "Whatsapp Message Enable On Sale",
        related="company_id.whatsapp_enable_sale_order",
        readonly=False,
    )
    whatsapp_enable_account_invoice = fields.Boolean(
        "Whatsapp Message Enable On Customer Invoice",
        related="company_id.whatsapp_enable_account_invoice",
        readonly=False,
    )
    whatsapp_enable_account_bill = fields.Boolean(
        "Whatsapp Message Enable On Vendor Bill",
        related="company_id.whatsapp_enable_account_bill",
        readonly=False,
    )
    whatsapp_enable_purchase_order = fields.Boolean(
        "Whatsapp Message Enable On Purchase",
        related="company_id.whatsapp_enable_purchase_order",
        readonly=False,
    )
    whatsapp_channal_for_so = fields.Many2one(
        related="company_id.whatsapp_mail_gateway_for_so",
        string="Whatsapp Channal for Sale Order",
        readonly=False,
    )
    whatsapp_channal_for_po = fields.Many2one(
        related="company_id.whatsapp_mail_gateway_for_po",
        string="Whatsapp Channal for Purchase Order",
        readonly=False,
    )
    whatsapp_channal_for_vb = fields.Many2one(
        related="company_id.whatsapp_mail_gateway_for_vb",
        string="Whatsapp Channal for Vendor Bill ",
        readonly=False,
    )
    whatsapp_channal_for_ci = fields.Many2one(
        related="company_id.whatsapp_mail_gateway_for_ci",
        string="Whatsapp Channal for Customer Invoice",
        readonly=False,
    )
