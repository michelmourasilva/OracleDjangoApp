(function($) {

    $.fn.bmdIframe = function( options ) {
        var self = this;

        var settings = $.extend({
            classBtn: '.btn-default',
            defaultW: 640,
            defaultH: 360

        }, options );
      
        $(settings.classBtn).on('click', function() {


          var src = $(this).attr('data-bmdSrc')

          var allowFullscreen = $(this).attr('data-bmdVideoFullscreen') || false;

          var dataVideo = {
            'src': $(this).attr('data-bmdSrc'),
            'height': $(this).attr('data-bmdHeight') || settings.defaultH,
            'width': $(this).attr('data-bmdWidth') || settings.defaultW
          };

            var v_oracle_user = document.getElementById('v_oracle_user').value
            var v_oracle_password = document.getElementById('v_oracle_password').value
            var lst_servers  = document.getElementsByName('lst_servers')
            var v_sql_file  = document.getElementById('v_sql_file').value

            var v_csv_splitter  = document.getElementById('v_csv_splitter').value
            var v_sql_query  = document.getElementById('v_sql_query').value
            var v_path_export  = document.getElementById('v_path_export').value

            var lst_file_import  = document.getElementById('lst_file_import').value
            var v_sql_loader_splitter  = document.getElementById('v_sql_loader_splitter').value
            var v_sql_loader_owner = document.getElementById('v_sql_loader_owner').value
            var v_sql_loader_table = document.getElementById('v_sql_loader_table').value
            var v_sql_loader_head = document.getElementById('v_sql_loader_head').value
            var v_sql_loader_constants = document.getElementById('v_sql_loader_constants').value


           var v_lst_servers = "";
            for (var i=0, n=lst_servers.length;i<n;i++)
            {
                if (lst_servers[i].checked)
                {
                    v_lst_servers += "&lst_servers="+lst_servers[i].value;
                }
            }
            if (v_lst_servers) v_lst_servers = v_lst_servers.substring(1);


            var v_frame = 'http://127.0.0.1:8000/Oracle/OracleFunctions/?'+ v_lst_servers
            v_frame = v_frame + '&v_action=' + src

            v_frame = v_frame +  '&v_sql_file=' + v_sql_file
            v_frame = v_frame +  '&v_csv_splitter=' + encodeURIComponent(v_csv_splitter)
            v_frame = v_frame +  '&v_sql_query=' + v_sql_query
            v_frame = v_frame +  '&v_path_export=' + v_path_export

            v_frame = v_frame +  '&lst_file_import=' + lst_file_import
            v_frame = v_frame +  '&v_sql_loader_splitter=' + encodeURIComponent(v_sql_loader_splitter)
            v_frame = v_frame +  '&v_sql_loader_owner=' + v_sql_loader_owner
            v_frame = v_frame +  '&v_sql_loader_table=' + v_sql_loader_table
            v_frame = v_frame +  '&v_sql_loader_head=' + v_sql_loader_head
            v_frame = v_frame +  '&v_sql_loader_constants=' + v_sql_loader_constants

            v_frame = v_frame +  '&v_oracle_user=' + v_oracle_user
            v_frame = v_frame +  '&v_oracle_password=' + v_oracle_password

          dataVideo.src = v_frame

          if ( allowFullscreen ) dataVideo.allowfullscreen = "";


          $(self).find("iframe").attr(dataVideo);
        }
        );

        this.on('hidden.bs.modal', function(){
          $(this).find('iframe').html("").attr("src", "");
        });
      
        return this;
    };
  
})(jQuery);
jQuery(document).ready(function(){
  jQuery("#myModal").bmdIframe();

});

$.fn.modal.prototype.constructor.Constructor.DEFAULTS.backdrop = 'static';
$.fn.modal.prototype.constructor.Constructor.DEFAULTS.keyboard = false;