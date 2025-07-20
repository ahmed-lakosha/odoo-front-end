# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Website(models.Model):
    _inherit = "website"

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append(
            (_('Vehicle'), self.env['ir.http']._url_for('/vehicle'), 'website_vehicle'))
        return suggested_controllers

    def get_cta_data(self, website_purpose, website_type):
        cta_data = super(Website, self).get_cta_data(website_purpose, website_type)
        if website_purpose == 'website_vehicle':
            cta_data.update({
                'cta_btn_text': _('Vehicle'),
                'cta_btn_href': '/vehicle',
            })
        return cta_data

    def _search_get_details(self, search_type, order, options):
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['vehicles', 'all']:
            result.append(self.env['website.vehicle']._search_get_detail(self, order, options))
        return result
