from odoo import fields, models


class WhatsappErrors(models.Model):
    _name = "whatsapp.errors"
    _description = "Whatsapp Errors"
    _order = "id desc"

    model = fields.Char("Related Document Model")
    request = fields.Text()
    url = fields.Char()
    response = fields.Text()
    record_id = fields.Char("Related Document ID")
    trace_back_error = fields.Text()
    status_code = fields.Char()
    status = fields.Selection([("error", "Error"), ("success", "Success")])
