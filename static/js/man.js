$('#settings-div').hide();
$('.settings-btn').click(function() {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/settings",
        success: function (data) {
            var graph = $("#settings-div");
            graph.html(data);
        },
        complete: function () {
            $('#settings-div').toggle();
        },

        dataType: "html"
    });
});
function refreshMethod() {
    $.ajax({
        type: "GET",
        url: "/tick/tickpair",
        success: function(data) {
            console.log('response: ', data);
        },
        complete: function() {
            setTimeout(refreshMethod, 5000);
        }
    });
}
function traderInit() {
    return $.ajax({
        type: "GET",
        url: "/traderinit",
        success: function(data) {
            var graph = $("#trade-div");
            graph.html(data);
        }
    });
}
traderInit()
 .then(cmdPeriodUpdateTask)

function cmdPeriodUpdateTask() {
    cmdGetPositions()
    .then(cmdGetOpenOrders)
    .then(cmdBalancesCurve)
    .then(cmdGetTrades)
    .then(cmdTradeGraph)
    .then(cmdUpnlRatio)
    .then(cmdPositionsChart)
    .then(setTimeout(cmdPeriodUpdateTask, 100*1000));
}

function cmdBalancesCurve () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/balances_curve",
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#balances-div");
            graph.html(data);
        },
        complete: function () {
        },
        dataType: "html"
    });
}

function cmdFetchHistory(what) {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/ohlcv",
        data: "asset=" + what,
        success: function (data) {
            var graph = $("#canvas");
            graph.html(data);
        },
        dataType: "html"
    });
}
function cmdAnalysis (A, B) {
    $.ajax({
        type: "POST",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/analysis",
        data: JSON.stringify(A, B),
        success: function (data) {
            var graph = $("#canvas2");
            graph.html(data);
        },
        dataType: "html"
    });
}
function cmdChart (w) {
    $.ajax({
        type: "GET",
        async:true,
        contentType: "application/json; charset=utf-8",
        url: "/chart",
        data: "asset=" + w,
        success: function (data) {
            var graph = $("#canvas");
            graph.html(data);
        },
        dataType: "html"
    });
}
function cmdGetPositions () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/positions",
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#positions-div");
            graph.html(data);
        },
        complete: function () {
        },
        dataType: "html"
    });
}
function cmdRepeatCall (cmd) {
    setTimeout(cmdGetPositions, 10000);
}
function cmdGetCurve () {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/curve",
        data: JSON.stringify(),
        success: function (data) {
            //var graph = $("#pair-upnl-canvas");
            //graph.html(data);
        },
        dataType: "html"
    });
}
function cmdGetOpenOrders () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/openorders",
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#open-orders-div");
            graph.html(data);
        },
        dataType: "html"
    });
}
function cmdVarHist (asset) {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/varhist/" + asset,
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#canvas");
            graph.html(data);
        },
        dataType: "html"
    });
}
function cmdCleanUp () {
    $("#canvas").html('');
    $("#canvas2").html('');
    $("#pair-upnl-canvas").html('');
    $("#algo-log").html('');
}
function cmdPairTrade () {
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/pairtrade",
        data: JSON.stringify(),
        success: function (data) {
            $("#algo-log").append(data);
        },
        dataType: "html"
    });
}
function cmdGetBalances () {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/balances",
        data: JSON.stringify(),
        success: function (data) {
            $("#algo-log").append(data);
        },
        dataType: "html"
    });
}
function cmdPairExit () {
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/pairexit",
        data: JSON.stringify(),
        success: function (data) {
            $("#algo-log").append(data);
        },
        dataType: "html"
    });
}
function cmdCheckNewListing () {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/check_new_listing",
        data: JSON.stringify(),
        success: function (data) {
            $("#algo-log").append(data);
        },
        dataType: "html"
    });
}
function cmdGetTrades () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/trade_history",
        data: JSON.stringify(),
        success: function (data, textStatus, xhr) {
            if (xhr.status == 200)
                $("#algo-log").html(data);
        },
        complete: function () {
        },
        dataType: "html"
    });
}
function cmdBestQuote (asset, amount) {
    var json = {
        'symbol': asset,
        'size':  amount,
    }
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/bestquote",
        data: JSON.stringify(json),
        success: function (data) {
            var graph = $("#algo-log");
            graph.append(data);
        },
        dataType: "html"
    });
}
function cmdUpnlRatio () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/upnl_balances_ratio",
        data: JSON.stringify(),
        success: function (data) {
            $("#drawdown-div").html(data);
        },
        dataType: "html"
    });
}
function cmdNextTarget () {
    $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/next_target",
        data: JSON.stringify(),
        success: function (data) {
            $("#algo-log").append(data);
        },
        dataType: "html"
    });
}
function cmdTradeGraph () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/trade_graph",
        data: JSON.stringify(),
        success: function (data) {
            $("#canvas").html(data);
        },
        dataType: "html"
    });
}
function cmdHeatMap () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/heat_map",
        data: JSON.stringify(),
        success: function (data) {
            $("#canvas2").html(data);
        },
        dataType: "html"
    });
}
function cmdTrackSymbol (symbol) {
    var json = {
        'asset': symbol
    }
    $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/track_target_asset",
        data: JSON.stringify(json),
        success: function (data) {
            var graph = $("#algo-log");
            graph.append(data);
        },
        dataType: "html"
    });
}
function cmdPositionsChart () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/positions_prices_chart",
        data: JSON.stringify(),
        success: function (data) {
            $("#canvas2").html(data);
        },
        dataType: "html"
    });
}
jQuery(function($, undefined) {
    $('#terminal-div').terminal({
        analysis: function(a, b) {
            cmdAnalysis(a, b);
        },
        ohlcv: function(w) {
            cmdFetchHistory(w);
        },
        chart: function(w) {
            cmdChart(w);
        },
        pos: function() {
            cmdGetPositions();
        },
        repeat: function(cmd) {
            cmdRepeatCall(cmd);
        },
        oo: function () {
            cmdGetOpenOrders();
        },
        varhist: function (asset) {
            cmdVarHist(asset);
        },
        cleanup: function () {
            cmdCleanUp();
        },
        pairtrade: function () {
            cmdPairTrade();
        },
        balances: function () {
            cmdGetBalances();
        },
        pairexit: function () {
            cmdPairExit();
        },
        cnl: function () {
            cmdCheckNewListing();
        },
        trades: function () {
            cmdGetTrades();
        },
        bbo: function (asset, amount) {
            cmdBestQuote(asset, amount);
        },
        upnlr: function () {
            cmdUpnlRatio();
        },
        nt: function () {
            cmdNextTarget();
        },
        tg: function () {
            cmdTradeGraph();
        },
        track: function (symbol) {
            cmdTrackSymbol(symbol);
        }
    }, {
        greetings: ' :- ',
        name: 'sats_console',
        height: $('#open-orders-div').width(),
        prompt: '\n$ ',
    });
});