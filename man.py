
import time, datetime
from flask import Flask, render_template, make_response, request
import numpy as np
import json
from statsmodels.tsa.stattools import adfuller
from time import sleep
from store import DBConn
from draw import VanGogh
from fetch import DataFetcher, any_upbit_listing
from cointegration_analysis import cg_f1, cg_f2
import hashlib
from flask import url_for

app = Flask(__name__)

def datetime_to_timestamp(str=None):
    # 2020-11-09T06:53:59.893Z -> unix timestamp
    dt = str
    dtobj = datetime.datetime.strptime(dt[0:19], "%Y-%m-%dT%H:%M:%S")
    currentTimestamp = datetime.datetime.timestamp(dtobj)
    return currentTimestamp

def datetime_cur_timestamp():
    dtobj = datetime.datetime.now(datetime.timezone.utc)
    return datetime.datetime.timestamp(dtobj) - 28800

class Man():

    def __init__(self):
        self.dbconn = None
        self.bitmex = None
        self.vangogh = None
        # Web setting cache
        self.settings_json = None
        self.pair = None
        self.open_pos = []
        self.curve_data = []
        self.curve_fig_html = None
        self.xbt_balances = []
        self.show_balances = ''
        self.btc_prices = []
        self.upnl_total = 0
        self.drawdowns = []
        self.last_trade_signature = ''
        self.balance_targets = []
        self.balances_str = '0.0'
        self.trade_graph_html = None
        self.btc_price_timestamps = []
        self.btc_price_first_timestamp = 0
        self.btc_trade_timestamps = []
        self.btc_trade_prices = []
        self.btc_long_timestamps = []
        self.btc_long_prices = []
        self.btc_short_timestamps = []
        self.btc_short_prices = []
        self.btc_entry_prices = []
        self.btc_entry_timestamps = []
        self.btc_timestamps_normalized = False
        self.common_oo = None
        self.drawdown_v = 0
        self.target_symbol = 'XBTUSD'
        self.positions_prices = dict()

    def hello(self):
        return render_template('base.html')

    def not_found(self, error):
        resp = make_response(render_template('error.html'), 404)
        return resp

    """Risk Management Metrics
    see https://www.investopedia.com/terms/v/var.asp
    """
    def var_by_histo(self, asset):
        data = self.pair[0]['data'].C.reset_index(drop=True)
        # calculate returns
        last = data.pop(0)
        returns = []
        for d in data:
            percent = (d / last - 1.0)*100.0
            returns.append(percent)
            last = d
        #print(returns)
        # 
        fig_html = self.vangogh.draw_var_histo(returns)
        return fig_html

    """Algo"""
    def adf(self, df):
        r = None
        try:
            r = adfuller(df['O'])
        except ValueError as e:
            return str(e)
        return render_template('algo.html', adf_values=r, algo_name='adf')

    def analysis(self):
        zvalue = cg_f1(np.log(self.pair[0]['data'].C), np.log(self.pair[1]['data'].C))[-1]
        '''Drop Timestamp, use default index'''
        zvalue.reset_index(drop=True, inplace=True)
        names = [self.pair[0]['name'], self.pair[1]['name']]
        fig_html = self.vangogh.draw_result_single_plot(names, zvalue)
        return fig_html

    """Paint"""
    def chart(self):
        cfg = json.loads(self.settings_json)

        name = request.args.get('asset', '')
        if name == '':
            return 'Illegal asset name'
        name_list = name.split('.')

        if len(name_list) < 2:
            df = self.bitmex.get_df(name, sd=cfg['sd'], tf=cfg['r'])
            single = {'name': name, 'data': df}
            fig_html = self.vangogh.draw_history_single_plot(single)
        else:
            dfa = self.bitmex.get_df(name_list[0], sd=cfg['sd'], tf=cfg['r'])
            dfb = self.bitmex.get_df(name_list[1], sd=cfg['sd'], tf=cfg['r'])
            self.pair = [{'name': name_list[0], 'data': dfa}, {'name': name_list[1], 'data': dfb}]
            fig_html = self.vangogh.draw_history_pair_plot(self.pair)

        return fig_html

    def cal_curve(self, data, currentTimestamp):
        score = 0
        upnl_diff = 0
        for d in data:
            if d['symbol'] == 'BCHUSD' or d['symbol'] == 'LTCUSD':
                score = score + 1
                upnl_diff = upnl_diff + int(d['upnl'])
        if score >= 2:
            self.curve_data.append(upnl_diff)

            return self.vangogh.draw_curve_plot(self.curve_data)
        else:
            # show price curve of all positions
            has_btc_data = False
            for p in data:
                if p['symbol'] == self.target_symbol:
                    has_btc_data = True
                    self.btc_prices.append(float(p['price']))
                    self.btc_entry_prices.append(float(p['entry']))
                    if self.btc_price_first_timestamp == 0:
                        self.btc_price_first_timestamp = currentTimestamp
                    timestamp_index = currentTimestamp - self.btc_price_first_timestamp
                    self.btc_price_timestamps.append(timestamp_index)
                    self.btc_entry_timestamps.append(timestamp_index)
            if not has_btc_data:
                    price, ts = self.bitmex.get_price_of(self.target_symbol[0:-3])
                    if ts == None:
                        ts = datetime_cur_timestamp()
                    print(price, ts)
                    if self.btc_price_first_timestamp == 0:
                        self.btc_price_first_timestamp = ts
                    self.btc_prices.append(price)
                    timestamp_index = ts - self.btc_price_first_timestamp
                    self.btc_price_timestamps.append(timestamp_index)
            if len(self.btc_prices) > 0:
                return self.vangogh.draw_curve_plot(self.btc_prices)

            return 'not_pair_trade'

    def get_curve(self):
        if self.curve_fig_html == None:
            return 'No curve avaiable'
        return self.curve_fig_html

    def ohlcv(self):
        name= request.args.get('asset', '')
        if name == '':
            return 'Illegal asset name'
        cfg = json.loads(self.settings_json)
        dl = self.bitmex.fetch_ohlcv(name, sd=cfg['sd'], tf=cfg['r'])
        return render_template('ohlcv.html', ohlcv=dl)

    def tick(self, name):
        return render_template('blank.html')

    def settings(self):
        if request.method == 'GET':
            cfg = json.loads(self.settings_json)
            return render_template('settings.html', cfg=cfg)
        else:
            self.settings_json = request.data.decode('ASCII')
            self.dbconn.write_settings(self.settings_json)
            return 'OK'

    def _update_position_prices(self, stock, price):
        if not self.positions_prices.__contains__(stock):
            self.positions_prices.__setitem__(stock, [price, 1.0])
        else:
            base_price = self.positions_prices[stock][0]
            self.positions_prices.__getitem__(stock).append(round(price / base_price, 6))

    def _remove_closed_position_prices(self, open_positions):
        found = False
        for k in self.positions_prices.keys():
            for pos in open_positions:
                if pos['symbol'] == k:
                    found = True
                    break
            if not found:
                self.positions_prices.__delitem__(k)
            found = False

    def positions(self):
        pos = self.bitmex.fetch_positions()

        if pos is None:
            return render_template('positions.html', pos=self.open_pos)

        _open_pos = []
        for p in pos:
            if p['isOpen']:
                _open_pos.append(p)
        self.open_pos = [dict() for p in _open_pos]
        self.upnl_total = 0
        for (stock, p) in enumerate(_open_pos):
            self.open_pos[stock]['entrytime'] = p['openingTimestamp']
            self.open_pos[stock]['symbol'] = p['symbol']
            self.open_pos[stock]['entry'] = p['avgEntryPrice']
            self.open_pos[stock]['price'] = p['lastPrice']
            self.open_pos[stock]['pliq'] = p['liquidationPrice']
            self.open_pos[stock]['size'] = p['currentQty']
            self.open_pos[stock]['upnl'] = p['unrealisedPnl']
            self.open_pos[stock]['pnl'] = p['realisedPnl']
            self.upnl_total = self.upnl_total + int(p['unrealisedPnl'])

            self._update_position_prices(p['symbol'], float(p['lastPrice']))
        self._remove_closed_position_prices(self.open_pos)
        """Calculate Pair Curve
        """
        currentTimestamp = datetime_to_timestamp(pos[0]['currentTimestamp'])
        self.curve_fig_html = self.cal_curve(self.open_pos, currentTimestamp)
        return render_template('positions.html', pos=self.open_pos)

    def openorders(self):
        open_orders = self.bitmex.get_open_orders()
        if open_orders == None:
            if len(self.common_oo):
                return render_template('oo.html', oo=self.common_oo)
            else:
                return render_template('notify.html', log='Get oo failed')
        self.common_oo = [dict() for o in open_orders if o['price']]
        index = 0
        for o in open_orders:
            if o['price']:
                self.common_oo[index]['symbol'] = o['symbol']
                self.common_oo[index]['price'] = o['price']
                self.common_oo[index]['size'] = o['remaining']
                self.common_oo[index]['side'] = o['side']
                index = index + 1

        return render_template('oo.html', oo=self.common_oo)

    def placeorder(self, name):
        order = json.loads(request.data.decode('ASCII'))
        #print(order)
        amount = order['size']
        price = order['price']
        #venue = 'BitMEX'
        #info = {'venue': venue, 'size': amount, 'price': price}
        self.bitmex.place_limit_order(name, amount, price)

        sleep(0.5)
        open_orders = self.bitmex.get_open_orders()
        common_oo = [dict() for o in open_orders if o['price']]
        index = 0
        for o in open_orders:
            if o['price']:
                common_oo[index]['symbol'] = o['symbol']
                common_oo[index]['price'] = o['price']
                common_oo[index]['size'] = o['remaining']
                common_oo[index]['side'] = o['side']
                index = index + 1

        return render_template('oo.html', oo=common_oo)

    def traderinit(self):
        return render_template('trade.html')

    def pairtrade(self):
        results = self.bitmex.buy_at_best_bid('BCH', 1)
        print(results)
        results = self.bitmex.sell_at_best_ask('LTC', 1)
        results = 'Ok trade'
        return render_template('notify.html', log=results)

    def pairexit(self):
        results = self.bitmex.buy_at_best_bid('LTC', 1)
        results = self.bitmex.sell_at_best_ask('BCH', 1)
        results = 'Ok exit'
        return render_template('notify.html', log=results)

    def bestquote(self):
        order = json.loads(request.data.decode('ASCII'))
        #print(order)
        name = order['symbol']
        amount = order['size']
        if amount == 0:
            return render_template('notify.html', log='Wrong amount')
        if amount < 0:
            results = self.bitmex.sell_at_best_ask(name, abs(amount))
        else:
            results = self.bitmex.buy_at_best_bid(name, amount)
        try:
            if results['remaining'] >= 0:
                results = '{0} Limit {1[side]} @ {1[price]}:{1[remaining]}:{1[filled]}'.format(
                    datetime.datetime.now(), results)
        except KeyError as error:
            print(error)
        return render_template('notify.html', log=results)

    def upnl_balances_ratio(self):
        balances = self.bitmex.get_total_balances()
        if balances != None:
            self.drawdown_v = round(self.upnl_total / int(balances), 6)
        self.drawdowns.append(self.drawdown_v)
        if self.show_balances == 'checked':
            return self.vangogh.draw_drawdown_plot(self.drawdowns)
        else:
            return render_template('notify.html', log=self.drawdown_v)

    def cancelall(self, name):
        results = self.bitmex.cancel_all_orders(name)
        status = 'No Order Found!'
        try:
            orders = 0
            for result in results:
                if result['remaining'] > 0:
                    orders = 1 + orders
            status = '{} Cancel {} order(s)'.format(datetime.datetime.now(), orders)
        except KeyError as error:
            print(error)
        return render_template('notify.html', log=status)

    def balances(self):
        self.balances_str = self.bitmex.get_total_balances()
        return render_template('notify.html', log=self.balances_str)

    def balances_curve(self):
        self.balances_str = self.bitmex.get_total_balances()
        if self.balances_str == None:
            return 'Non balances curve available'
        balances = float(self.balances_str)
        self.dbconn.write_balances_his(balances)
        self.xbt_balances.append(balances)
        cfg = json.loads(self.settings_json)
        self.show_balances = cfg['sb']
        if self.show_balances == 'checked':
            fig_html = self.vangogh.draw_balance_plot(self.xbt_balances)
        else:
            fig_html = self.balances_str
        return fig_html

    def check_new_listing(self):
        any_upbit_listing()
        return ''

    def trade_history(self):
        return_code = 200
        trades = self.bitmex.get_today_trades(20)
        if trades == None:
            return 'No trade history available'
        #signature = hashlib.md5(trades)
        signature = trades[-1]['timestamp']
        if self.last_trade_signature != signature:
            self.last_trade_signature = signature
        else:
            return_code = 208 # already reported
        recent_trades = []
        for trade in trades:
            if trade['ordType'] == 'Limit' and trade['side'] != '':
                if trade['side'] == 'Sell':
                    trade['orderQty'] = 's' + trade['orderQty']
                else:
                    trade['orderQty'] = 'b' + trade['orderQty']
                #trade['timestamp'] = trade['timestamp'].split('T')[1]
                recent_trades.insert(0, trade)
        # new trades. update long short data
        if return_code != 208:
            btc_trades = []
            trades = recent_trades.copy()
            for trade in trades:
                if trade['symbol'] == self.target_symbol:
                    btc_trades.append(trade)
            # don't clear those data if not
            # any btc trade happens
            if len(btc_trades) > 0:
                self.btc_trade_prices.clear()
                self.btc_trade_timestamps.clear()
                self.btc_long_prices.clear()
                self.btc_long_timestamps.clear()
                self.btc_short_prices.clear()
                self.btc_short_timestamps.clear()
            for trade in btc_trades:
                trade_timestamp = datetime_to_timestamp(trade['timestamp'])
                print(trade_timestamp)
                # we don't draw old trades
                if trade_timestamp < self.btc_price_first_timestamp:
                    continue
                self.btc_trade_prices.append(float(trade['price']))
                trade_timestamp = trade_timestamp - self.btc_price_first_timestamp
                self.btc_trade_timestamps.append(trade_timestamp)
                if trade['side'] == 'Sell':
                    self.btc_short_prices.append(float(trade['price']))
                    self.btc_short_timestamps.append(trade_timestamp)
                else:
                    self.btc_long_prices.append(float(trade['price']))
                    self.btc_long_timestamps.append(trade_timestamp)
        # limit display counts
        while len(recent_trades) > 12:
            recent_trades.pop()
        return render_template('trade_log.html', trades=recent_trades), return_code

    def next_target(self):
        init = 0.0152 * 1e8
        log = ''
        balances = float(self.balances_str)
        if balances <= 0:
            log = 'no balances avaiable'
        balance_final_target = 1e8
        if len(self.balance_targets) > 0:
            if balances < balance_final_target:
                if balances >= self.balance_targets[0]:
                    self.balance_targets.pop()
                log = str(self.balance_targets[0])
            else:
                log = 'Congratulates! 1BTC goal reached!'
        else:
            gain = 0.2
            while init < balance_final_target:
                init = init + gain * init
                self.balance_targets.append(init)
                sleep(0.1)
            log = str(self.balance_targets[0])

        return render_template('notify.html', log='{:.1f} -> {}'.format(balances, log))

    # keep only one day chart
    # remove trades before program started
    def _slim_trade_graph_data(self):
        while len(self.btc_prices) >= 4:
            first_price_ts = self.btc_price_timestamps[0]
            last_price_ts = self.btc_price_timestamps[-1]
            diff_price_ts = last_price_ts - first_price_ts
            if diff_price_ts < 86400:
                break
            # remove first entries
            self.btc_prices.pop(0)
            self.btc_price_timestamps.pop(0)

        if len(self.btc_price_timestamps) <= 0:
            return

        while len(self.btc_trade_timestamps) > 0 and self.btc_trade_timestamps[0] < self.btc_price_timestamps[0]:
            self.btc_trade_prices.pop(0)
            self.btc_trade_timestamps.pop(0)

        while len(self.btc_long_timestamps) > 0 and self.btc_long_timestamps[0] < self.btc_price_timestamps[0]:
            self.btc_long_prices.pop(0)
            self.btc_long_timestamps.pop(0)

        while len(self.btc_short_timestamps) > 0 and self.btc_short_timestamps[0] < self.btc_price_timestamps[0]:
            self.btc_short_prices.pop(0)
            self.btc_short_timestamps.pop(0)

        while len(self.btc_entry_timestamps) > 0 and self.btc_entry_timestamps[0] < self.btc_price_timestamps[0]:
            self.btc_entry_prices.pop(0)
            self.btc_entry_timestamps.pop(0)

    def trade_graph(self):
        if len(self.btc_prices) > 0 or len(self.btc_trade_prices) > 0:
            # Make sure entry line above all the x-axis
            if len(self.btc_trade_timestamps) and len(self.btc_price_timestamps):
                if self.btc_trade_timestamps[0] < self.btc_price_timestamps[0]:
                    if len(self.btc_entry_prices) and len(self.btc_entry_timestamps):
                        self.btc_entry_timestamps.insert(0, self.btc_trade_timestamps[0])
                        self.btc_entry_prices.insert(0, self.btc_entry_prices[0])
            '''print('--- prices trades ---')
            print(self.btc_prices)
            print(self.btc_price_timestamps)
            print(self.btc_trade_prices)
            print(self.btc_trade_timestamps)
            print('--- longs shorts ---')
            print(self.btc_long_prices)
            print(self.btc_long_timestamps)
            print(self.btc_short_prices)
            print(self.btc_short_timestamps)
            print('--- entry ---')
            print(self.btc_entry_prices)
            print(self.btc_entry_timestamps)'''
            self._slim_trade_graph_data()
            if len(self.btc_entry_prices) != len(self.btc_entry_timestamps):
                self.btc_entry_prices.clear()
                self.btc_entry_timestamps.clear()
            self.trade_graph_html = self.vangogh.draw_trade_graph_plot(self.btc_entry_prices, self.btc_entry_timestamps, self.btc_prices, self.btc_trade_prices, self.btc_price_timestamps, self.btc_trade_timestamps, self.btc_long_prices, self.btc_long_timestamps, self.btc_short_prices, self.btc_short_timestamps)
        if self.trade_graph_html == None:
            return 'No trade graph available'
        return self.trade_graph_html

    def heat_map(self):
        if True:
            return 'No heatmap available'
        return self.vangogh.draw_heatmap()

    def restart(self):
        req = json.loads(request.data.decode('ASCII'))
        #print(order)
        delay = req['delay']
        return render_template('notify.html', log='Restarting with Delay' + delay)

    def _clear_tracks(self):
        self.btc_price_first_timestamp = 0
        self.btc_prices.clear()
        self.btc_price_timestamps.clear()
        self.btc_trade_prices.clear()
        self.btc_trade_timestamps.clear()
        self.btc_long_prices.clear()
        self.btc_long_timestamps.clear()
        self.btc_short_prices.clear()
        self.btc_short_timestamps.clear()
        self.btc_entry_prices.clear()
        self.btc_entry_timestamps.clear()

    def track_target_asset(self):
        req = json.loads(request.data.decode('ASCII'))
        if req['asset'][-3:] == 'USD':
            if self.target_symbol != req['asset']:
                self.target_symbol = req['asset']
                self._clear_tracks()
            resp = 'Set target {} Ok'.format(self.target_symbol[0:-3])
        else:
            resp = 'Illegal target'
        return render_template('notify.html', log=resp)

    def positions_prices_chart(self):
        fig_html = self.vangogh.draw_positions_prices_chart(self.positions_prices)
        return fig_html

    def go(self):
        """Painter
        """
        self.vangogh = VanGogh()

        """Connect MongoDB
        """
        self.dbconn = DBConn()
        self.dbconn.connect()
        self.settings_json = self.dbconn.read_web_setting()
        print(self.settings_json)

        """Connect Exchanges
        """
        self.bitmex = DataFetcher()
        self.xbt_balances.append(float(self.dbconn.read_last_balances()))

        """Mount view functions
        """
        app.add_url_rule("/", "hello", view_func=self.hello)
        #app.add_url_rule("404", view_func=self.not_found)
        app.add_url_rule('/chart', view_func=self.chart, methods=['GET'])
        app.add_url_rule('/ohlcv', view_func=self.ohlcv, methods=['GET'])
        app.add_url_rule("/tick/<name>", view_func=self.tick, methods=['POST', 'GET'])
        app.add_url_rule("/analysis", view_func=self.analysis, methods=['POST'])
        app.add_url_rule("/settings", view_func=self.settings, methods=['POST','GET'])
        app.add_url_rule('/positions', view_func=self.positions)
        app.add_url_rule('/traderinit', view_func=self.traderinit)
        app.add_url_rule('/curve', view_func=self.get_curve)
        app.add_url_rule('/openorders', view_func=self.openorders)
        app.add_url_rule('/varhist/<asset>', view_func=self.var_by_histo, methods=['GET'])
        app.add_url_rule('/placeorder/<name>', view_func=self.placeorder, methods=['POST'])
        app.add_url_rule('/cancelall/<name>', view_func=self.cancelall, methods=['POST'])
        app.add_url_rule('/pairtrade', view_func=self.pairtrade, methods=['POST'])
        app.add_url_rule('/balances', view_func=self.balances, methods=['GET'])
        app.add_url_rule('/pairexit', view_func=self.pairexit, methods=['POST'])
        app.add_url_rule('/balances_curve', view_func=self.balances_curve, methods=['GET'])
        app.add_url_rule('/check_new_listing', view_func=self.check_new_listing, methods=['GET'])
        app.add_url_rule('/trade_history', view_func=self.trade_history, methods=['GET'])
        app.add_url_rule('/bestquote', view_func=self.bestquote, methods=['POST'])
        app.add_url_rule('/upnl_balances_ratio', view_func=self.upnl_balances_ratio, methods=['GET'])
        app.add_url_rule('/next_target', view_func=self.next_target)
        app.add_url_rule('/trade_graph', view_func=self.trade_graph)
        app.add_url_rule('/heat_map', view_func=self.heat_map)
        app.add_url_rule('/track_target_asset', view_func=self.track_target_asset, methods=['POST'])
        app.add_url_rule('/positions_prices_chart', view_func=self.positions_prices_chart)

        app.run(debug=True)

if __name__ == '__main__':
    realMan = Man()
    realMan.go()