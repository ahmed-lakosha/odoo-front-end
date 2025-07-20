# -*- coding: utf-8 -*-
{
    'name': 'Website Vehicle',
    'summary': """
        Website Vehicle pages
    """,
    'description': """
    """,
    'author': "Ahmed Lakosha",
    'version': '0.1',
    'category': 'Website',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'security/website_vehicle_security.xml',

        'data/pages.xml',

        'view/vehicles.xml',
        'view/snippets.xml',
        'view/vehicle_details.xml',
        'view/website_image_views.xml',
        'view/website_pages_views.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'assets': {
        'website.assets_editor': [
            'website_vehicle/static/src/js/systray_items/*.js',
        ],
        'web.assets_frontend': [
            'website_vehicle/static/src/js/sharing_links.js',
            'website_vehicle/static/src/scss/style.scss',
        ],
    },
    'installable': True,
}
