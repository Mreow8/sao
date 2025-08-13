$(document).ready(function(){

    $('#consent_container').addClass('active');
    console.log('test');

    $("#agreeCheck").change((event)=>{
        if($('#agreeCheck').is(':checked')){
            $('#proceedBtn').prop('disabled', false);
            $('#proceedBtn').removeClass('disabled');
        }
        else{
            $('#proceedBtn').prop('disabled', true);
            $('#proceedBtn').addClass('disabled');
        }
    });

    $(document).on('click','#proceedBtn' ,function(event){
        event.preventDefault();
        $('#consent_container').removeClass('active');
    });

    $('input[name="currentlyEmployed"]').change(function(){
        $('#explainationEmployed').removeClass('hidden')
        let selectedValue = $('input[name="currentlyEmployed"]:checked').val();
        if (selectedValue === "True") {
            $('#employedYesNo').text('-Please provide the name and address of the company:');
        } else if (selectedValue === "False") {
            $('#employedYesNo').text('-Please provide the name and address of the company you want:');
        }
    });
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

    $('#searchButton').on('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        console.log('hs')
        // Get the entered ID number
        let idNumber = $('#studentIDBox').val();

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
                $('#questionForm').removeClass('hidden')

                $('#studentID').val(response.student_id)
                $('#info_table tr').empty();
                
                // Append new row with retrieved data
                $('#info_table').append(
                    '<tr id="info_table_head">'+
                    '<th>NAME</th>'+
                    '<th>CONTACT NO.</th>'+
                    '</tr>'
                );
                $('#info_table').append(
                    '<tr>' +
                    '<td>' + response.name + '</td>' +
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
                    '<td colspan="2">Student ID not found.</td>' +
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
                url: '/check_date_time_validity_for_exit/',
                data: { selected_date: selectedDate },
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                },
                headers: {'X-CSRFToken': csrftoken}, 
                success: function(response) {
                    let disabledTimes = response.counseling_schedules;
                    $('#id_scheduled_time option').prop('disabled', false); // Enable all options initially
                    $('#id_scheduled_time option').prop('disabled', false).text(function () {
                        return $(this).text().replace(' (occupied)', ''); // Remove existing "(occupied)" text
                    }); // Enable all options initially
                    $.each(disabledTimes, function(index, value) {
                        if (value.status != "Declined") {
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
    function validateInputs() {
        let values = [];
        let hasDuplicates = false;

        // Select only the number inputs within the specific table
        $('table.table input[type="number"]').each(function() {
            let value = $(this).val();
            let name = $(this).attr('name');

            // Clear previous errors
            $(this).removeClass('error');
            $(this).next('.error-message').remove();
            if($(this).attr('name')==='what_is_your_intended_major'){
                let intendedMajor = $("input[name='what_is_your_intended_major']").val()
                if(intendedMajor ==""){
                    $('#id_intendedMajor').addClass('hidden')
                    $('#id_intendedMajor').removeAttr('required', 'required');
                }
                else{
                    $('#id_intendedMajor').removeClass('hidden')
                    $('#id_intendedMajor').attr('required', 'required');
                }
            }
            else if($(this).attr('name')==='major_event'){
                let major_event = $("input[name='major_event']").val()
                if(major_event==""){
                    $('#id_majorEvent').addClass('hidden')
                    $('#id_majorEvent').removeAttr('required', 'required');
                }
                else{
                    $('#id_majorEvent').removeClass('hidden')
                    $('#id_majorEvent').attr('required', 'required');
                }
            }
            if (value === "") {
                value = "empty";
            } else if (parseInt(value) < 1) {
                // Check if value is below 1
                $(this).addClass('error');
                $(this).after('<span class="error-message" style="color:red;">Value must be 1 or higher.</span>');
            }

            if (values.includes(value)) {
                hasDuplicates = true;
            }
            values.push(value);
        });

        if (hasDuplicates) {
            $('table.table input[type="number"]').each(function() {
                let value = $(this).val();
                if (value !== "" && values.filter(v => v === value).length > 1) {
                    $(this).addClass('error');
                    $(this).after('<span class="error-message" style="color:red;">Duplicate value found.</span>');
                }
            });
        }
    }

    // Attach the event handler to the number inputs within the specific table
    $('table.table input[type="number"]').on('change', function() {
        validateInputs();
    });
    $('#what_is_your_intended_major').on('change', function(){
        let what_is_your_intended_major = $('#what_is_your_intended_major').val()
        if(what_is_your_intended_major != ''){
            $('id_intendedMajor').removeClass('hidden');
        }
        else{
            $('id_intendedMajor').addClass('hidden');
            
        }
    });
});