$(document).ready(function(){
    // testing purposes
    $('#dummy.id').on('click', function(){
        console.log("Clicked");
    });

    $('#saveAll').on('click' , function(){
        console.log('save all clicked');
        const tableData = [];
        
        $('#attendeeTable tbody tr').each(function(){
            const rows = {
                sem_att_id: $(this).data('item-id'), 
                stud_id: $(this).find('td:eq(0)').text()
            };
            tableData.push(rows);
        });
        
        console.log(tableData)
        let sem_id = $("#sem_id").val();
        let _url = `jobplacement/attendance/attend_all/${sem_id}`;
        // send recorded data to the server using ajax
        $.ajax({
            url: _url,
            method: 'POST',
            contentType: 'application/json',
            followRedirects: true,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            },
            data: JSON.stringify(tableData),
            success: function(){
                console.log("Successfully POST items!");
                window.location.reload();
            }, 
            error: function(){
                console.log('Failed to POST items,');
            }
        })
    });

    $('#search_bar').on('input', function(){
        let query = $(this).val();
        if(query.length > 0){
            $.ajax({
                url: '/suggestions/',
                data: { 'query': query},
                success: function(data){
                    console.log(data);
                    $('#search_suggestions').html('');
                    for(let i = 0; i < data.length;i++){
                        text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
                        $('#search_suggestions').append('<li onclick="getstudent(this)" value="' + data[i][0] + '">' + text + '</li>');
                    }
                }
            })
        } else {
            $('#search_suggestions').html('');
        }
    })
});    

function getstudent(e){
    let element = $(e);
    $('#search_bar').val(element.val());
    $('#search_suggestions').html('');
}