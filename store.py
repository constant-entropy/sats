from arctic import Arctic
from arctic import exceptions as actic_execptions
import json

LIB_SATS_SETTINGS = 'sats_settings'
SYM_SATS_SETTINGS = 'web'
HIS_BALANCES = 'his_balances'

class DBConn():
    def __init__(self):
        self.dbconn = None
        self.settings = None

    def connect(self):
        self.dbconn = Arctic('localhost')
        self.dbconn.initialize_library(LIB_SATS_SETTINGS)
        self.dbconn.list_libraries()
        self.dblib = self.dbconn[LIB_SATS_SETTINGS]
        try:
            settings_ = self.dblib.read(SYM_SATS_SETTINGS).data
            try:
                json.loads(settings_)
            except json.decoder.JSONDecodeError:
                self.default_settings()
        except actic_execptions.NoDataFoundException:
            self.default_settings()

        try:
            balances = self.dblib.read(HIS_BALANCES).data
        except actic_execptions.NoDataFoundException:
            self.dblib.write(HIS_BALANCES, 0)

    def default_settings(self):
        config = json.dumps({
            'r': '1d',
            'pa': 'BTC/ETH',
            'sd': '2021-10-02',
            'ed': '2021-11-02',
            'rp': '30',
            'l': 'English',
            'sb': 'unchecked'
        })
        self.dblib.write(SYM_SATS_SETTINGS, config)

    def write_settings(self, data):
        self.dblib.write(SYM_SATS_SETTINGS, data)
        pass

    def read_web_setting(self):
        return self.dblib.read(SYM_SATS_SETTINGS).data

    def read_last_balances(self):
        return self.dblib.read(HIS_BALANCES).data

    def write_balances_his(self, data):
        self.dblib.write(HIS_BALANCES, data)

    def _on_exit(self):
        #self.dbcon
        pass