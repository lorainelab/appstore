var PendingApps = (function() {
    var alerts = $('#alerts');
    function setup_accept_and_decline_btns() {
        $('[pending_id]').each(function() {
            var pending_tag = $(this);
            var app_name = $(this).find('.app-name-pending').text();
            var app_version = $(this).find('.app-version').text();
            var symbolic_name = $(this).find('.Bundle_SymbolicName').text();
            console.log(symbolic_name);
            var pending_id = $(this).attr('pending_id');
            
            function do_action(action, msg, msg_type) {
                pending_tag.find('.btn').hide();
                pending_tag.find('.loading').show();
                $.post('',
                       {'action': action,
                       'pending_id': pending_id},
                       function() {
                            pending_tag.hide('slow', function() {
                                pending_tag.remove();
                            });
                            msg = msg.replace('%s', app_name + ' ' + app_version);
                            Msgs.add_msg(msg, msg_type, 'rating');
                       });
            }
            
            $(this).find('.accept').click(function() {
                var accept_msg = "Congratulations! You released an App <strong>" +  app_name.trim() + "</strong>, with Bundle_SymbolicName <strong>" + symbolic_name.trim() + "</strong>, and Bundle_Version <strong>" + app_version.trim() + "</strong>. If this is the highest available version, please confirm that you can now install it using <a href='/apps/" + symbolic_name + "' target='_blank'>this App Store page</a>. Also confirm that you can install the expected highest compatible versions within IGB using IGB App Manager. Note that all versions ever submitted to App Store – including this one – are listed on the <a href='/obr/releases' target='_blank'>App Store OBR index endpoint</a>. Please check that as well!";
                do_action('accept', accept_msg, 'success')
            });
            $(this).find('.decline').click(function() {
                do_action('decline', '%s has been declined.', 'danger')
            });
        });
    }
    
    return {
        'setup_accept_and_decline_btns': setup_accept_and_decline_btns,
    };
})();