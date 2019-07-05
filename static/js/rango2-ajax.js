$(document).ready(function(){
    $('#likes').click(function(){
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango2/like/',{category_id: catid},function(data){
            $('#like_count').html(data);
            $('#likes').hide();
        });
    });
});
