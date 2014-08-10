$(document).ready(function(){

	/*
	 * Change the image
	 */
	
	$(".imageSmallContainer").click(function(evt){
		var imageid = $(this).find("img.imageSmall").data("imageid");
		$.get("/changeimage", { "imageid": imageid })
			.done(function(data){
				var target = $("img#imageBackground");
				target.attr("src", data.file);
				target.data("imageid", imageid);
			});
	});

    function saveImg(drawing) {
      var _this = this;

      var imageid = $("img#imageBackground").data("imageid");

      var formData = new FormData();
      formData.append("imageid", imageid);

      $.ajax({
        type: 'POST',
        url: '/savedrawing',
        dataType: 'json',
        data: {drawing: drawing, imageid: imageid},
        success: function (resp) {
            console.log("profit");
            }
        });
    }
	/*
	 * Initialize wPaint
	 */
    $('#imagePaint').wPaint({  
        path:            '/wPaint/',
        menuHandle:      false,               // setting to false will means menus cannot be dragged around
        menuOrientation: 'vertical',       // menu alignment (horizontal,vertical)
        menuOffsetLeft:  -50,                  // left offset of primary menu
        menuOffsetTop:   0,
        saveImg: saveImg
  	});

});
