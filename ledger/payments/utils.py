import requests
import datetime
import traceback
import json
import csv
from six.moves import StringIO
from wsgiref.util import FileWrapper
from decimal import Decimal as D
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve
from django.contrib.auth.models import AnonymousUser
from six.moves.urllib.parse import urlparse
#
from ledger.basket.models import Basket
from ledger.catalogue.models import Product
from ledger.payments.models import OracleParser, OracleParserInvoice, Invoice, OracleInterface, OracleInterfaceSystem, BpointTransaction, BpayTransaction, OracleAccountCode 
from oscar.core.loading import get_class
from oscar.apps.voucher.models import Voucher
import logging
logger = logging.getLogger(__name__)


OrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')
Selector = get_class('partner.strategy', 'Selector')
selector = Selector()

def isLedgerURL(url):
    ''' Check if the url is a ledger url
    :return: Boolean
    '''
    match = None
    try:
        match = resolve(urlparse(url)[2])
    except:
        pass
    if match:
        return True
    return False

def checkURL(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except:
        raise

def systemid_check(system):
    system = system[1:]
    if len(system) == 3:
        system = '0{}'.format(system)
    elif len(system) > 4:
        system = system[:4]
    return system

def validSystem(system_id):
    ''' Check if the system is in the itsystems register.
    :return: Boolean
    '''
    if settings.CMS_URL:
        # TODO: prefetch whole systems register list, store in django cache, use that instead of doing a GET request every time
        res = requests.get('{}?system_id={}'.format(settings.CMS_URL,system_id), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
        try:
            res.raise_for_status()
            res = json.loads(res.content).get('objects')
            if not res:
                return False
            return True
        except:
            raise
    else:
        logger.warn('CMS_URL not set, ledger.payments.utils.validSystem will always return true')
        return True

def calculate_excl_gst(amount):
    percentage = D(100 - settings.LEDGER_GST)/ D(100.0)
    return percentage * D(amount)

def createBasket(product_list,owner,system,vouchers=None,force_flush=True):
    ''' Create a basket so that a user can check it out.
        @param product_list - [
            {
                "id": "<id of the product in oscar>",
                "quantity": "<quantity of the products to be added>"
            }
        ]
        @param - owner (user id or user object)
    '''
    try:
        if not validSystem(system):
            raise ValidationError('A system with the given id does not exist.')
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner, AnonymousUser):
            if not isinstance(owner, User):
                owner = User.objects.get(id=owner)
            # Check if owner has previous baskets
            if owner.baskets.filter(status='Open'):
                old_basket = owner.baskets.get(status='Open')

        # Use the previously open basket if its present or create a new one
        if old_basket:
            if system.lower() == old_basket.system.lower() or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket
        if isinstance(owner, User):
            basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        # Check if there are products to be added to the cart and if they are valid products
        if not product_list:
            raise ValueError('There are no products to add to the order.')
        for product in product_list:
            p = Product.objects.get(id=product["id"])
            if not product.get("quantity"):
                product["quantity"] = 1
            valid_products.append({'product': p, 'quantity': product["quantity"]})
        # Add the valid products to the basket
        for p in valid_products:
            basket.add_product(p['product'],p['quantity'])
        # Add vouchers to the basket
        if vouchers is not None:
            for v in vouchers:
                basket.vouchers.add(Voucher.objects.get(code=v["code"]))
        # Save the basket
        basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise

def createCustomBasket(product_list,owner,system,vouchers=None,force_flush=True):
    ''' Create a basket so that a user can check it out.
        @param product_list - [
            {
                "id": "<id of the product in oscar>",
                "quantity": "<quantity of the products to be added>"
            }
        ]
        @param - owner (user id or user object)
    '''
    #import pdb; pdb.set_trace()
    try:
        if not validSystem(system):
            raise ValidationError('A system with the given id does not exist.')
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner, AnonymousUser):
            if not isinstance(owner, User):
                owner = User.objects.get(id=owner)
            # Check if owner has previous baskets
            if owner.baskets.filter(status='Open'):
                old_basket = owner.baskets.get(status='Open')

        # Use the previously open basket if its present or create a new one
        if old_basket:
            if system.lower() == old_basket.system.lower() or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket
        if isinstance(owner, User):
            basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        basket.custom_ledger = True
        # Check if there are products to be added to the cart and if they are valid products
        defaults = ('ledger_description','quantity','price_incl_tax','oracle_code')
        for p in product_list:
            if not all(d in p for d in defaults):
                raise ValidationError('Please make sure that the product format is valid')
            p['price_excl_tax'] = calculate_excl_gst(p['price_incl_tax'])
        # Save the basket
        basket.save()
        # Add the valid products to the basket
        for p in product_list:
            basket.addNonOscarProduct(p)
        # Save the basket (again)
        basket.save()
        # Add vouchers to the basket
        if vouchers is not None:
            for v in vouchers:
                basket.vouchers.add(Voucher.objects.get(code=v["code"]))
            basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise

