$(document).ready(function() {
    $("#search-lots").autocomplete({
        minLength: 2,
        source: "/lots/search-ajax/",
        focus: function( event, ui ) {
            $("#search-lots").val( ui.item.name );
            return false;
        },
        select: function( event, ui ) {
            window.location.href = "/revenue/receipt/add/" + ui.item.name;
            return false;
        }
    }).autocomplete("instance")._renderItem = function(ul, item) {
        return $( "<li>" )
            .append( "<div>" + item.name + " <small>" + item.address + "</small><br>" + item.owner__name + "</div>" )
            .appendTo( ul );
    };
});
