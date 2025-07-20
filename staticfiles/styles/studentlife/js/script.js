$(function() {
    var calendar;
    var Calendar = FullCalendar.Calendar;
    var events = [];

    if (!!scheds) {
        Object.keys(scheds).map(k => {
            var row = scheds[k];
            events.push({ id: row.id, title: row.title, start: row.start_datetime, end: row.end_datetime });
        });
    }

    var date = new Date();
    var d = date.getDate(),
        m = date.getMonth(),
        y = date.getFullYear();

    calendar = new Calendar(document.getElementById('calendar'), {
        headerToolbar: {
            left: 'title',
            right: 'today dayGridMonth,dayGridWeek,list prev,next',
            center: '',
        },
        selectable: true,
        themeSystem: 'bootstrap',
        events: events,
        eventClick: function(info) {
            var _details = $('#event-details-modal');
            var id = info.event.id;
            if (!!scheds[id]) {
                _details.find('#title').text(scheds[id].title);
                _details.find('#description').text(scheds[id].description);
                _details.find('#start').text(scheds[id].sdate);
                _details.find('#end').text(scheds[id].edate);
                _details.find('#edit,#delete').attr('data-id', id);
                _details.modal('show');
            } else {
                alert("Event is undefined");
            }
        },
         //editable:true(for admin drag and drop events(script.js))
        editable: true,
        eventDrop: function(info) {
            var event = info.event;
            var scheduleId = event.id;
            var newStart = event.start;
            var newEnd = event.end;
            // Update start and end date in the database using AJAX
            updateScheduleDateTime(scheduleId, newStart, newEnd);
        },
        // Handle event resize
        eventResize: function(info) {
            var event = info.event;
            var scheduleId = event.id;
            var newStart = event.start;
            var newEnd = event.end;
             // Update start and end date in the database using AJAX
            updateScheduleDateTime(scheduleId, newStart, newEnd);
        }
    });

    calendar.render();
     // Function to update schedule start and end datetime in the database
    function updateScheduleDateTime(scheduleId, newStart, newEnd) {
        var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        // AJAX request to update schedule datetime
        $.ajax({
            url: '/update-schedule/' + scheduleId + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': csrfToken,
                'start_datetime': newStart.toISOString(),// Convert to ISO string format
                'end_datetime': newEnd.toISOString()// Convert to ISO string format
            },
            success: function(response) {
                console.log('Schedule updated successfully.');
            },
            error: function(response) {
                alert('An error occurred while updating the schedule.');
            }
        });
    }

    $('#schedule-form').on('reset', function() {
        $(this).find('input:hidden').val('');
        $(this).find('input:visible').first().focus();
    });

    $('#edit').click(function() {
        var id = $(this).attr('data-id');
        if (!!scheds[id]) {
            var _form = $('#schedule-form');
            _form.find('[name="id"]').val(id);
            _form.find('[name="title"]').val(scheds[id].title);
            _form.find('[name="description"]').val(scheds[id].description);
            _form.find('[name="start_datetime"]').val(String(scheds[id].start_datetime).replace(" ", "T"));
            _form.find('[name="end_datetime"]').val(String(scheds[id].end_datetime).replace(" ", "T"));
            $('#event-details-modal').modal('hide');
            _form.find('[name="title"]').focus();
        } else {
            alert("Event is undefined");
        }
    });

    $(document).ready(function() {
        $('#delete').on('click', function() {
            var scheduleId = $(this).data('id');
            var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

            if (confirm('Are you sure you want to delete this schedule?')) {
                $.ajax({
                    url: '/delete-schedule/' + scheduleId + '/',
                    type: 'POST',
                    data: {
                        'csrfmiddlewaretoken': csrfToken
                    },
                    success: function(response) {
                        alert('Event has been deleted successfully.');
                        location.reload();
                    },
                    error: function(response) {
                        alert('An error occurred while deleting the event.');
                    }
                });
            }
        });
    });
});
