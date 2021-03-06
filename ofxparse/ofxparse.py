from BeautifulSoup import BeautifulStoneSoup
import decimal, datetime

class Ofx(object):
    pass

class Account(object):
    def __init__(self):
        self.statement = None

class BankAccount(Account):
    def __init__(self):
        Account.__init__(self)
        self.number = ''
        self.routing_number = ''
    
class InvestmentAccount(Account):
    def __init__(self):
        Account.__init__(self)
        self.number = ''
        self.brokerid = ''

class Statement(object):
    def __init__(self):
        self.start_date = ''
        self.end_date = ''
        self.transactions = []

class InvestmentStatement(object):
    def __init__(self):
        self.positions = []
        self.transactions = []

class Transaction(object):
    def __init__(self):
        self.name = ''
        self.type = ''
        self.date = ''
        self.amount = ''
        self.id = ''
        self.memo = ''

class InvestmentTransaction(object):
    def __init__(self):
        self.security = ''
        self.units = 0
        self.unit_price = 0

class Position(object):
    def __init__(self):
        self.security = ''
        self.units = 0
        self.unit_price = 0

class Institution(object):
    pass

class OfxParser(object):
    @classmethod
    def parse(cls_, file_handle):
        if isinstance(file_handle, type('')):
            raise RuntimeError("parse() takes in a file handle, not a string")
        ofx_obj = Ofx()
        ofx = BeautifulStoneSoup(file_handle)
        stmtrs_ofx = ofx.find('stmtrs')
        if stmtrs_ofx:
            ofx_obj.account = cls_.parseStmtrs(stmtrs_ofx)
            return ofx_obj
        ccstmtrs_ofx = ofx.find('ccstmtrs')
        if ccstmtrs_ofx:
            ofx_obj.account = cls_.parseStmtrs(ccstmtrs_ofx)
            return ofx_obj
        invstmtrs_ofx = ofx.find('invstmtrs')
        if invstmtrs_ofx:
            ofx_obj.account = cls_.parseInvstmtrs(invstmtrs_ofx)
            return ofx_obj
        return ofx_obj
    
    @classmethod
    def parseOfxDateTime(cls_, ofxDateTime):
        #dateAsString looks like 20101106160000.00[-5:EST]
        #for 6 Nov 2010 4pm UTC-5 aka EST
        timeZoneOffset = datetime.timedelta(hours=int(ofxDateTime[19:].split(':')[0]))
        return datetime.datetime.strptime(ofxDateTime[:18], '%Y%m%d%H%M%S.%f') - timeZoneOffset

    @classmethod
    def parseInvstmtrs(cls_, invstmtrs_ofx):
        account = InvestmentAccount()
        acctid_tag = invstmtrs_ofx.find('acctid')
        if (hasattr(acctid_tag, 'contents')):
            account.number = acctid_tag.contents[0].strip()
        brokerid_tag = invstmtrs_ofx.find('brokerid')
        if (hasattr(brokerid_tag, 'contents')):
            account.brokerid = brokerid_tag.contents[0].strip()
        
        if (invstmtrs_ofx):
            account.statement = cls_.parseInvestmentStatement(invstmtrs_ofx)
        return account

    @classmethod
    def parseInvestmentPosition(cls_, ofx):
        position = Position()
        tag = ofx.find('uniqueid')
        if (hasattr(tag, 'contents')):
            position.security = tag.contents[0].strip()
        tag = ofx.find('units')
        if (hasattr(tag, 'contents')):
            position.units = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('unitprice')
        if (hasattr(tag, 'contents')):
            position.unit_price = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('dtpriceasof')
        if (hasattr(tag, 'contents')):
            position.date = cls_.parseOfxDateTime(tag.contents[0].strip())
        return position

    @classmethod
    def parseInvestmentTransaction(cls_, ofx):
        transaction = InvestmentTransaction()
        tag = ofx.find('uniqueid')
        if (hasattr(tag, 'contents')):
            transaction.security = tag.contents[0].strip()
        tag = ofx.find('units')
        if (hasattr(tag, 'contents')):
            transaction.units = decimal.Decimal(tag.contents[0].strip())
        tag = ofx.find('unitprice')
        if (hasattr(tag, 'contents')):
            transaction.unit_price = decimal.Decimal(tag.contents[0].strip())
        return transaction

    @classmethod
    def parseInvestmentStatement(cls_, invstmtrs_ofx):
        statement = InvestmentStatement()
        tag = invstmtrs_ofx.find('dtstart')
        if (hasattr(tag, 'contents')):
            statement.start_date = cls_.parseOfxDateTime(tag.contents[0].strip())
        tag = invstmtrs_ofx.find('dtend')
        if (hasattr(tag, 'contents')):
            statement.end_date = cls_.parseOfxDateTime(tag.contents[0].strip())
        for position_ofx in invstmtrs_ofx.findAll("posmf"):
            statement.positions.append(cls_.parseInvestmentPosition(position_ofx))
        for transaction_ofx in invstmtrs_ofx.findAll("buymf"):
            statement.transactions.append(cls_.parseInvestmentTransaction(transaction_ofx))
        return statement

    @classmethod
    def parseStmtrs(cls_, stmtrs_ofx):
        ''' Parse the <STMTRS> tag and return an Account object. '''
        account = BankAccount()
        acctid_tag = stmtrs_ofx.find('acctid')
        if hasattr(acctid_tag, 'contents'):
            account.number = acctid_tag.contents[0].strip()
        bankid_tag = stmtrs_ofx.find('bankid')
        if hasattr(bankid_tag, 'contents'):
            account.routing_number = bankid_tag.contents[0].strip()

        if stmtrs_ofx:
            account.statement = cls_.parseStatement(stmtrs_ofx)
        return account
    
    @classmethod
    def parseStatement(cls_, stmt_ofx):
        '''
        Parse a statement in ofx-land and return a Statement object.
        '''
        statement = Statement()
        dtstart_tag = stmt_ofx.find('dtstart')
        if hasattr(dtstart_tag, "contents"):
            statement.start_date = cls_.parseOfxDateTime(dtstart_tag.contents[0].strip())
        dtend_tag = stmt_ofx.find('dtend')
        if hasattr(dtend_tag, "contents"):
            statement.end_date = cls_.parseOfxDateTime(dtend_tag.contents[0].strip())
        ledger_bal_tag = stmt_ofx.find('ledgerbal')
        if hasattr(ledger_bal_tag, "contents"):
            balamt_tag = ledger_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                statement.balance = balamt_tag.contents[0].strip()
        avail_bal_tag = stmt_ofx.find('availbal')
        if hasattr(avail_bal_tag, "contents"):
            balamt_tag = avail_bal_tag.find('balamt')
            if hasattr(balamt_tag, "contents"):
                statement.available_balance = balamt_tag.contents[0].strip()
        for transaction_ofx in stmt_ofx.findAll('stmttrn'):
            statement.transactions.append(cls_.parseTransaction(transaction_ofx))
        return statement

    @classmethod
    def parseTransaction(cls_, txn_ofx):
        '''
        Parse a transaction in ofx-land and return a Transaction object.
        '''
        transaction = Transaction()

        type_tag = txn_ofx.find('trntype')
        if hasattr(type_tag, 'contents'):
            transaction.type = type_tag.contents[0].lower().strip()

        name_tag = txn_ofx.find('name')
        if hasattr(name_tag, "contents"):
            transaction.payee = name_tag.contents[0].strip()

        memo_tag = txn_ofx.find('memo')
        if hasattr(memo_tag, "contents"):
            transaction.memo = memo_tag.contents[0].strip()

        amt_tag = txn_ofx.find('trnamt')
        if hasattr(amt_tag, "contents"):
            transaction.amount = amt_tag.contents[0].strip()

        date_tag = txn_ofx.find('dtposted')
        if hasattr(date_tag, "contents"):
            transaction.date = cls_.parseOfxDateTime(date_tag.contents[0].strip())

        id_tag = txn_ofx.find('fitid')
        if hasattr(id_tag, "contents"):
            transaction.id = id_tag.contents[0].strip()

        return transaction
