




jQuery(document).ready(function(){
  jQuery("#myModal").bmdIframe();
});


jQuery(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});


function UpdateProgress(totalRecords, recordsProcessed) {

  var pct = recordsProcessed / totalRecords * 100;
  $('.progress-bar').css('width', pct + '%').attr('aria-valuenow', pct);



    var msg = Math.round(pct, 2) + '%' + '- De:' + recordsProcessed + ' - Para: ' + totalRecords;

  //$('.progText').text(msg);
   //$('.justify-content-center').text(msg);


  $('#message').text(msg);

  //if (pct > 0) {
  //  $('#progressRow').show();
  //}

  //if (pct == 100) {
  //  $('#progressRow').hide();
    //$('#message').text('Exportação Completa');
  //}

}

function fnc_update_progress_bar(max_value, file) {
    jQuery.get(file, function(data) {
        var myvar = data;
        UpdateProgress(max_value, myvar)
    })
}
