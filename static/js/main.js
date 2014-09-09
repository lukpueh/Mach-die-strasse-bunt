  /*
   * Store drawing on server
   */
    
  function saveDrawing() {

    var drawing = $("#imagePaint").wPaint("image");
    var imageid = $("#imageTarget").data("imageid");
    var creatormail = $("input[name=creatorMail]").val();

    //Add spinning wheel
    var spin = $(document.createElement('div'));
    spin.addClass('spin');
    $('#dialog-content').html(spin);

    $.ajax({
      type: 'POST',
      url: '/savedrawing',
      dataType: 'json',
      data: {drawing: drawing, imageid: imageid, creatormail: creatormail},
      success: function (resp) {
        popup("Das Bild wurde erfolgreich gespeichert. Es kann jedoch ein paar Tage dauern bis es in der Galerie angezeigt wird.");
        },
      fail: function(resp) {
        popup("Das Bild konnte leider nicht gespeichert werden.")
      }

      });
  }

  /*
   * Popup message
   */

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
    $('#dialog-content').html(message);
        
  }

$(document).ready(function() {


    /***********************************************
    * Encrypt Email script- Please keep notice intact
    * Tool URL: http://www.dynamicdrive.com/emailriddler/
    * **********************************************/
    var emailriddlerarray=[108,117,107,46,112,117,101,104,114,105,110,103,101,114,64,103,109,97,105,108,46,99,111,109]
    var encryptedemail_id79='' //variable to contain encrypted email 
    for (var i=0; i<emailriddlerarray.length; i++)
      encryptedemail_id79+=String.fromCharCode(emailriddlerarray[i])

    $('#mailLink').attr('href', 'mailto:' + encryptedemail_id79 );
    //--- VARIABLE "encryptedemail_id79" NOW CONTAINS YOUR ENCRYPTED EMAIL. USE AS DESIRED. ---// 

	/*
	 * Change image
	 */
	
	$(".imageSmallContainer").click(function(evt){

    var imageid = $(this).data('imageid');
    var drawingid = $(this).data('drawingid');
    var ids = {imageid : imageid,
               drawingid : drawingid};
               
		$.get('/changeimage', ids)
			.done(function(data){
        var imageContainer = $('#imageContainer');
        imageContainer.css('opacity', '0.0');
        var image = $('#imageTarget');

        image.attr('src', data.imagefile);
        image.data('imageid', imageid);

        //For Admin and Gallery also change Drawing
        if (typeof drawingid != 'undefined') {
            var drawing = $('#drawingTarget');
            drawing.attr('src', data.drawingfile);
            drawing.data('id', drawingid);
          }

        imageContainer.animate({opacity: '1.0'}, 500);
			});
	});

  /*
   * Change the class of moderated images
   */

  $('.imageSmallContainerOuter input').change(function(evt){
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

  $('#dialog-box .close, #dialog-overlay').click(function () {   
    $('#dialog-overlay, #dialog-box').hide();   
    return false;
  });

  $('#drawingDialogBtn').click(function(evt){
        popup("Aus den besten eingeschickten Zeichnungen werden Freecards gedruckt. \
      Mit dem Klick auf den Speicherbutton erklärst du dich dafür bereit, dass dein Bild vielleicht veröffentlicht wird. \
      Wenn du deine Emailadresse angibst, können wir dich informieren, falls wir deine Zeichnung ausgewählt haben. \
      <p>Email:</p> \
      <input type=text name=creatorMail> \
      <a id='drawingSaveBtn' href='javascript:saveDrawing();' class='btn'>Speichern</a>");
    });

});
