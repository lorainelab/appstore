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

    function get_app_info(app_bundleSymbolicName, repository_url, callback) {
        var manageApp = 'http://127.0.0.1:7090/manageApp';

        var xhr = createCORSRequest('POST', manageApp, null, app_bundleSymbolicName);

        if (!xhr) {
            return;
        }

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200 && callback) {
                callback(JSON.parse(this.response), this.status);
            } else if(xhr.readyState === 4 && xhr.status === 0) {
                get_old_app(app_bundleSymbolicName, function(app_status, is_running) {
			        if (is_running == "200") {
			            Msgs.add_msg('Please update to a newer version of IGB @ <a href="https://bioviz.org/download.html" target="_blank"> Click Here </a>',
			             'info');
			             document.getElementById("app-install-btn").onclick = getIgb;
			             //$("#igb_version").replaceWith($("#igb_version").text(""));
			        } else {
			            Msgs.add_msg('To install an App, start IGB version 9.1.0 or later. Then reload this page.', 'info');
			            document.getElementById("app-install-btn").onclick = getIgb;
			            //$("#igb_version").replaceWith($("#igb_version").text(""));
			        }
			    });
            } else if(xhr.readyState === 4 && xhr.status === 404) {
                // Usually happens when Appstores OBR is not added to the IGB Desktop Apps Repository
                Msgs.add_msg('Before IGB can load Apps, add this App Store to IGB. Open the App Manager (Tools menu) and click Manage Repositories.' +
                    ' Then click "Add" to add the URL ' + repository_url, 'info');
                document.getElementById("app-install-btn").set = getIgb;
                //$("#igb_version").replaceWith($("#igb_version").text(""));
          }
        }
    }

    function get_old_app(app_bundleSymbolicName, callback) {
        var manageApp = 'http://127.0.0.1:7085/igbStatusCheck';

        var xhr = createCORSRequest('GET', manageApp, null, app_bundleSymbolicName);

        if (!xhr) {
            return;
        }

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200 && callback) {
                callback(this.response, this.status);
            } else if(xhr.readyState === 4 && xhr.status === 0 && callback) {
                Msgs.add_msg('To install an App, start IGB version 9.1.0 or later. Then reload this page.', 'info');
                document.getElementById("app-install-btn").onclick = getIgb;
                //$("#igb_version").replaceWith($("#igb_version").text(""));
            }
        }
    }

    function install_app(app_bundleSymbolicName, action, callback) {
        var manageApp = 'http://127.0.0.1:7090/manageApp';

        var xhr = createCORSRequest('POST', manageApp, action, app_bundleSymbolicName);
        if (!xhr) {
            return;
        }

        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200 && callback) {
                callback(JSON.parse(this.response), this.status);
            }
        }
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
        install_btn_last_class = [... install_btn[0]['classList']]
        var index = install_btn_last_class.indexOf('disabled');
        if (index > -1) {
            install_btn_last_class.splice(index, 1);
        }
        if (install_btn_last_class.length !== 0)
            install_btn.removeClass(install_btn_last_class.pop());
            install_btn.addClass(btn_class);
            install_btn_last_class.push(btn_class);

            install_btn.find('h6').html("<i></i>&nbsp;&nbsp;&nbsp;" + btn_text);

            install_btn.find('h6').find('i').attr('class', '');
            install_btn.find('h6').find('i').addClass(icon_class);
            //app_version.html("<strong>App Version </strong>" + appVersion);
            //igb_version.html("IGB " + igbVersion);

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
		setup_install_btn('btn-success', 'fa fa-download', 'Installing...',appVersion, igbVersion);
    }

	function set_install_btn_to_install(app_bundleName, app_bundleSymbolicName, appVersion, igbVersion) {
		setup_install_btn('btn-success', 'fa fa-download', 'Install this App', appVersion, igbVersion,
            function() {
                set_install_btn_to_installing(appVersion, igbVersion);
                install_app(app_bundleSymbolicName, "install", function(app_status, status) {
                    if (status == "200" && app_status.status == "INSTALLED") {
                        Msgs.add_msg(app_bundleName + ' has been installed! Go to IGB to use it.', 'success');
                        set_download_count('Installed');
                        set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);
                    } else {
                        Msgs.add_msg('Could not install &ldquo;' + app_bundleName + '&rdquo; app: <tt>' + app_status.status + '</tt>', 'danger');
                        set_install_btn_to_install(app_bundleName, app_bundleSymbolicName, appVersion, igbVersion);
                    }
                });
            });
	}

	function set_install_btn_to_upgrading(appVersion, igbVersion) {
		setup_install_btn('btn-warning', 'icon-install-upgrade', 'Upgrading...',appVersion, igbVersion);
    }

	function set_install_btn_to_upgrade(app_bundleName, app_bundleSymbolicName, appVersion, igbVersion) {
		setup_install_btn('btn-warning', 'fa fa-arrow-circle-up', 'Upgrade this App',appVersion, igbVersion,
            function() {
                set_install_btn_to_upgrading(appVersion, igbVersion);
                install_app(app_bundleSymbolicName, "update", function(app_status, status) {
                    if (status == "200" && app_status.status == "UPDATED") {
                        Msgs.add_msg(app_bundleName + ' has been updated! Go to IGB to use it.', 'success');
                        set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);
                        set_download_count('Installed');
                    } else {
                        Msgs.add_msg('Could not update &ldquo;' + app_bundleName + '&rdquo; app: <tt>' + app_status.status + '</tt>', 'danger');
                        set_install_btn_to_install(app_bundleName, app_bundleSymbolicName, appVersion, igbVersion);
                    }
                });
            });
	}

	function set_install_btn_to_installed(appVersion, igbVersion) {
		setup_install_btn('btn-success', 'fa fa-check', 'Installed', appVersion, igbVersion);
	}


	function setup_install(app_bundleName, app_bundleSymbolicName, repository_url, release_BundleVersion) {
		get_app_info(app_bundleSymbolicName, repository_url, function(app_status, is_running) {
			if (is_running == "200") {

			        if(compareVersion(app_status.appVersion, release_BundleVersion) == -1 && app_status.status != "TO_UPDATE") {
			            document.getElementById("app-install-btn").setOn = getIgb;

			        } else if (app_status.status === 'NOT_FOUND' || app_status.status === 'UNINSTALLED') {
                        document.getElementById("change-url").href = "#";
                        set_install_btn_to_install(app_bundleName, app_bundleSymbolicName, app_status.appVersion, app_status.igbVersion);

                    } else if (app_status.status === 'INSTALLED') {
                        document.getElementById("change-url").href = "#";
                        set_install_btn_to_installed(app_status.appVersion, app_status.igbVersion);

                    } else if (app_status.status === 'TO_UPDATE') {
                        document.getElementById("change-url").href = "#";
                        set_install_btn_to_upgrade(app_bundleName, app_bundleSymbolicName, app_status.appVersion, app_status.igbVersion);
                    }
                    
			} else {
                Msgs.add_msg('To install an App, start IGB version 9.1.0 or later. Then reload this page.', 'info');
                document.getElementById("app-install-btn").setOn = getIgb;
                //$("#igb_version").replaceWith($("#igb_version").text(""));
            }
		});
	}

	function getIgb(){
	    window.open('https://bioviz.org', '_blank');
	}

	function compareVersion(v1, v2) {
        if (typeof v1 !== 'string') return false;
        if (typeof v2 !== 'string') return false;
        v1 = v1.split('.');
        v2 = v2.split('.');
        const k = Math.min(v1.length, v2.length);
        for (let i = 0; i < k; ++ i) {
            v1[i] = parseInt(v1[i], 10);
            v2[i] = parseInt(v2[i], 10);
            if (v1[i] > v2[i]) return 1;
            if (v1[i] < v2[i]) return -1;
        }
    return v1.length == v2.length ? 0: (v1.length < v2.length ? -1 : 1);
    }


    // Create and return an XHR object.
    function createCORSRequest(method, url, action, app_bundleSymbolicName) {
        if(action != null) {
            // POST Data
            formData = {
                "symbolicName" : app_bundleSymbolicName,
                "action" : action
            };
        } else {
            // POST Data
            formData = {
                "symbolicName" : app_bundleSymbolicName,
                "action" : "getInfo"
            };
        }

        var xhr = new XMLHttpRequest();

        if ("withCredentials" in xhr) {
            // XHR for Chrome/Firefox/Opera/Safari.
            xhr.open(method, url, true);
            xhr.send(JSON.stringify(formData))
        } else if (typeof XDomainRequest != "undefined") {
            // XDomainRequest for IE.
            xhr = new XDomainRequest();
            xhr.open(method, url);
            xhr.send(JSON.stringify(formData))
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
       Init
     ================================================================
    */

    return {
	    'setup_install': setup_install,
//      'setup_twox_download_popover': setup_twox_download_popover,
        'setup_stars': setup_stars,
        'setup_details': setup_details,
    }
})($);