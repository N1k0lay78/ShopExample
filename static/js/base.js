$(document).ready(function(){
    $('#burger').click(function(){
        $(this).toggleClass('open');
        $(".navigation").toggleClass("visible");
        if ($(".navigation").hasClass("visible")) {
            $("body").addClass("stop-scroll-1");
        } else if (!$(".navigation").hasClass("visible")) {
            $("body").removeClass("stop-scroll-1");
        }
    });
});