$(document).ready(function() {

	/*
	 * Change the image
	 */
	
	$(".imageSmallContainer").click(function(evt){

    var imageid = $(this).data("imageid");
    var drawingid = $(this).data("drawingid");
    var ids = {imageid : imageid,
               drawingid : drawingid};
               
		$.get("/changeimage", ids)
			.done(function(data){
        var imageContainer = $("#imageContainer");
        imageContainer.css("opacity", "0.0");
        var image = $("#imageTarget");

        image.attr("src", data.imagefile);
        image.data("imageid", imageid);

        if (typeof drawingid != 'undefined') {
            var drawing = $("#drawingTarget");
            drawing.attr("src", data.drawingfile);
            drawing.data("id", drawingid);
          }
        imageContainer.animate({opacity: "1.0"}, 500);
			});
	});


  /*
   * Store drawing on server
   */
    
    $("#saveDrawing").click(function(evt){
      var drawing = $("#imagePaint").wPaint("image");
      var imageid = $("#imageTarget").data("imageid");

      $.ajax({
        type: 'POST',
        url: '/savedrawing',
        dataType: 'json',
        data: {drawing: drawing, imageid: imageid},
        success: function (resp) {
            console.log("profit");
            }
        });
    })

});
