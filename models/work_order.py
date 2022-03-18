from odoo import fields, models, api, _


class WorkOrder(models.Model):
    _name = 'booking.work_order'
    _description = 'Work Order'
    _rec_name = "wo_number"

    wo_number = fields.Char(
        string='WO Number',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'))
    bo_reference = fields.Many2one(
        comodel_name='sale.order',
        readonly=True)
    team = fields.Many2one(
        comodel_name='booking.service_team',
        required=True)
    team_leader = fields.Many2one(
        comodel_name='res.users',
        string='Team Leader',
        required=True)
    team_members = fields.Many2many(
        comodel_name='res.users',
        string='Team Members')
    planned_start = fields.Datetime(
        string="Planned Start",
        required=True)
    planned_end = fields.Datetime(
        string='Planned End',
        required=True)
    date_start = fields.Datetime(
        string='Date Start',
        readonly=True)
    date_end = fields.Datetime(
        string='Date End',
        readonly=True)
    state = fields.Selection(
        [('pending', 'Pending'), ('in_progress', 'In Progress'), ('done', 'Done'), ('cancelled', 'Cancelled')],
        string='State',
        default='pending',
        track_visibility='onchange')
    note = fields.Text(
        string='Note')
