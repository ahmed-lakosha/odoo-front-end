/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.websiteDisaster = publicWidget.Widget.extend({
    selector: '.website_vehicle',
    events: {
        'click .o_twitter, .o_facebook, .o_linkedin, .o_google, .o_twitter_complete, .o_facebook_complete, .o_linkedin_complete, .o_google_complete': '_onShareArticle',
    },

    /**
     * @override
     */
    start: function () {
        // $('.js_tweet, .js_comment').share({});
        // return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onShareArticle: function (ev) {
        ev.preventDefault();
        var url = '';
        var $element = $(ev.currentTarget);
        var websiteVehicleTitle = $('#o_vehicle_name').html() || '';
        var articleURL = window.location.href;
        console.log(articleURL);
        console.log(websiteVehicleTitle);
        if ($element.hasClass('o_twitter')) {
            var tweetText = _t(
                "Tam vehicle: %s! Check it live: %s",
                websiteVehicleTitle,
                articleURL
            );
            url = 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=' + encodeURIComponent(tweetText);
        } else if ($element.hasClass('o_facebook')) {
            url = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(articleURL);
        } else if ($element.hasClass('o_linkedin')) {
            url = 'https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(articleURL);
        }
        window.open(url, '', 'menubar=no, width=500, height=400');
    },

});
