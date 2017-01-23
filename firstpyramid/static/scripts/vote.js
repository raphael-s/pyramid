$(document).ready(function() {
    $(document).on('click', '.vote-button', function(event){
        event.preventDefault();
        var link = $(event.target);
        if (link.is('span')) {
            link = link.parent();
        }
        var imageId = link.data('id');
        var type = link.data('type');
        var url = '/' + type + '/' + imageId;

        jQuery.ajax({
            url     : url,
            type    : 'POST',
            dataType: 'json',
            success : function(data){
                id = '#votes-id-' + imageId;
                $(id).html(data.votes);
                link.parent().find('.vote-button').addClass('disabled');
                link.addClass('voted');
            }
        });
    })
})
