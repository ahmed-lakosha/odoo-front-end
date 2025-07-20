from odoo import http, fields
from odoo.http import request


#
class WebsiteCustomPage(http.Controller):
    @http.route('/controller/hello', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        # Get the current website and define the domain
        current_website = http.request.website
        domain = [('website_id', '=', current_website.id)]

        vehicle_ids = request.env['website.vehicle'].search([])
        type_ids = vehicle_ids.mapped('type_id')
        data = {
            'vehicle_ids': vehicle_ids,
            'type_ids': type_ids,
        }
        return request.render('theme_vehicles.hello_template', data)