#Oracle Parser
def generateOracleParserFile(oracle_codes):
    strIO = StringIO()
    fieldnames = ['Activity Code','Amount']
    writer = csv.writer(strIO)
    writer.writerow(fieldnames)
    for k,v in oracle_codes.items():
        if v != 0:
            writer.writerow([k,v])
    strIO.flush()
    strIO.seek(0)
    return strIO

def sendInterfaceParserEmail(oracle_codes,system_name,system_id,error_email=False,error_string=None):
    try:
        dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        recipients = []
        if not error_email:
            _file = generateOracleParserFile(oracle_codes)
            try:
                sys = OracleInterfaceSystem.objects.get(system_id=system_id)
                recipients = sys.recipients.all()
            except OracleInterfaceSystem.DoesNotExist:
                recipients = []

            email = EmailMessage(
                'Oracle Interface Summary for {} as at {}'.format(system_name,dt),
                'Oracle Interface Summary File for {} as at {}'.format(system_name,dt),
                settings.DEFAULT_FROM_EMAIL,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
            )
            email.attach('OracleInterface_{}.csv'.format(dt), _file.getvalue(), 'text/csv')
        else:
            email = EmailMessage(
                'Oracle Interface Summary Error for {} as at{}'.format(system_name,dt),
                'There was an error in generating a summary report for the oracle interface parser.Please refer to the following log output:\n\n\n{}'.format(error_string),
                settings.DEFAULT_FROM_EMAIL,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
            )

        email.send()
    except Exception as e:
        print(traceback.print_exc())
        raise e

def addToInterface(oracle_codes,system_name):
    try:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        for k,v in oracle_codes.items():
            if v != 0:
                found = OracleAccountCode.objects.filter(active_receivables_activities=k)
                if not found:
                    raise ValidationError('{} is not a valid account code'.format(k)) 
                OracleInterface.objects.create(
                    receipt_number = 0,
                    receipt_date = date,
                    activity_name = k,
                    amount = v,
                    customer_name = system_name,
                    description = k,
                    comments = '{} GST/{}'.format(k,date),
                    status = 'NEW',
                    status_date = date
                )
    except:
        raise
