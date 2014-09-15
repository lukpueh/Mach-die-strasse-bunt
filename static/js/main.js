var emptySrc = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=';


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
      url: 'savedrawing',
      dataType: 'json',
      data: {drawing: drawing, imageid: imageid, creatormail: creatormail},
      success: function (resp) {
        if (resp.kind == 'success')
          popup("<p>Die Zeichnung wurde erfolgreich gespeichert.</p><p>Sie wird jedoch zuerst überprüft bevor sie in der Galerie zu sehen ist.</p>");
        if (resp.kind == 'error')
          popup("<p>Die Zeichnung konnte leider nicht gespeichert werden.</p><p>Der Fehler wird untersucht.</p>");
      },
      fail: function() {
        popup("<p>Die Zeichnung konnte leider nicht gespeichert werden.</p><p>Der Fehler wird untersucht.</p>");
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
               
		$.get('changeimage', ids)
			.done(function(data){
        var imageContainer = $('#imageContainer');
        var image = $('#imageTarget');

        //Add spinning wheel
        var spin = $(document.createElement('div'));
        spin.addClass('spin');

        image.attr('src', emptySrc);

        imageContainer.children('.imageRegular').hide();
        imageContainer.prepend(spin);

        //Image Load fires incorrectly in FF
        //Replace Image with empty image so at least it doesn't flickr

        image.attr('src', data.imagefile);
        image.data('imageid', imageid);

        //For Admin and Gallery also change Drawing
        if (typeof drawingid != 'undefined') {
            var drawing = $('#drawingTarget');
            drawing.attr('src', emptySrc);
            drawing.attr('src', data.drawingfile);
            drawing.data('id', drawingid);
          }

        imageContainer.imagesLoaded( function() {
          spin.remove();
          imageContainer.children('.imageRegular').fadeIn();
        });
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
        popup("<p>Aus den besten eingeschickten Zeichnungen werden Freecards gedruckt.</p> \
      <p>Mit dem Klick auf den Speicherbutton erklärst du dich dafür bereit, dass dein Bild vielleicht veröffentlicht wird.</p> \
      <p>Wenn du deine Email-Adresse angibst können wir dich informieren falls wir deine Zeichnung ausgewählt haben.</p> \
      <input type='text' name='creatorMail' placeholder='Email Adresse'> \
      <a id='drawingSaveBtn' href='javascript:saveDrawing();' class='btn'>Speichern</a>");
    });

});
