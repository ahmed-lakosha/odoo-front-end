from odoo import http
from odoo.http import request
from odoo.tools import sql
import logging

_logger = logging.getLogger(__name__)


class WebsiteVehicle(http.Controller):

    @http.route([
        '/vehicle/<model("website.vehicle"):vehicle>'
    ], type='http', auth="public", website=True, sitemap=True)
    def website_vehicle(self, vehicle, enable_editor=None, **kwargs):
        """
        Display the Website vehicle details page.

        This controller:
          - Ensures that the URL uses the canonical slug.
          - Retrieves a list of vehicles for navigation.
          - Computes the next vehicle.
          - Increments the view counter.
          - Injects metadata for 'Edit in Backend' button.
        """
        vehicles = request.env['website.vehicle'].sudo().search([('type_id', '=', vehicle.type_id.id)])
        vehicle_ids = vehicles.ids
        if vehicle.id not in vehicle_ids:
            return request.redirect("/vehicle", code=301)

        current_index = vehicle_ids.index(vehicle.id)
        next_vehicle = (
            request.env['website.vehicle'].sudo().browse(vehicle_ids[current_index + 1])
            if current_index + 1 < len(vehicle_ids) else False
        )

        values = {
            'vehicle': vehicle,
            'enable_editor': enable_editor,
            'next_vehicle': next_vehicle,
            'next_vehicle_slug': next_vehicle and request.env['ir.http']._slug(next_vehicle) or '',
            'main_object': vehicle,
        }

        response = request.render("website_vehicle.website_vehicle_template", values)

        # 🚗 Update view counter if not viewed in session
        if vehicle.id not in request.session.get('vehicles_viewed', []):
            if sql.increment_fields_skiplock(vehicle, 'visits'):
                request.session.setdefault('vehicles_viewed', []).append(vehicle.id)
                request.session.touch()

        return response

    @http.route('/vehicles', type='http', auth="public", website=True, sitemap=True)
    def vehicles(self, **kwargs):
        """
        List all vehicles and all vehicle types.
        """
        vehicle_ids = request.env['website.vehicle'].search([])
        type_ids = vehicle_ids.mapped('type_id')
        data = {
            'vehicle_ids': vehicle_ids,
            'type_ids': type_ids,
        }
        return request.render('website_vehicle.vehicle_types_page', data)
