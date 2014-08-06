$(document).ready(function(){

	/*
	 * Change the image
	 */
	
	$(".imageSmallContainer").click(function(evt){
		var imageid = $(this).find("img.imageSmall").data("imageid");
		$.get("/changeimage", { "imageid": imageid })
			.done(function(data){
				var target = $("img.imageRegular");
				target.attr("src", data.file);
				target.attr("id", imageid);
			});
	});

	/*
	 * Initialize wPaint
	 */
    $('#wPaintArea').wPaint({  
    	menuOrientation: 'vertical',
    	menuHandle: false,
	    menuOffsetLeft: 850,
  	});
});
