from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class BookingOrder(models.Model):
    _inherit = 'sale.order'

    is_booking_order = fields.Boolean(
        string='Is Booking Order')
    team = fields.Many2one(
        comodel_name='booking.service_team',
        string='Team')
    team_leader = fields.Many2one(
        comodel_name='res.users',
        string='Team Leader')
    team_members = fields.Many2many(
        comodel_name='res.users',
        string='Team Members')
    booking_start = fields.Datetime(
        string='Booking Start',
        default=fields.Date.today())
    booking_end = fields.Datetime(
        string='Booking End')
    wo_count = fields.Integer(
        string='Work Order',
        compute='_compute_wo_count')

    def _compute_wo_count(self):
        wo_data = self.env['booking.work_order'].sudo().read_group([('bo_reference', 'in', self.ids)], ['bo_reference'],
                                                                   ['bo_reference'])
        result = {
            data['bo_reference'][0]: data['bo_reference_count'] for data in wo_data
        }

        for wo in self:
            wo.wo_count = result.get(wo.id, 0)

    @api.onchange('team')
    def _onchange_team(self):
        search = self.env['booking.service_team'].search([('id', '=', self.team.id)])
        team_members = []
        for team in search:
            team_members.extend(members.id for members in team.team_members)
            self.team_leader = team.team_leader.id
            self.team_members = team_members

    def action_check(self):
        for check in self:
            wo = self.env['booking.work_order'].search(
                [('team_leader', 'in', [g.id for g in self.team_members]),
                 ('team_members', 'in', [self.team_leader.id]),
                 ('team_leader', '=', self.team_leader.id),
                 ('team_members', 'in', [g.id for g in self.team_members]),
                 ('state', '!=', 'cancelled'),
                 ('planned_start', '<=', self.booking_end),
                 ('planned_end', '>=', self.booking_start)], limit=1)
            if wo:
                raise ValidationError('Team already has work order during that period on SOXX')
            else:
                raise ValidationError('Team is available for booking')

    def action_confirm(self):
        res = super(BookingOrder, self).action_confirm()
        for order in self:
            wo = self.env['booking.work_order'].search(
                [('team_leader', 'in', [g.id for g in self.team_members]),
                 ('team_members', 'in', [self.team_leader.id]),
                 ('team_leader', '=', self.team_leader.id),
                 ('team_members', 'in', [g.id for g in self.team_members]),
                 ('state', '!=', 'cancelled'),
                 ('planned_start', '<=', self.booking_end),
                 ('planned_end', '>=', self.booking_start)], limit=1)
            if wo:
                raise ValidationError('Team is not available during this period, already booked on '
                                      'SOXX. Please book on another date.')
            order.action_work_order_create()
        return res

    def action_work_order_create(self):
        wo_obj = self.env['booking.work_order']
        for order in self:
            wo_obj.create([{'bo_reference': order.id,
                            'team': order.team.id,
                            'team_leader': order.team_leader.id,
                            'planned_start': order.booking_start,
                            'planned_end': order.booking_end}])