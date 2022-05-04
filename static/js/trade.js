$('#trade_btn').click(function() {
    var json = {
        'size':  Number($('#limit-order-size').val()),
        'price': Number($('#limit-order-price').val()),
    }
    var stonk = $('#trade-which-stock').val()
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/placeorder/" + stonk,
        data: JSON.stringify(json),
        success: function (data) {
            var graph = $("#open-orders-div");
            graph.html(data);
        },
        dataType: "html"
    });
});
$('#cancelall_btn').click(function() {
    var stonk = $('#trade-which-stock').val()
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/cancelall/" + stonk,
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#algo-log");
            graph.append(data);
        },
        dataType: "html"
    });
});