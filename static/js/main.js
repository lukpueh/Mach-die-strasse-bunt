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

  $(".imageSmallContainerOuter input").change(function(evt){
      var container = $(this).parent();
      var initial = container.data('initialstate');
      var checked = $(this).prop('checked');

      container.removeClass('notApproved');
      container.removeClass('approved');
      container.removeClass('changed');

      if (checked && initial == 'approved')
        container.addClass('approved');
      else if ((checked && initial == 'notApproved') || (!checked && initial == 'approved'))
        container.addClass('changed');
      else if (!checked && initial == 'notApproved')
        container.addClass('notApproved')



    });

  /*
   * Store drawing on server
   */
    
    $("#drawingSaveBtn").click(function(evt){
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
