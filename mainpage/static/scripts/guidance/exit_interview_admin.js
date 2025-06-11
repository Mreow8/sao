$(document).ready(function(){
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

    // Intercept form submission
    $('#searchButton').on('click', function(event) {
        event.preventDefault(); // Prevent default form submission behavior
        
        // Get the entered ID number
        var idNumber = $('#studentIDBox').val();

        // Send AJAX request to fetch student info
        $.ajax({
            url: '/search_exit_interview_request/',
            method: 'POST',
            data: {'id_number': idNumber},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
                $('#info_table tr').empty();
            
                // Append table headers
                $('#info_table').append(
                    '<tr id="info_table_head">' +
                    '<th>DATE RECEIVED</th>' +
                    '<th>STUDENT ID</th>' +
                    '<th>NAME</th>' +
                    '<th colspan="3">STATUS</th>' +
                    '</tr>'
                );
            
                // Append data for each student
                response.forEach(function(student) {
                    let show_form = '<button class="showformButton hidden">SHOW FORM</button>';
                    let status_val = '';
                    let button_element = '';
            
                    show_form = '<button class="showformButton hidden">SHOW FORM</button>'
                    if(student.status == 'Accepted'){
                        show_form = '<button class="showformButton">SHOW FORM</button>'
                        status_val = '<span class="accepted">Accepted</span>'
                    }
                    else if(student.status == 'Declined')
                        status_val = '<span class="declined">Declined</span>'
                    else if(student.status == 'Pending')
                        status_val = '<span class="pending">Pending</span>'
                    else{
                        status_val = '<span class="expired">Expired</span>'
                    }
                    if(student.status != 'Pending'){
                        button_element =  '<button class="delete">DELETE</button>'
                    }
                    else{
                        button_element = `<button class="accept">ACCEPT</button>
                        <button class="decline">DECLINE</button>
                        <button class="delete">DELETE</button>`
                    }
            
                    $('#info_table').append(
                        '<tr>' +
                        `<input type="hidden" name="exitinterviewId" class="exitinterviewId"
                        value="${student.exit_interview_id}">`+
                        '<td>' + student.date_received + '</td>' +
                        '<td>' + student.student_id + '</td>' +
                        '<td>' + student.name + '</td>' +
                        '<td>' + status_val + '</td>' +
                        '<td>' + '<div class="horizontal">' + button_element + '</div>' + '</td>' +
                        '<td>' + show_form + '</td>' +
                        '</tr>'
                    );
                });
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
    $(document).on('click','.accept' ,function() {
        let exitinterviewId = $(this).closest('tr').find('.exitinterviewId').val();
        let statusSpan = $(this).closest('tr').find('.pending');
        let accept = $(this).closest('tr').find('.accept');
        let showformButton = $(this).closest('tr').find('.showformButton');
        let decline = $(this).closest('tr').find('.decline');
        // Perform further actions here, such as sending the ID to the server
        $.post({
            url: '/update_exit_interview_status/',
            data: { 'exitinterviewId': exitinterviewId, 'type': 'accept' },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            headers: {'X-CSRFToken': csrftoken}, 
            success: function(response) {
                showformButton.removeClass('hidden')
                statusSpan.replaceWith(' <span class="accepted">Accepted</span>')
                accept.remove()
                decline.remove()
            },
            error: function(xhr, status, error) {
                // Handle error if needed
            }
        });
    });
    $(document).on('click', '.showformButton', function() {
        console.log('haha');
        let requestID = $(this).closest('tr').find('.exitinterviewId').val();
        $('.showform_container').addClass('active');
        $.post({
            url: '/get_exit_interview_request/',
            data: { 'requestID': requestID},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            headers: {'X-CSRFToken': csrftoken}, 
            success: function(response) {
                console.log(response)
                $('#name').text(response.name)
                $('#date').text(response.date)
                $('#date-enrolled').text(response.dateenrolled)
                $('#contact').text(response.contact)
                $('#question1').text(response.reasonforleaving)
                if(response.satisfiedWithAcadamic){
                    $('#question2_yes').text('✔')
                }
                else{
                    $('#question2_no').text('✔')
                }
                $('#question2').text(response.feedbackWithAcademic)
                if(response.satisfiedWithSocial){
                    $('#question3_yes').text('✔')
                }
                else{
                    $('#question3_no').text('✔')
                }
                $('#question3').text(response.feedbackWithSocial)
                if(response.satisfiedWithServices){
                    $('#question4_yes').text('✔')
                }
                else{
                    $('#question4_no').text('✔')
                }
                $('#question4').text(response.feedbackWithServices)
                $('#table_data1').text(response.contributedToDecision[0])
                $('#table_data2').text(response.contributedToDecision[1])
                $('#table_data3').text(response.contributedToDecision[2])
                $('#table_data5').text(response.contributedToDecision[3])
                $('#table_data6').text(response.contributedToDecision[4])
                $('#table_data7').text(response.contributedToDecision[5])
                $('#table_data8').text(response.contributedToDecision[6])
                $('#table_data9').text(response.contributedToDecision[7])
                $('#table_data10').text(response.contributedToDecision[8])
                $('#table_data11').text(response.contributedToDecision[9])
                $('#table_data12').text(response.contributedToDecision[10])
                $('#table_data13').text(response.contributedToDecision[11])
                $('#table_data14').text(response.contributedToDecision[12])
                $('#table_data15').text(response.contributedToDecision[13])
                $('#table_data16').text(response.contributedToDecision[14])
                
                $('#intendedMajor').text(response.intendedMajor)
                $('#question5').text(response.firstConsider)
                $('#question6').text(response.whatCondition)
                if(response.recommed){
                    recommend = 'Yes'
                }
                else{
                    recommed = 'No'
                }
                $('#question7').text(recommed)

                if(response.howSatisfied == 'Very Satisfied'){
                    $('#question8_vs').text('[✔]Very satisfied')
                }
                else if(response.howSatisfied == 'Somewhat Satisfied'){
                    $('#question8_ss').text('[✔]Somewhat satisfied')
                }
                else if(response.howSatisfied == 'Satisfied'){
                    $('#question8_s').text('[✔]Satisfied')
                }
                else if(response.howSatisfied == 'Somewhat Dissatisfied'){
                    $('#question8_sd').text('[✔]Somewhat Dissatisfied')
                }
                else{
                    $('#question8_vd').text('[✔]Very Dissatisfied')
                }
                $('#question9').text(response.planTOReturn)
                
                if(response.accademicExperienceSatisfied){
                    $('#question10_yes').text('✔')
                }
                else{
                    $('#question10_no').text('✔')
                }
                
                $('#question11').text(response.knowAboutYourTime)
                
                if(response.currentlyEmployed){
                    $('#question12_yes').text('✔')
                    $('#question12_ifyes').text(response.explainationEmployed)
                }
                else{
                    $('#question12_no').text('✔')
                    $('#question12_ifno').text(response.explainationEmployed)
                }
                
                $('.showform_container').addClass('active');
            },
            error: function(xhr, status, error) {
                // Handle error if needed
            }
        });
    });
    
    $(document).on('click','.saveButton' ,function(){
        const elements = document.getElementById("paper");
        const student_name = $('#student-name').text()
        const options = {
            margin: [0, 0, 0, 0],
            filename: `${student_name}_certificate.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: [216, 279], orientation: 'portrait' }
        };

        html2pdf()
            .from(elements)
            .set(options)
            .save();
    });
    $('.closeform').click(function(){
        $('.showform_container').removeClass('active');
    });
    // Event listener for decline button
    $(document).on('click', '.decline' ,function() {
        let exitinterviewId = $(this).closest('tr').find('.exitinterviewId').val();
        let statusSpan = $(this).closest('tr').find('.pending');
        let accept = $(this).closest('tr').find('.accept');
        let decline = $(this).closest('tr').find('.decline');
        // Perform further actions here, such as sending the ID to the server
        $.post({
            url: '/update_exit_interview_status/',
            data: { 'exitinterviewId': exitinterviewId, 'type': 'decline' },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            headers: {'X-CSRFToken': csrftoken}, 
            success: function(response) {
                statusSpan.replaceWith(' <span class="declined">Declined</span>')
                accept.remove()
                decline.remove()
            },
            error: function(xhr, status, error) {
                // Handle error if needed
            }
        });
    });

    // Event listener for delete button
    $(document).on('click','.delete' ,function() {
        let exitinterviewId = $(this).closest('tr').find('.exitinterviewId').val();
        let parentRow = $(this).closest('tr')
        $.post({
            url: '/delete_exit_interview_status/',
            data: { 'exitinterviewId': exitinterviewId },
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            headers: {'X-CSRFToken': csrftoken}, 
            success: function(response) {
                parentRow.remove()
            },
            error: function(xhr, status, error) {
                // Handle error if needed
            }
        });
    });
});