$(function() {
    var calendar;
    var Calendar = FullCalendar.Calendar;
    var events = [];

    if (!!scheds) {
        Object.keys(scheds).map(k => {
            var row = scheds[k];
            events.push({ id: row.sched_Id, title: row.title, start: row.start_datetime, end: row.end_datetime });
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
            var event = scheds.find(event => event.sched_Id == id);
            if (event) {
                _details.find('#title').text(event.title);
                _details.find('#description').text(event.description);
                _details.find('#start').text(event.start_datetime);
                _details.find('#end').text(event.end_datetime);
                _details.find('#edit,#delete').attr('data-id', id);
                _details.modal('show');
            } else {
                alert("Event is undefined");
            }
        },
        editable: false
    });

    calendar.render();

    // Form reset listener
    $('#schedule-form').on('reset', function() {
        $(this).find('input:hidden').val('');
        $(this).find('input:visible').first().focus();
    });

    // Edit Button
    $('#edit').click(function() {
        var id = $(this).attr('data-id');
        var event = scheds.find(event => event.sched_Id == id);
        if (event) {
            var _form = $('#schedule-form');
            _form.find('[name="id"]').val(id);
            _form.find('[name="title"]').val(event.title);
            _form.find('[name="description"]').val(event.description);
            _form.find('[name="start_datetime"]').val(event.start_datetime.replace(" ", "T"));
            _form.find('[name="end_datetime"]').val(event.end_datetime.replace(" ", "T"));
            $('#event-details-modal').modal('hide');
            _form.find('[name="title"]').focus();
        } else {
            alert("Event is undefined");
        }
    });

    // Delete Button
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
                    location.reload(); // Reload the page to reflect the changes
                },
                error: function(response) {
                    alert('An error occurred while deleting the event.');
                }
            });
        }
    });
});
