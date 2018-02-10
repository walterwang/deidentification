/**
 * Created by walter on 1/15/18.
 */
$(document).on('hide.bs.dropdown', function (e) {
  if ($(e.currentTarget.activeElement).hasClass('dropdown-toggle')) {
    $(e.relatedTarget).parent().removeClass('open');
    return true;
  }
  return false;
});


$(function() {
    $('#upload-file').submit(function(event) {
        event.preventDefault();
        var files = $("#document-file").val();
        if (files.length > 0) {
            $("#file_status").text("processing...");
            $("#upload-file input:submit").prop("disabled", true);
            var zip_name = $.now();
            var form_data = new FormData($('#upload-file')[0]);
            var show_bio = $("input[name='display_label']:checked").val()
            form_data.append("zip_name", zip_name)
            form_data.append("show_bio", show_bio)
            $.ajax({
                type: 'POST',
                enctype: 'multipart/form-data',
                url: '/upload_files',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                async: false,
                success: function (data) {
                    window.location.href = $SCRIPT_ROOT + "/download_deid_files/" + zip_name;
                    $("#upload-file input:submit").prop("disabled", false);
                    $("#file_status").text("");
                },
            });
        } else {
            alert("No files Select");
        }
    });
});

$(function() {
    $('#target').submit(function(event) {
        $("#target input:submit" ).prop( "disabled", true );
        $("#result").text("loading...");
      $.getJSON($SCRIPT_ROOT + '/submit_text', {
        input_text: $('textarea[name="input_text"]').val(),
        show_bio: $("input[name='display_label']:checked").val()
      }, function(data) {

        $("#result").text(data.deided_text);
        $("#target input:submit" ).prop( "disabled", false );
      });
      event.preventDefault();
    });
});

function resetbtnstate() {

    $('#display_bio_show').removeClass('active');
    $('#display_bio_hide').addClass('active');
    $( "#inlineradio2" ).prop( "checked", true );

};