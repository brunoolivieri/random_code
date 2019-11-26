.. _parameters-landingpage-test1:

========================
Parameters (landingpage)
========================


Sample landingpage to multiple versions of parameters. lorem ipsum dolor sit amet...

-  **List of available parameters**

..raw:: html

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
	
	
	
foooooooooooooooooooooooooooooooooooooooo

..raw:: html

    <embed>
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
    </embed>
	
	
faaaaaaaaaaaaaaaaaaaaaaaa


{%- block extrahead %} 

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

{% endblock %}




