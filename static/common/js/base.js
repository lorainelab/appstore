$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

var bioviz_url = $('#bioviz-url').text();

$('#TopMenu').find('a').each(function() {
    var current_link = $(this).attr('href');
    if(current_link === undefined) {
        current_link = '#';
    }
    if(!current_link.startsWith('http')){
        $(this).attr('href', bioviz_url + current_link);
    }
});