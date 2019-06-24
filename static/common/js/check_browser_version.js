$(function() {
    function display_unsupported_msg() {
	    Msgs.add_msg('Your browser is not supported. Consider switching to <a href="http://www.getfirefox.com">Firefox</a>.', 'danger');
    }
    
    if (!$.support.ajax) {
        display_unsupported_msg();
    }
});
