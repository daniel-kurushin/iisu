var MEASURE_URL = 'http://192.168.0.101:8001/state';
var ON48V_URL = 'http://192.168.0.101:8001/48v/on';
var OFF48V_URL = 'http://192.168.0.101:8001/48v/off';

function measure()
{
    $.get(MEASURE_URL, function(data){
        $('#U_12').text(data['U_12']);
        $('#I_12').text(data['I_12']);
        $('#I_48').text(data['I_48']);
    });
}

function do48vOFF()
{
    $.get(OFF48V_URL, function(){
    	measure();
    });
}

function do48vON()
{
    $.get(ON48V_URL, function(){
    	measure();
    });
}

$(document).ready(function(){
	measure();
}
)