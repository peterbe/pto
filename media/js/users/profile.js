var dateFormat = 'DD, MM d, yy';
$(function() {

  $('input.date').datepicker({
    dateFormat: dateFormat,
    maxDate: new Date()
  });

});
