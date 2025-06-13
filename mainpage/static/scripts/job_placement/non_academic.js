$('document').ready(function(){
    $('#program_select').change(function(){
        var awards = {
            'AGRICULTURE': ['Leadership Award', 'Social Responsibility and Civic Engangement Award', 'Others'],
            'BIT': ['Best OJT Award', 'Researcher of the Year', 'Others'],
            'BES': ['Leadership Award', 'Others'],
            'BSHM': ['Leadership Award', 'Others'],
            'BSIE': ['Leadership Award', 'Outstanding Athlete Award', 'Researcher of the Year', 'Others'],
            'BSIT': ['Best Capstone', 'Excellence Award', 'Leadership Award', 'Programmer of the Year', 'Others'],
            'CAS': ['Academic Leadership Award', 'BAEL Pride Award', 'Leadership Award', 'Loyalty Award', 'Outstanding Athlete Award', 'Others'],
            'FORESTRY': ['Leadership Award', 'Outstanding Athlete', 'Others'],
            'COED': ['Best in Elocution Award', 'Leadership Award', 'Relentless Mentor of the Year Award', 'Researcher of the Year', 'Student Extensionista of the Year Award', 'Others']
        };

        $('#program_select').on('change', function() {
            $('#award_select').val('None').trigger('change');
            var selectedProgram = $(this).val();
            var awardSelect = $('#award_select');
            awardSelect.empty(); // Clear existing options

            if (selectedProgram !== 'None' && awards[selectedProgram]) {
                awards[selectedProgram].forEach(function(award) {
                    awardSelect.append(new Option(award, award));
                });
                $('#award_select').trigger('change');
            } else {
                awardSelect.append(new Option('No awards available', ''));
            }
        });

        $('#award_select').on('change', function(){
            $('#leadership_fields').addClass('hidden_fields');
            $('#capstone_fields').addClass('hidden_fields');
            $('#ojt_fields').addClass('hidden_fields');
            $('#research_fields').addClass('hidden_fields');
            $('#Others').addClass('hidden_fields');
            switch ($(this).val()) {
                case "Leadership Award":
                    console.log('Leadership');
                    $('#leadership_fields').removeClass('hidden_fields');
                    break;
                case "Best Capstone":
                    console.log('Capstone');
                    $('#capstone_fields').removeClass('hidden_fields');
                    break;
                case "Best OJT Award":
                    console.log('OJT');
                    $('#ojt_fields').removeClass('hidden_fields');
                    break;
                case "Researcher of the Year":
                    console.log('Research');
                    $('#research_fields').removeClass('hidden_fields');
                    break;
                case "Others":
                    console.log('Others');
                    $('#Others').removeClass('hidden_fields');
                    break;
            }
        })
    })

    $('#assign_student_id').on('input', function(){
        console.log('called')
        let query = $(this).val();
        if(query.length > 0){
            $.ajax({
                url: '/suggestions/',
                data: { 'query': query},
                success: function(data){
                    console.log(data);
                    $('#suggestions').html('');
                    for(let i = 0; i < data.length;i++){
                        text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
                        $('#suggestions').append('<li onclick="assign_student(this)" value="' + data[i][0] + '">' + text + '</li>');
                    }
                }
            })
        } else {
            $('#suggestions').html('');
        }
    })



    $('#program_select').val('None').trigger('change');
})

function assign_student(e){
    let element = $(e);
    $('#stud_id_holder').val(element.val());
    $('#assign_student_id').val(element.text());
    $('#suggestions').html('');
}