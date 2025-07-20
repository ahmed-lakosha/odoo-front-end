from odoo import api, fields, models, tools, _
from odoo.http import request
from odoo.tools.translate import html_translate
from odoo.tools.image import is_image_size_above
from odoo.addons.http_routing.models.ir_http import slug, unslug


class WebsiteVehicleTag(models.Model):
    _name = 'website.vehicle.tag'
    _description = 'Vehicle Tag'

    name = fields.Char(required=True, translate=True)
    color = fields.Integer('Color')


class WebsiteVehicleType(models.Model):
    _name = 'website.vehicle.type'
    _description = "Website Vehicle Type"
    _inherit = [
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.searchable.mixin',
    ]
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color')
    vehicle_ids = fields.One2many('website.vehicle', 'type_id', string='Vehicles')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists!"),
    ]


class VehicleExteriorImage(models.Model):
    _name = 'vehicle.exterior.image'
    _description = "Vehicle Exterior Image"
    _inherit = ['image.mixin']
    _order = 'sequence, id'

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(default=10)

    image_1920 = fields.Image()
    vehicle_id = fields.Many2one('website.vehicle', "Vehicle", index=True, ondelete='cascade')
    can_image_1024_be_zoomed = fields.Boolean("Can Image 1024 be zoomed", compute='_compute_can_image_1024_be_zoomed',
                                              store=True)

    @api.depends('image_1920', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for image in self:
            image.can_image_1024_be_zoomed = image.image_1920 and is_image_size_above(image.image_1920,
                                                                                      image.image_1024)


class WebsiteVehicle(models.Model):
    _name = 'website.vehicle'
    _description = "Vehicle"
    _order = 'id DESC'

    _inherit = [
        'mail.thread',
        'image.mixin',
        'website.seo.metadata',
        'website.published.multi.mixin',
        'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]

    website_description = fields.Html(
        string="Description for the website",
        translate=html_translate,
        sanitize_overridable=True,
        sanitize_attributes=False,
        sanitize_form=False,
    )
    visits = fields.Integer('No of Views', copy=False, default=0, readonly=True)
    website_id = fields.Many2one('website', string='Website', default=lambda self: self.env.user.website_id.id)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 default=lambda self: self.env.company)

    def _compute_website_url(self):
        super(WebsiteVehicle, self)._compute_website_url()
        for property in self:
            property.website_url = "/vehicle/%s" % (slug(property))

    def _default_content(self):
        return '''
            <p class="o_default_snippet_text">''' + _("Start writing here...") + '''</p>
        '''

    def _get_access_action(self, access_uid=None, force_website=False):
        """ Instead of the classic form view, redirect to the post on website
        directly if user is an employee or if the post is published. """
        self.ensure_one()
        user = self.env['res.users'].sudo().browse(access_uid) if access_uid else self.env.user
        if not force_website and user.share and not self.sudo().website_published:
            return super(WebsiteVehicle, self)._get_access_action(access_uid=access_uid, force_website=force_website)
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
            'target_type': 'public',
            'res_id': self.id,
        }

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        """ Add access button to everyone if the document is published. """
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        if not self:
            return groups

        self.ensure_one()
        if self.website_published:
            for _group_name, _group_method, group_data in groups:
                group_data['has_button_access'] = True

        return groups

    name = fields.Char('Title', required=True, translate=True, default='')
    title = fields.Char(string="Title", compute="_compute_title", store=True)

    @api.depends('name')
    def _compute_title(self):
        for rec in self:
            rec.title = rec.name

    tag_ids = fields.Many2many('website.vehicle.tag', string="Tags")
    description = fields.Text('Description', translate=True)
    type_id = fields.Many2one('website.vehicle.type', string='Vehicle Type')
    datasheet = fields.Binary('Datasheet')
    image_1920 = fields.Image()

    exterior_image_ids = fields.One2many(
        string="Extra Exterior Media",
        comodel_name='vehicle.exterior.image',
        inverse_name='vehicle_id',
        copy=True,
    )

    def _default_website_meta(self):
        res = super(WebsiteVehicle, self)._default_website_meta()
        res['default_opengraph']['og:description'] = res['default_twitter']['twitter:description'] = self.title
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:tag'] = self.tag_ids.mapped('name')
        # background-image might contain single quotes eg `url('/my/url')`
        # res['default_opengraph']['og:image'] = res['default_twitter']['twitter:image'] = json_scriptsafe.loads(self.cover_properties).get('background-image', 'none')[4:-1].strip("'")
        res['default_opengraph']['og:title'] = res['default_twitter']['twitter:title'] = self.name
        res['default_meta_description'] = self.title
        return res

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        search_fields = ['name']
        fetch_fields = ['id', 'name']
        state = options.get('state')
        domain = [website.website_domain()]
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'url', 'type': 'text', 'truncate': False},
        }
        if self.env.user.has_group('website.group_website_designer'):
            if state == "confirmed":
                domain.append([("website_published", "=", True)])
            elif state == "draft":
                domain.append(['|', ("website_published", "=", False)])
        if with_description:
            search_fields.append('description')
            fetch_fields.append('description')
            mapping['description'] = {'name': 'description', 'type': 'text', 'match': True}
        return {
            'model': 'website.vehicle',
            'base_domain': domain,
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-rss',
            'order': 'from_date desc, id desc' if 'from_date desc' in order else 'from_date asc, id desc',
        }

    def _search_render_results(self, fetch_fields, mapping, icon, limit):
        results_data = super()._search_render_results(fetch_fields, mapping, icon, limit)
        for data in results_data:
            data['url'] = '/vehicle/%s' % data['id']
        return results_data
