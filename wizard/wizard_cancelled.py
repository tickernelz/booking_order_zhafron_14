from odoo import models, fields, api, exceptions, _


class Cancelled(models.TransientModel):
    _name = "cancelled.wo"

    note = fields.Text('Note')

    def cancelled(self):
        cancel = self.env['booking.work_order'].browse(self.env.context['active_id'])
        cancel_create = cancel.update({'note': self.note, 'state': 'cancelled'})
