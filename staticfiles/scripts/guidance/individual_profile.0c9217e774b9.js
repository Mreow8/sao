$(document).ready(function(){
    $('#consent_container').addClass('active');

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
            url: '/search_student_info_for_individual_profile/',
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
                    '<th>NAME</th>'+
                    '<th>COURSE</th>'+
                    '<th>SEX</th>'+
                    '</tr>'
                );
                let sex ="";
                if(response.sex === "M"){
                    sex = "Male";
                }
                else{
                    sex = "Female";
                }
                $('#info_table').append(
                    '<tr>' +
                    '<td>' + response.name + '</td>' +
                    '<td>' + `${response.program}` + '</td>' +
                    '<td>' + sex + '</td>' +
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



    $("#addanother").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="sibllingsrowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="name[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="number" name="age[]">
                            </div>      
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="placework[]">
                            </div>
                        </td>
                        <td>
                            <button class="deleteRow OrangeButton">Delete</button>
                        </td>
                    </tr>`
        $("#siblings").append(newRow);
    });
    $("#siblings").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#siblings tr.sibllingsrowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
        }
    });
    $("#organizationTable").on("click", ".deleteRow", function(event) {
        event.preventDefault();
        var rowCount = $("#organizationTable tr.orgRowTemplate").length;
        if (rowCount > 1) {
            $(this).closest("tr").remove();
        } else {
            $(this).closest("tr").find("input").val("");
            $('.inoutschool input[type="radio"]').prop('checked', false);
        }
    });
    

    $("#addOrganization").on("click", function(event){
        event.preventDefault();
        let newRow = `<tr class="orgRowTemplate">
                        <td>
                            <div class="field_container">
                                <input type="text" name="name_of_organization[]" required>
                            </div>
                        </td>
                        <td>
                            <div class="inoutschool field_container">    
                                <div id="inoutSchool" class="side-way"><div>
                                    <label for="id_elementaryType_0"><input type="radio" name="inoutSchool[]" value="True" class="side-way" required="" id="inoutSchool_0">
                                        Yes
                                    </label>
                                
                                </div>
                                <div id="inoutSchool" class="side-way">
                                    <label for="id_elementaryType_1"><input type="radio" name="inoutSchool[]" value="False" class="side-way" required="" id="inoutSchool_1">
                                        No
                                    </label>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="position[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <input type="text" name="inclusiveyears[]">
                            </div>
                        </td>
                        <td>
                            <div class="field_container">
                                <button class="deleteRow OrangeButton">Delete</button>
                            </div>
                        </td>
                    </tr>`;
        $("#organizationTable").append(newRow);
    });
    $("#id_sourceOfIncome").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "familyownedbusiness" || selectedValue == "relatives"){
            $("#source_income_container").removeClass("hidden")
            $('#id_sourceOfIncomeSpecify').attr('required','required')
        }
        else{
            $("#source_income_container").addClass("hidden")
            $('#id_sourceOfIncomeSpecify').removeAttr('required','required')
        }
    })
    $("#id_studentType").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "newStudent"){
            $("#hs_curriculum").removeClass("hidden")
            $('#id_curriculumtype').attr('required','required')
        }
        else{
            $("#hs_curriculum").addClass("hidden")
            $('#id_curriculumtype').removeAttr('required','required')
        }
    })
    $("#id_curriculumtype").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "seniorhigh"){      
            $("#hs_track").removeClass("hidden")
            $("#id_track").attr('required','required')
        }
        else{
            $("#trackbox").addClass("hidden")
            $("#id_track").removeAttr('required','required')
        }
    })
    $("#id_livingWith").change(function(event){
        let selectedValue = $(this).val();

        if(selectedValue=="relative" || selectedValue == "others"){
            $("#living_specify").removeClass("hidden")
            $("#id_livingSpecify").attr('required','required')
        }
        else{
            $("#living_specify").addClass("hidden")
            $("#id_livingSpecify").removeAttr('required','required')
        }
    })
    
    $("#id_placeOfLiving").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "others"){
            $("#place_of_living_other").removeClass("hidden")
            $("#id_placeOfLivingOthers").attr('required','required')
        }
        else{
            $("#place_of_living_other").addClass("hidden")
            $("#id_placeOfLivingOthers").removeAttr('required','required')
        }
    })
    
    $("#id_fatherOccupation").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "others"){
            $("#father_occupation_other").removeClass("hidden")
            $("#id_fatherOtherOccupation").attr('required','required')
        }
        else{
            $("#father_occupation_other").addClass("hidden")
            $("#id_fatherOtherOccupation").removeAttr('required','required')
        }
    })
    $("#id_motherOccupation").change(function(event){
        let selectedValue = $(this).val();
    
        console.log(selectedValue)
        if(selectedValue == "others"){
            $("#mother_occupation_other").removeClass("hidden")
            $("#id_motherOtherOccupation").attr('required','required')
        }
        else{
            $("#mother_occupation_other").addClass("hidden")
            $("#id_motherOtherOccupation").removeAttr('required','required')
        }
    })
    $("#id_schoolLeaver_0").change(function(event){
        if($(this).val()){
            $("#reasonOfLeaving").removeClass("hidden")
        }
    });
    $("#id_schoolLeaver_1").change(function(event){
        if($(this).val()){
            $("#reasonOfLeaving").addClass("hidden")
        }
    });
    
    $("#id_finaciallySupporting").change(function(event){
        let selectedValue = $(this).val();
        
        console.log(selectedValue)
        if(selectedValue == "scholarship"){
            $("#scholarship").removeClass("hidden")
            $("#id_typeOfScholarship").attr("required","required")
            $("#id_specifyScholarship").attr("required","required")
        }
        else{
            $("#scholarship").addClass("hidden")
            $("#id_typeOfScholarship").removeAttr("required","required")
            $("#id_specifyScholarship").removeAttr("required","required")
        }
    });
    $("#id_typeOfScholarship").change(function(event){
        let selectedValue = $(this).val();
        
        console.log(selectedValue)
        if(selectedValue == "organizations"){
            $("#specifyScholarShip").removeClass("hidden")
        }
        else{
            $("#specifyScholarShip").addClass("hidden")
        }
    });
    $("#id_doYouPlanToWork_0").change(function(event){
        if($(this).val()){
            $("#specifyDontWork").addClass("hidden")
            $('#id_specifyIfNo').removeAttr('required', 'required');
        }
    });
    $("#id_doYouPlanToWork_1").change(function(event){
        if($(this).val()){
            $("#specifyDontWork").removeClass("hidden")
            $('#id_specifyIfNo').attr('required', 'required');
        }
    });
    $("#id_decisionForTheCourse").change(function(event){
        let selectedValue = $(this).val();
        if(selectedValue != "self"){
            $("#preferedCourse").removeClass('hidden')
        }
        else{
            $("#preferedCourse").addClass('hidden')
        }
    });
    

    function validateFields(container) {
        var isValid = true;
        var radioGroups = {};
    
        container.find('input, select, textarea').each(function() {
            var $this = $(this);
            if ($this.prop('required')) {
                if (!$this.val()) {
                    isValid = false;
                } else if ($this.attr('type') === 'email') {
                    var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
                    if (!emailPattern.test($this.val())) {
                        isValid = false;
                    }
                } else if ($this.attr('type') === 'radio') {
                    var name = $this.attr('name');
                    if (!(name in radioGroups)) {
                        radioGroups[name] = false;
                    }
                    if ($this.prop('checked')) {
                        radioGroups[name] = true;
                    }
                }
            }
        });
    
        Object.values(radioGroups).forEach(function(value) {
            if (!value) {
                isValid = false;
            }
        });
    
        return isValid;
    }
    
    $('.nextpage').on('click', function() {
        let current = $('.current-page-activated');
        let next = current.next('.fill_out_container');
        let curret_page_counter = $('.current-fill-out');
        let next_page_counter = curret_page_counter.next('.page_viewer');


        if(validateFields(current)){
            current.removeClass('current-page-activated').addClass('current-page-deactivated');
            curret_page_counter.removeClass('current-fill-out');
            next_page_counter.addClass('current-fill-out');
            setTimeout(function() {
                current.addClass('hidden');
                next.removeClass('hidden').addClass('current-page-activated');
                current.removeClass('current-page-deactivated');
            }, 200);
        }
    });
    $('.prevPage').on('click',()=>{
        let current = $('.current-page-activated');
        let prev = current.prev('.fill_out_container');
        let curret_page_counter = $('.current-fill-out');
        let prev_page_counter = curret_page_counter.prev('.page_viewer');
        current.removeClass('current-page-activated');
        curret_page_counter.removeClass('current-fill-out');
        prev_page_counter.addClass('current-fill-out');
        setTimeout(function() {
            current.addClass('hidden');
            prev.removeClass('hidden').addClass('current-page-activated');
            current.removeClass('current-page-deactivated');
        }, 200);
    
    });
});