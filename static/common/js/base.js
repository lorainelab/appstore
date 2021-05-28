$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

$(document).ready(function(){

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
    if(current_link==='https://apps.bioviz.org'){
        $(this).attr('href', '/');
    }

});

$(document).ready(function() {

  $('[data-toggle="popover"]').popover();


  // Gets the video src from the data-src
  var $videoSrc;
  $('.video-btn').click(function() {
      $videoSrc = $(this).data( "src" );
  });

  // when the modal is opened autoplay it
  $('#myModal').on('shown.bs.modal', function (e) {
    $("#video").attr('src',$videoSrc + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0" );
  })

  // stop playing the youtube video when I close the modal
  $('#myModal').on('hide.bs.modal', function (e) {
      $("#video").attr('src',$videoSrc);
  })
});
