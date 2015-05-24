

function getUsers(){

    return $.ajax({
        url: "http://localhost:5000/project/api/users/"
    }).always(function(){
        //Remove old list of users
        $("#userlist").empty();

    }).done(function (data){
        //Extract the users
        users = data.collection.items;
        for (var i=0; i < users.length; i++){
            var user = users[i];
            //Extract the nickname by getting the data values. Once obtained
            // the nickname use the method appendUserToList to show the user
            // information in the UI.
            //Data format example:
            //  [ { "name" : "nickname", "value" : "Mystery" },
            //    { "name" : "registrationdate", "value" : "2014-10-12" } ]
            var user_data = user.data;
            for (var j=0; j<user_data.length;j++){
                if (user_data[j].name=="nickname"){
                    appendUserToList(user.href, user_data[j].value);
                }
            }
        }

    }).fail(function (){
        //Inform user about the error using an alert message.
        alert ("Could not fetch the list of users.  Please, try again");
    });
}


function appendUserToList(url, nickname) {
    var $user = $('<li>').html('<a class= "user_link" href="'+url+'">'+nickname+'</a>');
    //Add to the user list
    $("#userlist").append($user);
    return $user;
}

/***
 * ON PAGE LOAD
 */
$(function(){

    getUsers();

    $('#userlist').on('click', 'li', function (event) {
        event.preventDefault();
        var userurl = ($("a",this).attr('href'));



    });


})