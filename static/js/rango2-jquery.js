$(document).ready(function(){
    $("#about-btn").click(function(event){
        alert("You clicked the button using jQuery!")
    });
    $("p").hover(function(){
        $(this).css('color', 'red');
        },
        function(){
        $(this).css('color','blue');
        });
    $("#about-btn").addClass('btn btn-primary');
    $("#about-btn").click(function(event){
        msgstr = $("#msg").html()
        msgstr = msgstr + "000"
        $("#msg").html(msgstr)
    });
    $("#likesd").click(function(event){
        alert("You clicked the button using jQuery!");
        $("#likes").hide();
        numlikes = int($("#like_count").html());
        numlikes = numlikes + 1;
        $("#like_count").html(str(numlikes));
    });
});
