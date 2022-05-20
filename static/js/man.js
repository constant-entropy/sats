$(window).on('resize', function () {
    cmdSetCanvas();
})
var get_cookie = function (name) {
    const cookieValue = 100;
    try {
        cookieValue = document.cookie
         .split('; ')
         .find(row => row.startsWith(name))
         .split('=')[1];
    } catch (e) {
        //console.log('get_cookie: ', e.name);
    }
    if (cookieValue < 10) {
        cookieValue = 10;
    }
    return cookieValue;
}
var get_canvas = function () {
    var json = {
        'balance': [$('#balances-container').width(),$('#balances-container').height()],
        'trade_graph': [$('#canvas-container').width(),$('#canvas-container').height()],
        'drawdown': [$('#drawdown-container').width(), $('#drawdown-container').height()],
        'position_prices': [$('#canvas2-container').width(), $('#canvas2-container').height()],
        'holy_ladder': [$('#canvas-holy-ladder').width(), $('#canvas-holy-ladder').height()]
    };
    //console.log(json);
    return json;
};
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
 .then(cmdGetPositions)
 .then(cmdSetCanvas)
 .then(setTimeout(cmdPeriodUpdateTask, 3*1000))

function cmdSetCanvas() {
    return $.ajax({
        type: "POST",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/set_canvas",
        data: JSON.stringify(get_canvas()),
        success: function(data) {
        }
    });
}
function cmdPeriodUpdateTask() {
    cmdGetPositions()
    .then(cmdGetOpenOrders)
    .then(cmdBalancesCurve)
    .then(cmdGetTrades)
    .then(cmdTradeGraph)
    .then(cmdHolyLadder)
    .then(cmdUpnlRatio)
    .then(cmdPositionsChart)
    .then(cmdGetConnectionQuality)
    .then(setTimeout(cmdPeriodUpdateTask, get_cookie('rp')*1000));
}

function cmdBalancesCurve () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/balances_curve",
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#balances-container");
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
    return $.ajax({
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
function cmdBestQuoteV2 (asset, amount, interval, total) {
    console.log('cmdBestQuoteV2 called', asset, amount, interval, total, Date());
    cmdBestQuote(asset, amount)
     .then(function () {
         if (total > 0)
            setTimeout(cmdBestQuoteV2.bind(null, asset, amount, interval, total - 1), interval*1000);
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
            $("#drawdown-container").html(data);
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
            $("#canvas-container").html(data);
        },
        dataType: "html"
    });
}

function cmdHolyLadder () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/holy_ladder",
        data: JSON.stringify(),
        success: function (data) {
            $("#canvas-holy-ladder").html(data);
        },
        dataType: "html"
    })
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
function cmdGetConnectionQuality () {
    return $.ajax({
        type: "GET",
        async: true,
        contentType: "application/json; charset=utf-8",
        url: "/connection_quality",
        data: JSON.stringify(),
        success: function (data) {
            var graph = $("#pair-upnl-canvas");
            graph.html(data);
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
            $("#canvas2-container").html(data);
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
        },
        bbov2: function (asset, amount, interval, total) {
            cmdBestQuoteV2(asset, amount, interval, total);
        }
    }, {
        greetings: ' :- ',
        name: 'sats_console',
        height: $('#open-orders-div').width(),
        prompt: '\n$ ',
    });
});