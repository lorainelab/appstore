var myDefaultWhiteList = $.fn.tooltip.Constructor.Default.whiteList

// To allow table elements
myDefaultWhiteList.input = []
myDefaultWhiteList.button = []
myDefaultWhiteList.style = []

var AppPage = (function($) {
    /*
    ================================================================
    Install via IGB App Manager
    ================================================================
    */

    function get_app_info(app_symbolicName, callback) {
        var manageApp = 'http://127.0.0.1:7090/manageApp';

        var xhr = createCORSRequest('POST', manageApp, null, app_symbolicName);

        if (!xhr) {
            return;
        }

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200 && callback) {
                callback(JSON.parse(this.response), this.status);
            }
        }

        xhr.send(JSON.stringify(formData))
    }

    function install_app(app_symbolicName, action, callback) {
        var manageApp = 'http://127.0.0.1:7090/manageApp';

        var xhr = createCORSRequest('POST', manageApp, action, app_symbolicName);

        if (!xhr) {
            return;
        }

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200 && callback) {
                callback(JSON.parse(this.response), this.status);
            }
        }

        xhr.send(JSON.stringify(formData))
    }

    /* Increases the download counter for a particular app when installed */
    function set_download_count(status) {
         $.post('', {'action': 'installed_count', 'status': status}, function(data) {
                // Can Write a Logic here if we change it in later phases
            });
    }

	var install_btn = $('#app-install-btn');
	var igb_version = $('#igb_version');
	var app_version = $('#app_version');
    var install_btn_last_class = [];

	function setup_install_btn(btn_class, icon_class, btn_text, appVersion, igbVersion, func) {

        if (install_btn_last_class.length !== 0)
            install_btn.removeClass(install_btn_last_class.pop());
            install_btn.addClass(btn_class);
            install_btn_last_class.push(btn_class);

            install_btn.find('i').attr('class', '');
            install_btn.find('i').addClass(icon_class);

            install_btn.find('h4').html(btn_text);
            app_version.html("<strong>Version </strong>"+appVersion);
            igb_version.html("IGB "+igbVersion);

            install_btn.off('click');
            install_btn.removeClass('disabled');
		if (func) {
            var license_modal = $('#license_modal');
            if (license_modal.length !== 0) {
                license_modal.find('.btn-primary').click(function() {
                    license_modal.modal('hide');
                    func();
                });
                install_btn.click(function() {
                    var license_iframe = license_modal.find('iframe');
                    license_iframe.attr('src', license_iframe.attr('data-src'));
                    license_modal.modal('show');
                });
            } else {
                /* license modal doesn't exist in DOM */
                install_btn.click(func);
            }
		} else {
			install_btn.addClass('disabled');
        }
	}


	function set_install_btn_to_installing(appVersion, igbVersion) {
		setup_install_btn('btn-info', 'icon-install-install', 'Installing...',appVersion, igbVersion);
    }

	function set_install_btn_to_install(app_name, app_symbolicName, appVersion, igbVersion) {

		setup_install_btn('btn-info', 'icon-install-install', 'Install', appVersion, igbVersion,
            function() {
                set_install_btn_to_installing(appVersion, igbVersion);
                install_app(app_symbolicName, "install", function(app_status, status) {
                    if (status == "200" && app_status.status == "INSTALLED") {
                        Msgs.add_msg(app_name + ' has been installed! Go to IGB to use it.', 'success');
                        set_download_count('Installed');
                        set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);
                    } else {
                        Msgs.add_msg('Could not install &ldquo;' + app_name + '&rdquo; app: <tt>' + app_status.status + '</tt>', 'danger');
                        set_install_btn_to_install(app_name, app_symbolicName, appVersion, igbVersion);
                    }
                });
            });
	}

	function set_install_btn_to_upgrading(appVersion, igbVersion) {
		setup_install_btn('btn-warning', 'icon-install-upgrade', 'Upgrading...',appVersion, igbVersion);
    }

	function set_install_btn_to_upgrade(app_name, app_symbolicName, appVersion, igbVersion) {
		setup_install_btn('btn-warning', 'icon-install-upgrade', 'Upgrade',appVersion, igbVersion,
            function() {
                set_install_btn_to_upgrading(appVersion, igbVersion);
                install_app(app_symbolicName, "update", function(app_status, status) {
                    if (status == "200" && app_status.status == "UPDATED") {
                        Msgs.add_msg(app_name + ' has been updated! Go to IGB to use it.', 'success');
                        set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);
                    } else {
                        Msgs.add_msg('Could not update &ldquo;' + app_name + '&rdquo; app: <tt>' + app_status.status + '</tt>', 'danger');
                        set_install_btn_to_install(app_name, app_symbolicName, appVersion, igbVersion);
                    }
                });
            });
	}

	function set_install_btn_to_installed(appVersion, igbVersion) {
		setup_install_btn('btn-success', 'icon-install-installed', 'Installed', appVersion, igbVersion);
	}

	function setup_install(app_name, app_symbolicName) {
		get_app_info(app_symbolicName,function(app_status, is_running) {
			if (is_running == "200") {
					if (app_status.status === 'NOT_FOUND' || app_status.status === 'UNINSTALLED') {
						set_install_btn_to_install(app_name, app_symbolicName, app_status.appVersion, app_status.igbVersion);
					} else if (app_status.status === 'INSTALLED') {
						set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);

					} else if (app_status.status === 'TO_UPDATE') {
                        set_install_btn_to_upgrade(app_name, app_symbolicName, app_status.appVersion, app_status.igbVersion);
					}
			} else {
				Msgs.add_msg('IGB is not running!', 'info');
				document.getElementById("app_status_block").style.display = "none";
			}
		});
	}


    // Create and return an XHR object.
    function createCORSRequest(method, url, action, app_symbolicName) {
        if(action != null) {
            // POST Data
            formData = {
                "symbolicName" : app_symbolicName,
                "action" : action
            };
        } else {
            // POST Data
            formData = {
                "symbolicName" : app_symbolicName,
                "action" : "getInfo"
            };
        }

        var xhr = new XMLHttpRequest();

        if ("withCredentials" in xhr) {
            // XHR for Chrome/Firefox/Opera/Safari.
            xhr.open(method, url, true);
        } else if (typeof XDomainRequest != "undefined") {
            // XDomainRequest for IE.
            xhr = new XDomainRequest();
            xhr.open(method, url);
        } else {
            // CORS not supported.
            xhr = null;
            console.log("CORS Not Supported");
        }

        return xhr;
    }
    /*
     ================================================================
       Stars
     ================================================================
    */

    function rating_to_width_percent(rating) {
        return Math.ceil(100 * rating / 5);
    }

    function width_percent_to_rating(width_percent) {
        return Math.ceil(width_percent * 5 / 100);
    }

    function cursor_x_to_rating(cursor_x, stars_width) {
        var rating = 5 * cursor_x / stars_width;
        if (rating <= 0.5)
            return 0;
        else if (rating > 5.0)
            return 5;
        else
            return Math.ceil(rating);
    }

    function setup_rate_popover(popover) {
        var stars_tag      = $('.popover-content .rating-stars');
        var stars_full_tag = $('.popover-content .rating-stars-filled');
        var rating = 5;
        $('.popover-title .close').click(function() {
            popover.popover('toggle');
        });
        $('.popover-content .rating-stars').mousemove(function(e) {
            var potential_rating = cursor_x_to_rating(e.pageX - $(this).offset().left, $(this).width());
            var width_percent = rating_to_width_percent(potential_rating);
            stars_full_tag.css('width', width_percent + '%');
        }).click(function() {
            rating = width_percent_to_rating(parseInt(stars_full_tag.css('width')));
            $('.popover-content #rate-btn #rating').text(rating);
        }).mouseleave(function() {
            var width_percent = rating_to_width_percent(rating);
            stars_full_tag.css('width', width_percent + '%');
        });
        $('.popover-content #rate-btn').click(function() {
            $(this).text('Submitting...').attr('disabled', 'true');
            $.post('', {'action': 'rate', 'rating': rating}, function(data) {
                popover.off('click').popover('destroy').css('cursor', 'default');
                popover.find('.rating-stars-filled').css('width', data.stars_percentage.toString() + '%');
                $('#rating-count').text('(' + data.votes.toString() + ')');
                popover.tooltip({'title': 'Your rating has been submitted. Thanks!'}).tooltip('show');
                setTimeout(function() {
                    popover.tooltip('hide');
                }, 5000);
            });
        });
    }

    function setup_stars() {
        var stars_tag       = $('#app-usage-info .rating-stars');
        var stars_empty_tag = $('#app-usage-info .rating-stars-empty');
        var stars_full_tag  = $('#app-usage-info .rating-stars-filled');
        stars_tag.popover({
            'container' : 'body',
            'html': true,
            'content': $('#rate-popover-content').html(),
            'trigger': 'manual'
        });
        stars_tag.click(function() {
            stars_tag.popover('toggle');
            setup_rate_popover($(this));
        });
        stars_empty_tag.click(stars_tag.click);
        stars_full_tag.click(stars_tag.click);
    }


    function setup_details() {
        $('#app-details-md');
    }

    /*
     ================================================================
       Release Notes
     ================================================================
    */

    function setup_release_notes() {
        $('.app-release-notes').each(function() {
            $(this).text;
        });

        $('.timeago').text;
    }

    /*
     ================================================================
       Init
     ================================================================
    */

    return {
	    'setup_install': setup_install,
//      'setup_twox_download_popover': setup_twox_download_popover,
        'setup_stars': setup_stars,
        'setup_details': setup_details,
        'setup_release_notes': setup_release_notes,
    }
})($);