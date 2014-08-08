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

	/*
	 * Initialize wPaint
	 */
   //  $('#imagePaint').wPaint({  
   //  	menuOrientation: 'vertical',
   //  	menuHandle: false,
	  //   menuOffsetLeft: 850,
  	// });

    /*
     * Send painting
     */

//      $("#saveimage").click(function(evt){
//      	//TODO:
//      	// make toDataUrl safer
//      	// perform some checks
//      	// 		is there an image?
//      	// 		is there a valid background?
//      	var c = $(".wPaint-canvas")[0];
//      	console.log(c);
//      	var painting = c.toDataURL();
//      	var imageid = $("img.imageBackground").data("imageid");
     	

//      	$.post("/savepainting", {"imageid" : imageid, "painting" : painting })
//      		.done(function(data){
//      			//Give some feedback
//      			console.log("sent successfully, yeah!");
//      		})
//      		.fail(function(data){
//      			//Give some feedback
//      			console.log("couldn't send, oh nooo!");
//      		});
//      });
});
