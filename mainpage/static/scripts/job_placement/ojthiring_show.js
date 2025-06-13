window.onload = function(){
    //para sa read more cards
    const showPopups = document.querySelectorAll('.btnshow');
    const showContainers = document.querySelectorAll('.show_container');
    const closeButtonsTop = document.querySelectorAll('.close-top');
    const closeButtons = document.querySelectorAll('.close');
    
    showPopups.forEach((showPopup, index) => {
        showPopup.onclick = () => {
            showContainers[index].classList.add('active');
        }
    });
    closeButtonsTop.forEach((closeButtonTop, index) => {
        closeButtonTop.onclick = () => {
            showContainers[index].classList.remove('active');
        }
    });
    closeButtons.forEach((closeBtn, index) => {
        closeBtn.onclick = () => {
            showContainers[index].classList.remove('active');
        }
    });
    window.onclick = function(event) {
        showContainers.forEach(showContainer => {
            if (event.target == showContainer) {
                showContainer.classList.remove('active');
            }
        });
    }

    //para sa pop up form
    const btn = document.querySelector(".showform");
    const formContainer = document.querySelector(".showform_container");
    const xbtn = document.querySelector(".closeform");

    btn.onclick = function() {
        formContainer.classList.add('active');
    }
    xbtn.onclick = function() {
        formContainer.classList.remove('active');
    }

    const btn2 = document.querySelector(".showform2");
    const formContainer2 = document.querySelector(".studentcontainer");
    const xbtn2 = document.querySelector(".closeform2");
    btn2.onclick = function() {
        formContainer2.classList.add('active');
    }
    xbtn2.onclick = function() {
        formContainer2.classList.remove('active');
    }

    $('#stud_id').on('input', function(){
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

    $('#assign_student_id').on('input', function(){
        let query = $(this).val();
        if(query.length > 0){
            $.ajax({
                url: '/suggestions/',
                data: { 'query': query},
                success: function(data){
                    console.log(data);
                    $('#assign_student_suggestions').html('');
                    for(let i = 0; i < data.length;i++){
                        text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
                        $('#assign_student_suggestions').append('<li onclick="assign_stud_id(this)" value="' + data[i][0] + '">' + text + '</li>');
                    }
                }
            })
        } else {
            $('#assign_student_suggestions').html('');
        }
    })
    
    $('#assign_company_id').on('input', function(){
        let query = $(this).val();
        if(query.length > 0){
            $.ajax({
                url: '/suggestions/companies',
                data: { 'query': query},
                success: function(data){
                    console.log(data);
                    $('#company_suggestions').html('');
                    for(let i = 0; i < data.length;i++){
                        text = `${data[i][0]} - ${data[i][1]}, ${data[i][2]}`;
                        $('#company_suggestions').append('<li onclick="assign_company_id(this)" value="'+ data[i][0] + '">' + text + '</li>');
                    }
                }
            })
        } else {
            $('#company_suggestions').html('');
        }
      })

};
    
  function getstudent(e){
    let element = $(e);
    $('#stud_id').val(element.val());
    $('#search_suggestions').html('');
}

function assign_stud_id(e){
    let element = $(e);
    $('#student_id_holder').val(element.val());
    $('#assign_student_id').val(element.text());
    $('#assign_student_suggestions').html('');
}

function assign_company_id(e){
    let element = $(e);
    $('#company_id_holder').val(element.val());
    $('#assign_company_id').val(element.text());
    $('#company_suggestions').html('');
}