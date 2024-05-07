$(document).ready(function(){
    $('#tweetForm').submit(function(event){
        event.preventDefault(); // Prevent default form submission
        var userData = $('#tweet').val(); // Get the value from the form
        var selectedOption = $('input[name="option"]:checked').val();
        console.log(selectedOption)
        $.ajax({
            url: '/normalize',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ userInput: userData, option: selectedOption }),
            success: function(response){
                console.log(response);
                $('#result').text(response.result);
            },
            error: function(error){
                console.log(error);
            }
        });
    });
});
