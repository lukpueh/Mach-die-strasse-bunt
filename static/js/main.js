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
    popup("Die besten eingeschickten Zeichnungen werden als Freecard abgespeichert. \
      Mit dem Klick auf den Speicherbutton erklärst du dich dafür bereit, dass dein Bild veröffentlicht wird.");
    // var drawing = $("#imagePaint").wPaint("image");
    // var imageid = $("#imageTarget").data("imageid");

    // $.ajax({
    //   type: 'POST',
    //   url: '/savedrawing',
    //   dataType: 'json',
    //   data: {drawing: drawing, imageid: imageid},
    //   success: function (resp) {
    //       console.log("profit");
    //       }
    //   });
  })



  function popup(message) {
      
    // get the screen height and width  
    var maskHeight = $(document).height();  
    var maskWidth = $(window).width();
    
    // calculate the values for center alignment
    var dialogTop =  (maskHeight/2) - ($('#dialog-box').height()/2);  
    var dialogLeft = (maskWidth/2) - ($('#dialog-box').width()/2); 
    
    // assign values to the overlay and dialog box
    $('#dialog-overlay').css({height:maskHeight, width:maskWidth}).show();
    $('#dialog-box').css({top:dialogTop, left:dialogLeft}).show();
    
    // display the message
    $('#dialog-message').html(message);
        
  }


  $('a.btn-ok, #dialog-overlay').click(function () {   
    $('#dialog-overlay, #dialog-box').hide();   
    return false;
  });

});
