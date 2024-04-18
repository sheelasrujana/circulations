
$('#result').on('change', function() {
  $('#permanent').css('display', 'none');
  if ( $(this).val() === 'permanent' ) {
    $('#permanent').css('display', 'block');
  }
});



$('#result').on('change', function() {
  $('#specific').css('display', 'none');
  if ( $(this).val() === 'specific_date' ) {
    $('#specific').css('display', 'block');
  }
});

$('#copies').on('change', function() {
  $('#increase').css('display', 'none');
  if ( $(this).val() === 'increase' ) {
    $('#increase').css('display', 'block');
  }
});



$('#copies').on('change', function() {
  $('#decrease').css('display', 'none');
  if ( $(this).val() === 'decrease' ) {
    $('#decrease').css('display', 'block');
  }
});

$('#additional_types').on('change', function() {
  $('#increase_additional').css('display', 'none');
  if ( $(this).val() === 'increase_additional' ) {
    $('#increase_additional').css('display', 'block');
  }
});



$('#additional_types').on('change', function() {
  $('#decrease_additional').css('display', 'none');
  if ( $(this).val() === 'decrease_additional' ) {
    $('#decrease_additional').css('display', 'block');
  }
});


$(function(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var minDate= year + '-' + month + '-' + day;

    $('#txtDate').attr('min', minDate);
});



$(function(){
    var dtToday = new Date();

    var month = dtToday.getMonth() + 1;
    var day = dtToday.getDate();
    var year = dtToday.getFullYear();
    if(month < 10)
        month = '0' + month.toString();
    if(day < 10)
        day = '0' + day.toString();

    var minDate= year + '-' + month + '-' + day;

    $('#txtDateNew').attr('min', minDate);
});