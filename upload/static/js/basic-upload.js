/* Credit to Vitor Freitas https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html */
$(function () {
  $("#fileupload").fileupload({
    dataType: 'json',
    done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
      if (data.result.is_valid) {
        $("#gallery tbody").prepend(
          "<tr><td class=\"text-left\"><a href='" + data.result.url + "'>" + data.result.name.split("/")[2] + "</a></td></tr>"
        );
        $("#fileupload-arrow").remove();
      }
    }
  });

});