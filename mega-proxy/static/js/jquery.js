$(document).ready(function(){
    function ajax_login(){
        $.ajax(
            {
                url : '/ajax-login',
                data: $('form').serialize(),
                type: 'POST',
                success: function(response) {
                    console.log(response);
                },
                error: function(error){
                    console.log(error);
                }
            }
        )

    }
    $("#login-form").submit(function(event){
        event.preventDefault();
        ajax_login();
    });
});

