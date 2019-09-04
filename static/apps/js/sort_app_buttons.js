var SortAppButtons = (function() {
    var descending = false;
    var prev_sort_by = null;

    var ISO_DATE_RE = /(\d{4})\-(\d{1,2})\-(\d{1,2})/;
    function parseISODate(dateStr) {
      var pieces = ISO_DATE_RE.exec(dateStr);
      if (pieces === null) {
        return null;
      }
      var y = parseInt(pieces[1], 10);
      var m = parseInt(pieces[2], 10);
      var d = parseInt(pieces[3], 10);
      return new Date(y, m - 1, d);
    }
    
    var sort_funcs = {
      'int': function(attr_name) {
            return function(a, b) {
                var numA = parseInt(a.attr(attr_name));
                var numB = parseInt(b.attr(attr_name));
                return numA - numB;
            };
        },
        
        'str': function(attr_name) {
            return function(a, b) {
                var nameA = a.attr(attr_name).toLowerCase();
                var nameB = b.attr(attr_name).toLowerCase();
                if (nameA > nameB)
                    return 1;
                else if (nameB > nameA)
                    return -1;
                else
                    return 0;
            }
        },

        'date': function(attr_name) {
            return function(a, b) {
                var dateA = parseISODate(a.attr(attr_name));
                var dateB = parseISODate(b.attr(attr_name));
                if (dateA > dateB)
                    return 1;
                else if (dateB > dateA)
                    return -1;
                else
                    return 0;
            }
        }
    };
    
    
    function sort_app_buttons(container, sort_func, attr_name, attr_type) {
        var currLeftCounter, currRightCounter;
        currLeftCounter = currRightCounter = -1;

        var buttons = [];
        container.find('.app_button').each(function () {
            buttons.push($(this));
        });

        zero_value_buttons = [];
        $.each(buttons, function(index, button) {
            button_value = button[0]['attributes'][attr_name].value;
            if(button_value == "0" || button_value == "") {
                delete buttons[index];
                zero_value_buttons.push(button);
            }
        });
        /*
            If all the buttons have 0 attribute value then no sorting is done.
        */
        if( buttons.includes(undefined) && buttons.length == zero_value_buttons.length || buttons.length == 0 ){
            return;
        }

        buttons = buttons.filter(function(e) { return e != undefined; })
        buttons.sort(sort_func);
        /*
          In case few buttons have 0 values for the sorting attribute then those buttons
           are sorted by name and the others are sorted by value.
        */
        if(zero_value_buttons.length != 0) {
          zero_value_buttons = zero_value_buttons.filter(function(e) {
            return e != undefined;})
            zero_value_buttons.sort(sort_funcs['str']('fullname'));
        }

        if (descending) {
            buttons = buttons.reverse();
            zero_value_buttons = zero_value_buttons.reverse();
            buttons = $.merge(buttons, zero_value_buttons);
        } else {
             buttons = $.merge(zero_value_buttons, buttons);
        }

        $.each(buttons, function(index, button) {
            if(index % 2 == 0)
            {
                currLeftCounter++;
                panel = container.find("div #left").eq(currLeftCounter).find(".wrap");
            }
            else{
                currRightCounter++;
                panel = container.find("div #right").eq(currRightCounter).find(".wrap");
            }
            panel.empty();
            panel.append(button);
        });
    }

    function sort_button_by_name(container, name) {
        return container.find('#sort_app_buttons button .title:contains(' + name + ')').parent();
    }

    var SORT_BY_COOKIE = 'igb.AppStore.AppButtons.SortBy';
    var SORT_DESCENDING_COOKIE = 'igb.AppStore.AppButtons.SortDescending';

    function setup_sort_buttons(container) {
        var buttons = container.find('#sort_app_buttons');
        buttons.find('button').click(function() {
            var sort_by = $(this).find('.title').text();
            var attr_name = $(this).attr('attr_name');
            var attr_type = $(this).attr('attr_type');
            var sort_func = sort_funcs[attr_type](attr_name);

            if (sort_by === prev_sort_by) {
                descending = !descending;
            } else {
                buttons.find('button .triangle').html('');
                prev_sort_by = sort_by;
                descending = (attr_type === 'int' || attr_type === 'date');
            }

            if (!$(this).hasClass('active')) {
                buttons.find('button').removeClass('active');
                $(this).addClass('active');
            }

            $(this).find('.triangle').html(descending ? '&#x25BC;' : '&#x25B2;');
            sort_app_buttons(container, sort_func, attr_name, attr_type);

            Cookies.set(SORT_BY_COOKIE, sort_by, {path: '/'});
            Cookies.set(SORT_DESCENDING_COOKIE, descending, {path: '/'});
        });
    }


   return {
       'init_sort_buttons': function(container) {
            setup_sort_buttons(container);
            var sort_by_hash = window.location.hash.substring(1);
            var sort_by_cookie = Cookies.get(SORT_BY_COOKIE);
            var descending_cookie = Cookies.get(SORT_DESCENDING_COOKIE);
            var sort_by;
            if (sort_by_hash === "") {
              sort_by = sort_by_cookie;
            } else {
              sort_by = sort_by_hash;
              descending_cookie = "";
            }
            var sort_button = sort_button_by_name(container, sort_by);
            if (sort_button.length === 0) {
               sort_button_by_name(container, 'name').click();
            } else {
               descending = (descending_cookie === 'false');
               prev_sort_by = sort_by;
               sort_button.click();
            }
       }
   };
})();
