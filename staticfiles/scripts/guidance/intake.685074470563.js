$(document).ready(function(){

    $(document).on('click','#proceedBtn' ,function(event){
        event.preventDefault();
        $('#consent_container').removeClass('active');
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
        
        // Get the entered ID number
        var idNumber = $('#studentIDBox').val();

        // Send AJAX request to fetch student info
        $.ajax({
            url: '/search_student_info_for_intake/',
            method: 'POST',
            data: {'id_number': idNumber},
            beforeSend: function(xhr, settings) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function(response) {
                $('#info_table').removeClass('hidden')
                $('#individualProfileForm').removeClass('hidden')

                $('#student_id_val').val(response.student_id)
                $('#info_table tr').empty();
                
                // Append new row with retrieved data
                $('#info_table').append(
                    '<tr id="info_table_head">'+
                    '<th>PROFILE NO</th>'+
                    '<th>STUDENT ID'+
                    '<th>NAME</th>'+
                    '<th>DATE FILLED</th>'+
                    '</tr>'
                );
                response.response.forEach(function(item, index){
                    $('#info_table').append(
                        '<tr>' +
                        '<td>' + item.profile_number + '</td>' +
                        '<td>' + item.studentid + '</td>' +
                        '<td>' + item.name + '</td>' +
                        '<td>' + item.datefilled + '</td>' +
                        '<td><div class="deleteBox"><button class="selectItem OrangeButton">Select</button></div></td>'+
                        
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
    $("#info_table").on("click", ".selectItem", function(event){
        event.preventDefault();
        
        // Get profile number and the entire row
        let profileNo = $(this).closest('tr').find('td:first').text();
        let selectedRow = $(this).closest('tr').clone();
        
        // Remove the button from the selected row
        selectedRow.find('.selectItem').closest('td').remove();
        
        // Remove the button from the original row
        $(this).closest('td').empty();
    
        $('#info_table tr').empty();
                
        // Append new row with retrieved data
        $('#info_table').append(
            '<tr id="info_table_head">'+
            '<th>PROFILE NO</th>'+
            '<th>STUDENT ID'+
            '<th>NAME</th>'+
            '<th>DATE FILLED</th>'+
            '</tr>'
        );
        $('#info_table').append(selectedRow);
    
        // Update form fields or do whatever you need with the selected data
        $("#individualId").val(profileNo);
        $('#intakeForm').removeClass('hidden');
    });
    


    $("#individual_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="individualrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="individualActivity[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="individualAccomplished[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="individualRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#individual_inventory").append(newRow);
    });
    $("#individual_inventory").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#individual_inventory tr.individualrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });

    $("#appraisal_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="appraisalrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="appraisalTest[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="appraisalDateTaken[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="appraisalDateInterpreted[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="appraisalRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#appraisal").append(newRow);
    });
    $("#appraisal").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#appraisal tr.appraisalrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });

    $("#counseling_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="counselingrowTemplate">
                        <td>
                            <div class="inoutschool field_container side-way">    
                                <div id="counseling_type" class="side-way">
                                    <label for="id_couseling_type_0"><input type="radio" name="couseling_type[]" value="False" class="side-way" required="" id="couseling_type_0">
                                        Walk-in
                                    </label>
                                </div>
                                <div id="counseling_type" class="side-way">
                                    <label for="id_couseling_type_1"><input type="radio" name="couseling_type[]" value="False" class="side-way" required="" id="couseling_type_1">
                                        Referral
                                    </label>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="counselingDate[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="counselingConcern[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="counselingRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#counseling").append(newRow);
    });
    $("#counseling").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#counseling tr.counselingrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
            $('.inoutschool input[type="radio"]').prop('checked', false);
        }
    });

    $("#follow_up_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="followrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="followActivity[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="followDate[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="followRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#follow").append(newRow);
    });
    $("#follow").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#follow tr.followrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });

    $("#information_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="sibllingsrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="informationActivity[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="informationDate[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="informationRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#information").append(newRow);
    });
    $("#information").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#information tr.sibllingsrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });

    $("#consultation_button").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="consultationrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="counseltationActivity[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="date" name="counseltationDate[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="counseltationRemarks[]">
                            </div>
                        </td>
                        <td>
                            <div class="deleteBox">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`
        $("#consultation").append(newRow);
    });
    $("#consultation").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#consultation tr.consultationrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });
});