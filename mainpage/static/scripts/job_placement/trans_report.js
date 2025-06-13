function togglemonthlyfilter(el){
    element = $(el);
    if(element.val() === 'true'){
        element.val('false');
    } else if(element.val() === 'false') {
        element.val('true');
    } else {
        console.log('neither true or false')
    }
}
