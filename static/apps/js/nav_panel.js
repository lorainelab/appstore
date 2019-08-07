$(function() {
    var form = $('#search');
        form.find('button').click(function() {
        form.submit();
    });
});

$(function() {
    var TAG_LIST_COOKIE = 'igb.AppStore.Nav.TagList';

    function show_not_top_tags(animate) {
	$('#more-button').html('less &laquo;');
	if (animate)
	  $('#not-top-tags').slideDown('fast')
	else
	  $('#not-top-tags').show()
	Cookies.get(TAG_LIST_COOKIE, 'show_all', {path: '/'});
    }

    function hide_not_top_tags(animate) {
	$('#more-button').html('More &raquo;');
	if (animate)
	  $('#not-top-tags').slideUp('fast')
	else
	  $('#not-top-tags').hide()
	Cookies.get(TAG_LIST_COOKIE, 'show_some', {path: '/'});
    }

    if (Cookies(TAG_LIST_COOKIE) === 'show_all')
	show_not_top_tags(false);
    else
	hide_not_top_tags(false);

    $('#more-button').click(function() {
	if ($('#not-top-tags').is(':visible')) {
	    hide_not_top_tags(true);
	} else {
	    show_not_top_tags(true);
	}
    });

});

$(function() {
    var TAGS_COOKIE = 'igb.AppStore.Nav.Tags';

    function show_tag_list(animate) {
        $('#tag-cloud').hide();
        $('#tag-list').show(animate ? 'fast' : '');
        $('#tag-buttons button').removeClass('active');
        $('#tag-buttons #tag-list-btn').addClass('active');
        Cookies.get(TAGS_COOKIE, 'tag_list', {path: '/'})
    }

    function show_tag_cloud(animate) {
        $('#tag-list').hide();
        $('#tag-cloud').show(animate ? 'fast' : '');
        $('#tag-buttons button').removeClass('active');
        $('#tag-buttons #tag-cloud-btn').addClass('active');
        Cookies.get(TAGS_COOKIE, 'tag_cloud', {path: '/'})
    }

    if (Cookies(TAGS_COOKIE) === 'tag_cloud')
	    show_tag_cloud(false);
    else
	    show_tag_list(false);
    
    $('#tag-buttons #tag-list-btn').click(function() {
	if (!($('#tag-list').is(':visible')))
	    show_tag_list(true);
    });

    $('#tag-buttons #tag-cloud-btn').click(function() {
	if (!($('#tag-cloud').is(':visible')))
	    show_tag_cloud(true);
    });
});