def oracle_parser(date,system,system_name):
    with transaction.atomic():
        try:
            invoices = []
            invoice_list = []
            oracle_codes = {}
            parser_codes = {}
            op,created = OracleParser.objects.get_or_create(date_parsed=date)
            bpoint_txns = []
            bpay_txns = []
            bpoint_txns.extend([x for x in BpointTransaction.objects.filter(settlement_date=date,response_code=0)])
            bpay_txns.extend([x for x in BpayTransaction.objects.filter(p_date__contains=date, service_code=0)])
            # Get the required invoices
            for b in bpoint_txns:
                if b.crn1 not in invoice_list:
                    invoice = Invoice.objects.get(reference=b.crn1)
                    if invoice.system == system:
                        invoices.append(invoice)
                        invoice_list.append(b.crn1)
            for b in bpay_txns:
                if b.crn not in invoice_list:
                    invoice = Invoice.objects.get(reference=b.crn)
                    if invoice.system == system:
                        invoices.append(invoice)
                        invoice_list.append(b.crn)
            for invoice in invoices:
                if invoice.order:
                    if invoice.reference not in parser_codes.keys():
                        parser_codes[invoice.reference] = {}
                    # Go through the items
                    items = invoice.order.lines.all()
                    items_codes = [{'id':i.id,'code':i.oracle_code} for i in items]
                    for i in items_codes:
                        v = i['code']
                        k = i['id']
                        if i['code'] not in oracle_codes.keys():
                            oracle_codes[v] = D('0.0')
                        if i['id'] not in parser_codes[invoice.reference].keys():
                            parser_codes[invoice.reference] = {k:{'code':v,'payment': D('0.0'),'refund': D('0.0')}}

                    # Start passing items in the invoice
                    for i in items:
                        code = i.oracle_code
                        item_id = i.id
                        # Check previous parser results for this invoice
                        previous_invoices = OracleParserInvoice.objects.filter(reference=invoice.reference)
                        code_paid_amount = D('0.0')
                        code_refunded_amount = D('0.0')
                        for p in previous_invoices:
                            details = dict(json.loads(p.details))
                            for k,v in details.items():
                                p_item = details[k]
                                if int(k) == item_id:
                                    code_paid_amount +=  D(p_item['payment'])
                                    code_refunded_amount += D(p_item['refund'])

                        # Deal with the current txn
                        paid_amount = D('0.0')
                        for k,v in i.payment_details['bpay'].items():
                            paid_amount += D(v)
                        for k,v in i.payment_details['card'].items():
                            paid_amount += D(v)
                        code_payable_amount = paid_amount - code_paid_amount
                        if code_payable_amount >= 0:
                            oracle_codes[code] += code_payable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'payment':
                                    item[k] += code_payable_amount

                        refunded_amount = D('0.0')
                        for k,v in i.refund_details['bpay'].items():
                            refunded_amount += D(v)
                        for k,v in i.refund_details['card'].items():
                            refunded_amount += D(v)
                        code_refundable_amount = refunded_amount - code_refunded_amount
                        if code_refundable_amount >= 0:
                            oracle_codes[code] -= code_refundable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'refund':
                                    item[k] += code_refundable_amount

            # Convert Deimals to strings as they cannot be serialized
            for k,v in parser_codes.items():
                for a,b in v.items():
                    for r,f in b.items():
                        parser_codes[k][a][r] = str(parser_codes[k][a][r])
            for k,v in parser_codes.items():
                can_add = False
                for g,h in v.items():
                    if h['payment'] != 0 or h['refund'] != 0:
                        can_add = True
                if can_add:
                    OracleParserInvoice.objects.create(reference=k,details=json.dumps(v),parser=op)
            # Add items to oracle interface table
            addToInterface(oracle_codes,system_name)
            # Send an email with all the activity codes entered into the interface table
            sendInterfaceParserEmail(oracle_codes,system_name,system)
            return oracle_codes
        except Exception as e:
            error = traceback.format_exc()
            sendInterfaceParserEmail(oracle_codes,system_name,system,error_email=True,error_string=error)
            raise e

