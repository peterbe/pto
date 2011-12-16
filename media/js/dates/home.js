$(function() {
  $('#calendar').fullCalendar({
    editable: false,
    //events: "/calendar/events/",
    events: function(start, end, callback) {
      var ops = {start: start.getTime(), end: end.getTime()};
      $.getJSON('/calendar/events/', ops, function(response) {
        callback(response.events);
        var c = 0;
        $.each(response.colors, function() { c++; });
        L(response.colors);
        if (c > 0) {
          var container = $('#calendar-legend');
          if (container.size()) {
            $('span', container).remove();
          } else {
            container = $('<div id="calendar-legend">');
            $('<strong>')
              .text('Legend:')
                .appendTo(container);
          }
          $.each(response.colors, function(i, each) {
            $('<span>')
              .text(each.name)
                .css('background-color', each.color)
                  .css('color', '#fff')
                    .appendTo(container);
          });
          $('<a href="/following/">')
            .addClass('following-link')
            .html('Manage people you follow &rarr;')
              .appendTo(container);
          container.insertAfter('#calendar table.fc-header');
        } else if ($('#calendar-legend span').size()) {
          $('#calendar-legend').remove();
        }
      });
    },
    firstDay: CALENDAR_FIRST_DAY,
    selectable: true,
    selectHelper: true,
    select: function(start, end, allDay) {
      url = '/notify/?start=' + start.getTime() + '&end=' + end.getTime();
      location.href = url;
      calendar.fullCalendar('unselect');
    }
  });

  $('<a href="#rightnow"></a>')
    .html($('#rightnow h2').text() + ' &darr;')
      .addClass('anchor')
        .prependTo($('#content'));

  $('<a href="#pto_taken"></a>')
    .html($('#pto_taken h2').text() + ' &darr;')
      .addClass('anchor')
        .prependTo($('#content'));

});
