    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.js"></script>

    <center>
    <br><br><br>

    <select class="selectpicker" onChange="window.document.location.href=this.options[this.selectedIndex].value;">
  
    <script type="text/javascript">

    jQuery.getJSON("parameters-Copter.json", {}, function(json) {
        $.each(json, function(key, value) {
        $('.selectpicker').append('<option value="' + json[key] + '">' + key + '</option>');
        });
    });

    </script>
