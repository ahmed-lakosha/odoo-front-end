from odoo import models, fields, api, _


class ThemeTam(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_vehicles_post_copy(self, mod):
        self.enable_view('website.template_header_default')
        self.disable_view('website.header_visibility_standard')
        self.disable_view('website.header_text_element')
        self.disable_view('website.header_search_box')
        self.disable_view('website.header_call_to_action')
        self.disable_view('website.header_social_links')
