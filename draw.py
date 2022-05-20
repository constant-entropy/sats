"""
May 7 2020 Updates:
https://matplotlib.org/stable/gallery/user_interfaces/web_application_server_sgskip.html?highlight=memory
to avoid all plt related usages
"""
import matplotlib
#import matplotlib.font_manager as fm
matplotlib.use('Agg')
#from matplotlib.font_manager import _rebuild; _rebuild()
#from matplotlib import get_cachedir
#print(get_cachedir())
from matplotlib import rcParams
#print(rcParams['datapath'])
import os
#matplotlib.use('Agg')
#path = os.path.join(rcParams["datapath"], "fonts/afm/pcrr8a.afm")
#prop = matplotlib.font_manager.FontProperties(fname=path)
#print('prop name' + prop.get_name())
#rcParams['font.family'] = prop.get_name()
#rcParams['font.family'] = 'monospace'
#rcParams['font.monospace'] = ['Courier New']
'''See this on font-family not found problem
https://github.com/matplotlib/matplotlib/issues/10201#issuecomment-357355690
https://stackoverflow.com/questions/64118109/findfont-font-family-tahoma-not-found-falling-back-to-dejavu-sans
print(rcParams.keys())
'''
import matplotlib.pyplot as plt, mpld3
import matplotlib.ticker as ticker
#from matplotlib.ticker import FormatStrFormatter

#axes_titlef = fm.FontEntry(fname='pcrr8a.afm', name='Courier', style='normal',size=11)
#print(axes_titlef.name)

import numpy as np

from io import BytesIO
from matplotlib.figure import Figure #since 3.1

def pixel():
    return 1 / plt.rcParams['figure.dpi']

def currency(x, pos):
    if x > 1e3:
        s = '${:1.1f}K'.format(x*1e-3)
    else:
        s = x
    return s

def volume(x, pos):
    """The two args are the value and tick position"""
    if x >= 1e6:
        s = '${:1.1f}M'.format(x*1e-6)
    else:
        s = '${:1.0f}K'.format(x*1e-3)
    return s

