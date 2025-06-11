$(document).ready(function(){
    // Get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    // Intercept form submission
    $('#searchButton').on('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        
        // Get the entered ID number
        var idNumber = $('#studentIDBox').val();

        // Send AJAX request to fetch student info
        $.ajax({
            url: '/search_student_info/',
            method: 'POST',
            data: {'id_number': idNumber},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
                $('#info_table').removeClass('hidden')
                $('#requestForm').removeClass('hidden')

                $('#student_id_val').val(response.student_id)
                $('#info_table tr').empty();
                
                // Append new row with retrieved data
                $('#info_table').append(
                    '<tr id="info_table_head">'+
                    '<th>NAME</th>'+
                    '<th>PROGRAM/YEAR AND SECTION</th>'+
                    '<th>CONTACT NO.</th>'+
                    '</tr>'
                );
                $('#info_table').append(
                    '<tr>' +
                    '<td>' + response.name + '</td>' +
                    '<td>' + `${response.program} ${response.year}` + '</td>' +
                    '<td>' + '0' + response.contact_number + '</td>' +
                    '</tr>'
                );
            },
            error: function(error) {
                $('#requestForm').addClass('hidden')
                $('#info_table').removeClass('hidden')
                $('#info_table').empty()
                $('#info_table').append(
                    '<tr>' +
                    '<td colspan="4">Student ID not found.</td>' +
                    '</tr>'
                );
            }
        });
    });
    $('#id_scheduled_date').on('change', function() {
        if ($(this).val()) {
            $('#id_scheduled_time').prop('disabled', false);
            let selectedDate = $(this).val();
            let csrftoken = getCookie('csrftoken');
            // Make a POST request
            $.post({
                url: '/check_date_time_validity/',
                data: { selected_date: selectedDate },
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                headers: {'X-CSRFToken': csrftoken}, 
                success: function(response) {
                    let disabledTimes = response.counseling_schedules;
                    $('#id_scheduled_time option').prop('disabled', false); // Enable all options initially
                    console.log(response)
                    $.each(disabledTimes, function(index, value) {
                        if (value.status !== 'declined') {
                            $('#id_scheduled_time option[value="' + value.scheduled_time + '"]').prop('disabled', true).text(function (index, text) {
                                return text + ' (occupied)'; // Append "(occupied)" to disabled options
                            });
                        }
                    });
                },
                error: function(xhr, status, error) {
                    // Handle error if needed
                }
            });
        } else {
            $('#id_scheduled_time').prop('disabled', true);
            $('#id_scheduled_time').val(''); 
        }
    });
    
});