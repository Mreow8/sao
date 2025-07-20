$(document).ready(function(){
    // testing purposes
    const open = document.querySelector(".view-pdf");
    const close = document.querySelector(".close-button");
    const form = document.querySelector(".showcontainer");
    const xbtn = document.querySelector(".closeform");

    $('.view-pdf').click(function() {
        let ojtRequirementId = $(this).val();
        let attrName = $(this).attr('name');

        let req_holder = $('input[name="req_id"]');
        let attr_holder = $('input[name="attr_name"]');

        
        $.ajax({
            type: 'POST',
            url: `view/iframe/${ojtRequirementId}`,
            data: {
                csrfmiddlewaretoken: '{{ csrf_token }}',
                id: ojtRequirementId,
                attr_name: attrName
            },
            success: function(response) {
                if (response.url) {
                    // Assuming you have an iframe with id="pdfViewer"
                    $('#pdf-iframe').attr('src', response.url);
                    req_holder.val(ojtRequirementId);
                    attr_holder.val(attrName);
                    form.classList.add('active')
                } else {
                    alert('PDF not found!');
                }
            },
            error: function(xhr, textStatus, errorThrown) {
                console.error('Error:', errorThrown);
            }
        });
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
                        $('#search_suggestions').append('<li onclick="assign_stud_id(this)" value="' + data[i][0] + '">' + text + '</li>');
                    }
                }
            })
        } else {
            $('#search_suggestions').html('');
        }
    })
    
    open.addEventListener('click', ()=>{
        form.classList.add('active')
    })
    close.addEventListener('click', ()=>{
        form.classList.remove('active')
    })
    xbtn.addEventListener('click', () => {
        form.classList.remove('active')
    }) 
    window.onclick = function(event) {
        if (event.target == form) {
            form.classList.remove('active');
        }
    }
});

function assign_stud_id(e){
    let element = $(e);
    $('#search_bar').val(element.val());
    // $('#search_bar').val(element.text());
    $('#search_suggestions').html('');
}


