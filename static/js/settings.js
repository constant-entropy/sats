$('.settings-item').change(function() {
    var json = {
        'r':  $('#data-resolution').val(),
        'pa': $('#analysis-pair').val(),
        'sd': $('#start-date').val(),
        'ed': $('#end-date').val(),
        'rp': $('#refresh-period').val(),
        'l':  $('#language').val(),
        'sb': $('#sb-curve').is(':checked') ? 'checked' : 'unchecked'
    }
    console.log(json)
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/settings",
        data: JSON.stringify(json),
        success: function (data) {
        },
        dataType: "html"
    });
});