class VanGogh():

    def __init__(self):
        plt.ioff()
        plt.style.use('seaborn-bright')
        self.canvas = dict()
        self.facecolor = 'white'

    def set_canvas(self, canvas):
        self.canvas = canvas

    def get_canvas(self, which):
        #print(self.canvas)
        return self.canvas.get(which)

    def set_facecolor(self, fc):
        self.facecolor = fc

    def get_facecolor(self):
        return self.facecolor

    def draw_var_histo(self, returns):
        fig = Figure(figsize=(7, 1.2))
        axs = fig.subplots()
        _, bins, _ = axs.hist(returns, bins=int(len(returns)/5), density=False,
            facecolor='g', alpha=0.75, color='white', rwidth=0.3)
        axs.set_xticks(bins)
        axs.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
        axs.set_xlabel('Daily PNL')
        #axs.set_minor
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        #plt.show()

        return fig_html

    def draw_curve_plot(self, data):
        fig, axs = plt.subplots(figsize=(7, 1.2))
        axs.plot(data)
        #axs.set_xlim(0, 10000)
        #axs.set_xticks
        #axs.set_ylim(min(data), max(data))
        axs.minorticks_off()
        if data[-1] < 0:
            axs.tick_params(length=20,width=20,color='r',bottom=False,labelbottom=False,labeltop=False)
        else:
            axs.tick_params(length=20,width=20,color='g',bottom=False,labelbottom=False,labeltop=False)
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        plt.cla()
        plt.clf()
        plt.close(fig)

        return fig_html

    def draw_result_single_plot(self, names, data):
        width, height = self.get_canvas('position_prices')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        name_a = names[0]
        name_b = names[1]
        axs = fig.subplots()
        axs.set_title('{:s} & {:s} Z-value Result'.format(name_a, name_b))
        #data.plot(ax=axs, color='blue')
        axs.plot(data, color='blue', linewidth=0.8)
        axis_y = [0] * len(data)
        axs.plot(axis_y, color='lightgreen', linestyle='dashdot', linewidth=0.6)
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        return fig_html

    def draw_history_single_plot(self, single):
        width, height = self.get_canvas('trade_graph')
        fig = Figure(figsize=(width * pixel() * 1.3, height * pixel() * 1.3))
        name, df = single['name'], single['data']
        (ax1, ax2) = fig.subplots(nrows=2, ncols=1, sharex=False)
        axis_x = range(0, df.O.size)
        ax1.plot(axis_x, df.O, label='Open')
        ax1.plot(axis_x, df.H, label='Highest')
        ax1.plot(axis_x, df.L, label='Lowest')
        ax1.plot(axis_x, df.C, label='Close')
        ax2.bar(axis_x, df.V, label='Volume', facecolor='g')
        ax2.set_xlabel('Day of October')
        ax1.set_ylabel(name + ' Price (USD)')
        axis_y_0 = [0] * len(axis_x)
        ax1.fill_between(axis_x, df.L, axis_y_0, facecolor='lightblue')
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        return fig_html

    def draw_history_pair_plot(self, pair):
        width, height = self.get_canvas('trade_graph')
        fig = Figure(figsize=(width * pixel() * 1.3, height * pixel() * 1.3))
        axs = fig.subplots(2, 2, sharex=False)
        name_a = pair[0]['name']
        name_b = pair[1]['name']
        fig.suptitle('{:s} & {:s} Price Volume Chart'.format(name_a, name_b))
        df_a = pair[0]['data']
        df_b = pair[1]['data']
        axis_x = range(0, df_a.O.size)
        axs[0, 0].plot(axis_x, df_a.O, label='Open')
        axs[0, 1].plot(axis_x, df_b.O, label='Open')
        axs[0, 0].plot(axis_x, df_a.H, label='Highest')
        axs[0, 1].plot(axis_x, df_b.H, label='Highest')
        axs[0, 0].plot(axis_x, df_a.L, label='Lowest')
        axs[0, 1].plot(axis_x, df_b.L, label='Lowest')
        axs[0, 0].plot(axis_x, df_a.C, label='Close')
        axs[0, 1].plot(axis_x, df_b.C, label='Close')
        axs[1, 0].bar(axis_x, df_a.V, label='Volume', facecolor='w')
        axs[1, 1].bar(axis_x, df_b.V, label='Volume', facecolor='g')
        #axs[0, 0].set_ylabel(name_a + ' Price (USD)',fontname=axes_titlef.name)
        axs[0, 0].set_ylabel(name_a + ' Price (USD)')
        axs[0, 1].set_ylabel(name_b + ' Price (USD)')
        axs[0, 0].yaxis.set_major_formatter(ticker.FuncFormatter(currency))
        axs[1, 0].yaxis.set_major_formatter(ticker.FuncFormatter(volume))
        axis_y_0 = [0] * len(axis_x)
        axs[0, 0].fill_between(axis_x, df_a.L, axis_y_0, facecolor='lightblue')
        axs[0, 1].fill_between(axis_x, df_b.L, axis_y_0, facecolor='lightblue')
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        return fig_html

    def draw_balance_plot(self, data, targets):
        width, height = self.get_canvas('balance')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        axs = fig.subplots(subplot_kw={'facecolor':self.get_facecolor()})
        axis_x = range(0, len(data))
        axs.plot(axis_x,data,color='green',linewidth=0.8)
        for target in targets:
            target_data = [target] * len(data)
            axs.plot(axis_x,target_data,linewidth=0.8,linestyle='dashed')
            axs.fill_between(axis_x,data,target_data,alpha=0.38)
        #initial_data = [0.0152*1e8] * len(data)
        #axs.plot(axis_x,initial_data,linewidth=0.8,color='pink')
        #axs.set_xlim(0, 10000)
        #axs.set_xticks
        #axs.set_ylim(min(data), max(data))
        axs.minorticks_off()
        #axs.tick_params(length=20,width=20,color='g',bottom=False,labelbottom=False,labeltop=False)
        axs.set_xticks([])
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)

        return fig_html

    def draw_drawdown_plot(self, data):
        width, height = self.get_canvas('drawdown')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        axs = fig.subplots(subplot_kw={'facecolor':self.get_facecolor()})
        if data[-1] < 0:
            color='r'
        else:
            color='g'
        axis_x = range(0, len(data))
        axis_y = [min(data)] * len(data)
        axs.plot(data,color=color,linewidth=0.8)
        axs.fill_between(axis_x, data, axis_y, alpha=0.32, facecolor='r')
        #axs.set_xlim(0, 10000)
        #axs.set_xticks
        #axs.set_ylim(min(data), max(data))
        axs.minorticks_off()
        #axs.tick_params(length=20,width=20,color=color,bottom=False,labelbottom=False,labeltop=False)
        axs.set_xticks([])
        axs.xaxis.set_ticks_position('bottom')
        #axs.spines.bottom.set_visible(False)
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)

        return fig_html

    def draw_trade_graph_plot(self, entry_prices, entry_x, spot_prices, trade_prices, spot_x, trade_x, long_prices, long_x, short_prices, short_x):
        width, height = self.get_canvas('trade_graph')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        axs, axs_rate = fig.subplots(2, 1, subplot_kw={'facecolor':self.get_facecolor()})
        #if len(trade_x) == len(trade_prices):
        #    axs.plot(trade_x, trade_prices, 'c:')
        #if len(entry_x) == len(entry_prices):
        #    axs.plot(entry_x, entry_prices, 'm-.')
        spot_line_color='k'
        if len(spot_x) == len(spot_prices):
            axs.plot(spot_x, spot_prices,linewidth=0.8, color=spot_line_color)
            arr = np.array(spot_prices)
            mu = arr.mean()
            std = arr.std()
            axs.fill_between(spot_x,list(arr+std),list(arr-std),alpha=0.32,facecolor='C1')
        if len(long_x) == len(long_prices):
            axs.plot(long_x, long_prices, 'g^')
        if len(short_x) == len(short_prices):
            axs.plot(short_x, short_prices, 'rv')
        #axs.set_xlim(0, 10000)
        #axs.set_xticks
        #axs.set_ylim(min(spot_prices), max(spot_prices))
        axs.minorticks_off()
        axs_rate.minorticks_off()
        #if spot_prices[-1] < 0:
        #    axs.tick_params(length=20,width=20,color='r',bottom=False,labelbottom=False,labeltop=False)
        #else:
        #    axs.tick_params(length=20,width=20,color='g',bottom=False,labelbottom=False,labeltop=False)
        axs.set_xticks([])
        axs_rate.set_xticks([])
        #axs.spines.top.set_visible(False)
        axs.xaxis.set_ticks_position('bottom')
        mirror_spot_prices = [-price for price in spot_prices]
        axs_rate.plot(spot_x, mirror_spot_prices, linewidth=0.6, color='green')
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)

        return fig_html
    
    def draw_heatmap(self):
        vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
              "potato", "wheat", "barley"]
        farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
                "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

        harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
                            [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
                            [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
                            [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
                            [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
                            [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
                            [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


        fig, ax = plt.subplots(figsize=(6.5, 3.6))
        _ = ax.imshow(harvest)

        # Show all ticks and label them with the respective list entries
        ax.set_xticks(np.arange(len(farmers)), labels=farmers)
        ax.set_yticks(np.arange(len(vegetables)), labels=vegetables)

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                rotation_mode="anchor")

        # Loop over data dimensions and create text annotations.
        for i in range(len(vegetables)):
            for j in range(len(farmers)):
                _ = ax.text(j, i, harvest[i, j],
                            ha="center", va="center", color="w")

        #ax.set_title("Harvest of local farmers (in tons/year)")
        fig.tight_layout()
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)
        plt.cla()
        plt.clf()
        plt.close(fig)

        return fig_html

    def draw_positions_prices_chart(self, positions_prices):
        width, height = self.get_canvas('position_prices')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        axs = fig.subplots(subplot_kw={'facecolor':self.get_facecolor()})
        min_y = 1
        for k in positions_prices.keys():
            if min_y > min(positions_prices[k][1:]):
                min_y = min(positions_prices[k][1:])
            axis_x = range(1, len(positions_prices[k]))
            axs.plot(axis_x, positions_prices[k][1:], linewidth=0.8, scalex=True, scaley=True, label=k)
            zero_y = [min_y] * len(positions_prices[k][1:])
            axs.fill_between(axis_x, positions_prices[k][1:], zero_y, alpha=0.35)

        axs.set_xticks([])
        axs.set_ylabel('Rate')
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)

        return fig_html

    def draw_holy_ladder(self, ladders):
        width, height = self.get_canvas('holy_ladder')
        fig = Figure(figsize=(width * pixel(), height * pixel()))
        axs = fig.subplots(subplot_kw={'facecolor':self.get_facecolor()})
        axs.set_title('Holy Ladder Title Placeholder')
        min_y_num = 1
        max_y_num = 0
        for k in ladders.keys():
            x_len = len(ladders[k])
            axis_x = range(1, x_len)
            axis_y = ladders[k][1:]
            if min(axis_y) < min_y_num:
                min_y_num = min(axis_y)
            if max(axis_y) > max_y_num:
                max_y_num = max(axis_y)
            axs.plot(axis_x, axis_y, linewidth=0.8, scalex=True, scaley=True, label=k)
            axis_y2 = [1] * (x_len - 1)
            axs.fill_between(axis_x, axis_y, axis_y2, alpha=0.4)
        axis_x = range(0, 2)
        axis_y = [1] * 2
        axs.plot(axis_x, axis_y, linewidth=0.5, linestyle='dashdot', color='g', fillstyle='bottom', markerfacecolor='blue')
        axis_y_bottom = [min_y_num] * 2
        axs.fill_between(axis_x, axis_y, axis_y_bottom, alpha=0.34, facecolor='red')
        axis_y_top = [max_y_num] * 2
        axs.fill_between(axis_x, axis_y, axis_y_top, alpha=0.34, facecolor='green')
        axs.set_xticks([])
        axs.set_xlabel('Holy Ladders')
        fig_html = mpld3.fig_to_html(fig,include_libraries=False)

        return fig_html