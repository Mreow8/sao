$(document).ready(function(){
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