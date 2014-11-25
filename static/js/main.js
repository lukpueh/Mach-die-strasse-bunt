/*
 * Store drawing on server
 */
  
function saveDrawing() {

  var drawing = $('#imagePaint').wPaint('image');
  var imageid = $('#imageTarget').data('imageid');
  var creatormail = $('input[name=creatorMail]').val();

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

function saveDrawingLocal() {

    var imageid = $('img#imageTarget').data('imageid');
    var drawingid = $('img#drawingTarget').data('drawingid');

    window.location.href = 'getfile?drawingid=' + drawingid + '&imageid=' + imageid;
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
    var emailriddlerarray=[104,111,115,116,109,97,115,116,101,114,64,109,97,99,104,100,105,101,115,116,114,97,115,115,101,98,117,110,116,46,99,111,109]
    var encryptedemail_id65='' //variable to contain encrypted email 
    for (var i=0; i<emailriddlerarray.length; i++)
     encryptedemail_id65+=String.fromCharCode(emailriddlerarray[i])

    $('#mailMaster').attr('href', 'mailto:' + encryptedemail_id65 );

  var emailriddlerarray=[105,110,102,111,64,109,97,99,104,100,105,101,115,116,114,97,115,115,101,98,117,110,116,46,99,111,109]
  var encryptedemail_id23='' //variable to contain encrypted email 
  for (var i=0; i<emailriddlerarray.length; i++)
   encryptedemail_id23+=String.fromCharCode(emailriddlerarray[i])

    $('#mailInfo').attr('href', 'mailto:' + encryptedemail_id23 );


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

        //Hide all images in container
        imageContainer.children('.imageRegular').hide();

        //Add spinning wheel
        var spin = $(document.createElement('div'));
        spin.addClass('spin');
        imageContainer.prepend(spin);

        //Remove hidden old image
        $('#imageTarget').remove();

        //Create new hidden image
        var imageNew = $(document.createElement('img'));
        imageNew.attr('id', 'imageTarget');
        imageNew.addClass('imageRegular');
        imageNew.attr('data-imageid', imageid);
        imageNew.data('imageid', imageid);
        imageNew.attr('src', data.imagefile);
        imageNew.css('display', 'none');

        //Prepend new Image to container
        imageContainer.prepend(imageNew);

        //For Admin and Gallery also change Drawing
        if (typeof drawingid != 'undefined') {
            var drawing = $('#drawingTarget');
            drawing.attr('src', data.drawingfile);
            drawing.attr('data-drawingid', drawingid);
            drawing.data('drawingid', drawingid);
            drawing.attr('drawingid', drawingid);
          }

        // If newImage src is loaded, remove spin and fade all imgs
        // Fires too early in FF
        imageContainer.imagesLoaded(function() {
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
