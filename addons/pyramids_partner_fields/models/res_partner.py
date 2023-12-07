# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

ADDRESS_FIELDS = ('py_house_number','py_floor_number','street', 'street2', 'py_landmark', 'zip', 'city', 'state_id', 'country_id')

class ResPartner(models.Model):

    _inherit = 'res.partner'

    py_gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'), ('female', 'Female')]
    )

    py_house_number = fields.Char('House Number')
    py_floor_number = fields.Char('Floor Number')
    py_landmark = fields.Char('Landmark')
    

    @api.model
    def _get_default_address_format(self):
        super()._get_default_address_format()
        return "%(py_house_number)s %(py_floor_number)s\n%(street)s\n%(street2)s\n%(py_landmark)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        super()._address_fields()
        return list(ADDRESS_FIELDS)