function L() {
   if (window.console && window.console.log)
     console.log.apply(console, arguments);
}
function _grr(error) {
  alert(error);
  return false;
}


$(document).bind("mobileinit", function () {
  $.extend($.mobile, { ajaxFormsEnabled: false });
});

var Data = (function() {
  function html_escape(s) {
    return s.replace(/&/g,'&amp;')
            .replace(/>/g,'&gt;')
            .replace(/</g,'&lt;')
            .replace(/"/g,'&quot;');
  }

  return {
     rightnow: function() {
       $.getJSON('/mobile/rightnow.json', function(response) {
         if (response.error) return _grr(response.error);

         var p = $('#rightnow .now');
         $.each(response.now, function(i, each) {
           $('<dt>').text(each.name).appendTo(p);
           $.each(each.descriptions, function(j, description) {
             $('<dd>').text(description).appendTo(p);
           });
         });
         if (!response.now.length) {
           $('<dt>')
             .text("None at the moment")
               .addClass('none')
                 .appendTo(p);
         }

         p = $('#rightnow .upcoming');
         $.each(response.upcoming, function(i, each) {
           $('<dt>').text(each.name).appendTo(p);
           $.each(each.descriptions, function(j, description) {
             $('<dd>').text(description).appendTo(p);
           });
         });
         if (!response.upcoming.length) {
           $('<dt>')
             .text("None at the moment")
               .addClass('none')
                 .appendTo(p);
         }

       });

     },  // end rightnow

    left: function() {
       $.getJSON('/mobile/left.json', function(response) {
         if (response.error) return _grr(response.error);

         var p = $('#left p.info');
         var html;
         if (response.hours) {
           html = 'You have ';
           if (response.hours > 16) {
             html += '<strong>' + response.days + '</strong>';
           } else {
             html += '<strong>' + response.hours + ' hours</strong>';
           }
           html += ' of PTO left this year.';
         } else {
           if (response.missing) {
             html = 'To be able to work this out, enter your ';
             html += '<a href="#settings">' + response.missing.join(' and ') + '</a>.';
           } else if (response.less_than_a_year) {
             html = 'Sorry, this can not be automatically worked out if you have worked less than one year ';
             html += '(you have worked here ' + response.less_than_a_year + ' days)';
           }
         }
         p.html(html);

       });
    },  // end left

    settings: function() {
      $.getJSON('/mobile/settings.json', function(response) {
        var html = "You're currently logged in as ";
        html += '<strong>' + html_escape(response.full_name) + '</strong>.';
        $('#settings p.info').html(html);

        if (response.start_date) {
          $('#id_start_date').val(response.start_date);
        }
        if (response.country) {
          $('#id_country').val(response.country);
        }
        if (response.city) {
          $('#id_city').val(response.city);
        }
      });
    }  // end settings

  }
})();

var Notify = (function() {
  function zfill(n) {
    var s = n + '';
    if (s.length == 1)
      s = '0' + s;
    return s;
  }
  return {
     init: function() {
       // set up some defaults
       var today = new Date(),
         today_str = today.getFullYear() + '-' +
           zfill((today.getMonth() + 1)) + '-' +
           zfill(today.getDate());
       if (!$('#id_start').val()) {
         $('#id_start').val(today_str);
       }
       if (!$('#id_end').val()) {
         $('#id_end').val(today_str);
       }

       $('#notify form').submit(function() {
         var data = {
            start: $('#id_start').val(),
           end: $('#id_end').val(),
           details: $('#id_details').val()
         };
         if (!data.start) return false;
         if (!data.end) return false;
         $.post($('#notify form').attr('action'), data, function(response) {
           if (response.error) return _grr(response.error);
           if (response.form_errors) {
             $.each(response.form_errors, function(name, errors) {
               $.each(errors, function(j, error) {
                 if (name == '__all__') {
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .prependTo($('#notify form'));
                 } else {
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .insertBefore($('#notify input[name="' + name + '"]'));
                 }
               });
             });
           } else {
             $('#id_entry').val(response.entry);
             $.mobile.changePage('#hours');
           }
         });
         return false;
       });

     }
  }
})();


$(document).ready(function() {
  $('#index').bind('pageshow', function() {
    $.getJSON($('#login form').attr('action'), function(response) {
      if (!response.logged_in) {
        $.mobile.changePage('#login');
      }
    });
  });

  $('#logout').bind('pageshow', function() {
    $.getJSON($('#login form').attr('action'), function(response) {
      // in case the login page is shown to a user already logged in
      if (!response.logged_in) {
        $.mobile.changePage('#index');
      }
    });
  }).bind('pagecreate', function() {
    $('#logout form').submit(function() {
      $.post($('#logout form').attr('action'), function(response) {
        $.mobile.changePage('#login');
      });
      return false;
    });
  });

  $('#login').bind('pageshow', function() {
    $.getJSON($('#login form').attr('action'), function(response) {
      // in case the login page is shown to a user already logged in
      if (response.logged_in) {
        $.mobile.changePage('#index');
      }
    });
  }).bind('pagecreate', function() {
    $('#login form').submit(function() {
      var data = {
        username: $('#id_username').val(),
        password: $('#id_password').val()
      };
      $('#login form .error').remove();
      $.post($('#login form').attr('action'), data, function(response) {
        if (response.error) return _grr(response.error);
        if (response.form_errors) {
          $.each(response.form_errors, function(name, errors) {
            $.each(errors, function(j, error) {
               $.each(errors, function(j, error) {
                 if (name == '__all__') {
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .prependTo($('#login form'));
                 } else {
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .insertBefore($('#login input[name="' + name + '"]'));
                 }
               });
            });
          });
        } else {
          $.mobile.changePage('#index');
        }
      });
      return false;
    });
  });

  $('#rightnow').bind('pageshow', function() {
    Data.rightnow();
  });

  $('#left').bind('pageshow', function() {
    Data.left();
  });

  $('#settings')
    .bind('pageshow', function() {
    Data.settings();
  }).bind('pagecreate', function() {
    $('#settings form').submit(function() {
      var data = {
        start_date: $('#id_start_date').val(),
        country: $('#id_country').val(),
        city: $('#id_city').val()
      };
      $('#settings form .error').remove();
      $.post($('#settings form').attr('action'), data, function(response) {
        if (response.error) return _grr(response.error);
        if (response.form_errors) {
          $.each(response.form_errors, function(name, errors) {
            $.each(errors, function(j, error) {
              $('<span>')
                .text(error)
                  .addClass('error')
                    .insertBefore($('#settings input[name="' + name + '"]'));
            });
          });
        } else {
          alert('Saved successfully!');
          Data.settings();
        }
      });
      return false;
    });

  });

  $('#notify').bind('pagecreate', function() {
    Notify.init();
  });

  var sample_radio_field;
  $('#hours')
    .bind('pagecreate', function() {
      sample_radio_field = $('#hours .sample').clone(true);
      $('#hours form').submit(function() {
        var data = {
           entry: $('#id_entry').val()
        };
        $('input[type="radio"]:checked:visible').each(function(i, element) {
          data[$(element).attr('name')] = $(element).val();
        });
        $.post($('#hours form').attr('action'), data, function(response) {
           if (response.error) return _grr(response.error);
           if (response.form_errors) {
             $.each(response.form_errors, function(name, errors) {
               $.each(errors, function(j, error) {
                 if (name == '__all__') {
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .prependTo($('#hours form'));
                 } else {
                   // XXX: not sure this works
                   $('<span>')
                     .text(error)
                       .addClass('error')
                         .insertBefore($('#hours input[name="' + name + '"]'));
                 }
               });
             });
           } else {
             alert('Saved successfully!');
             Data.settings();
             $.mobile.changePage('#index');
           }
        });
        return false;
      });
    })
      .bind('pageshow', function() {
        var entry_id = $('#id_entry').val();
        if (!entry_id) {
          $.mobile.changePage('#notify');
          return;
        }
        $.getJSON('/mobile/hours.json', {entry: entry_id}, function(response) {
          if (response.error) return _grr(response.error);
          var field;
          $.each(response, function(i, day) {
            field = sample_radio_field.clone(true);
            $('legend', field).text(day.full_day + ':');
            $('input[name="duration"]', field).attr('name', day.key);
            $.each(['full_day', 'half_day', 'zero', 'bday'], function(j, bit) {
              if (parseInt($('#duration-' + bit, field).val()) == day.value) {
                $('#duration-' + bit, field).attr('checked', 'checked');
              } else {
                $('#duration-' + bit, field).removeAttr('checked');
              }
              $('#duration-' + bit, field)
                .attr('id', 'duration-' + bit + '_' + (i + 1));
              $('label[for="duration-' + bit + '"]', field)
                .attr('for', 'duration-' + bit + '_' + (i + 1));
            });

            field.show();
            $('input', field).parent().nextAll('br').remove();
            field.removeClass('sample');
            $('#hours form').append(field);
            field.controlgroup('refresh', true);
            $('fieldset', field).controlgroup('refresh', true);
            $('input', field).checkboxradio().checkboxradio("refresh");
          });
        });

        //$('#hours form').append($('#hours fieldset.save').clone(true));
      });

});