def update_payments(invoice_reference):
    try:
        i = None
        try:
            i = Invoice.objects.get(reference=str(invoice_reference))
        except Invoice.DoesNotExist:
            raise ValidationError('The invoice with refererence {} does not exist'.format(invoice_reference))
        refunded = D(0.0)
        paid = D(0.0)
        # Bpoint Transactions
        if i.order:
            for line in i.order.lines.all():
                paid_amount = line.paid
                refunded_amount = line.refunded
                amount = line.line_price_incl_tax
                total_paid = i.payment_amount
                total_refund = i.refund_amount
                paid += paid_amount
                refunded += refunded_amount
                # Bpoint Amounts
                for bpoint in i.bpoint_transactions:
                    if bpoint.approved:
                        if paid_amount < amount and paid < total_paid:
                            if bpoint.action == 'payment':
                                remaining_amount = amount - paid_amount
                                if bpoint.id in line.payment_details['card'].keys():
                                    new_amount  = D(line.payment_details['card'][bpoint.id]) + remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    line.payment_details['card'][bpoint.id] = str(new_amount)
                                    paid_amount += remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    paid += paid_amount
                                else:
                                    new_amount  = D(0.0) + remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    line.payment_details['card'][bpoint.id] = str(new_amount)
                                    paid_amount += remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    paid += paid_amount
                        if refunded_amount < amount and refunded < total_refund:
                            if bpoint.action == 'refund':
                                remaining_amount = amount - refunded_amount
                                if bpoint.id in line.refund_details['card'].keys():
                                    new_amount = D(line.refund_details['card'][bpoint.id]) + remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    line.refund_details['card'][bpoint.id] = str(new_amount)
                                    refunded_amount += remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    refunded += refunded_amount
                                else:
                                    new_amount = D(0.0) + remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    line.refund_details['card'][bpoint.id] = str(new_amount)
                                    refunded_amount += remaining_amount if remaining_amount <= bpoint.amount else bpoint.amount
                                    refunded += refunded_amount
                # Bpay Transactions
                for bpay in i.bpay_transactions:
                    if bpay.approved:
                        if paid_amount < amount and paid < total_paid:
                            if bpay.p_instruction_code == '05' and bpay.type == '399':
                                remaining_amount = amount - paid_amount
                                if bpay.id in line.payment_details['bpay'].keys():
                                    new_amount  = D(line.payment_details['bpay'][bpay.id]) + remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    line.payment_details['bpay'][bpay.id] = str(new_amount)
                                    paid_amount += remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    paid += paid_amount
                                else:
                                    new_amount  = D(0.0) + remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    line.payment_details['bpay'][bpay.id] = str(new_amount)
                                    paid_amount += remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    paid += paid_amount
                        if refunded_amount < amount and refunded < total_refund:
                            if bpay.p_instruction_code == '25' and bpay.type == '699':
                                remaining_amount = amount - refunded_amount
                                if bpay.id in line.refund_details['bpay'].keys():
                                    new_amount = D(line.refund_details['bpay'][bpay.id]) + remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    line.refund_details['bpay'][bpay.id] = str(new_amount)
                                    refunded_amount += remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    refunded += refunded_amount
                                else:
                                    new_amount = D(0.0) + remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    line.refund_details['bpay'][bpay.id] = str(new_amount)
                                    refunded_amount += remaining_amount if remaining_amount <= bpay.amount else bpay.amount
                                    refunded += refunded_amount
                # Cash Transactions
                for c in i.cash_transactions.all():
                    if paid_amount < amount and paid < total_paid:
                        if c.type == 'payment':
                            remaining_amount = amount - paid_amount
                            if c.id in line.payment_details['cash'].keys():
                                new_amount  = D(line.payment_details['cash'][c.id]) + remaining_amount if remaining_amount <= c.amount else c.amount
                                line.payment_details['cash'][c.id] = str(new_amount)
                                paid_amount += remaining_amount if remaining_amount <= c.amount else c.amount
                                paid += paid_amount
                            else:
                                new_amount  = D(0.0) + remaining_amount if remaining_amount <= c.amount else c.amount
                                line.payment_details['cash'][c.id] = str(new_amount)
                                paid_amount += remaining_amount if remaining_amount <= c.amount else c.amount
                                paid += paid_amount
                    if refunded_amount < amount and refunded < total_refund:
                        if c.type == 'refund':
                            remaining_amount = amount - refunded_amount
                            if c.id in line.refund_details['cash'].keys():
                                new_amount = D(line.refund_details['cash'][c.id]) + remaining_amount if remaining_amount <= c.amount else c.amount
                                line.refund_details['cash'][c.id] = str(new_amount)
                                refunded_amount += remaining_amount if remaining_amount <= c.amount else c.amount
                                refunded += refunded_amount
                            else:
                                new_amount = D(0.0) + remaining_amount if remaining_amount <= c.amount else c.amount
                                line.refund_details['cash'][c.id] = str(new_amount)
                                refunded_amount += remaining_amount if remaining_amount <= c.amount else c.amount
                                refunded += refunded_amount
                line.save()
    except:
        print(traceback.print_exc())
        raise
