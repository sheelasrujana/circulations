from odoo import fields, models, api, _
from odoo.fields import Command
from odoo.exceptions import UserError, ValidationError
import qrcode, base64
from io import BytesIO
from datetime import datetime


class CreatePayment(models.Model):
    _inherit = 'account.move'


class CreateQuotationPayment(models.TransientModel):
    _name = 'create.quotation.payment.duplicate'

    @api.model
    def default_get(self, values):
        result = super(CreateQuotationPayment, self).default_get(values)
        quotation_obj = self.env['account.move'].browse(self._context.get('active_id'))
        result['order_id'] = quotation_obj.id
        result['quotation_total_amount'] = quotation_obj.amount_total
        result['agent_id'] = quotation_obj.partner_id.id
        result['payment_amount'] = quotation_obj.amount_residual

        return result

    bank_name = fields.Char("Bank Name")
    order_id = fields.Many2one('account.move', string='Reference')
    payment_type = fields.Selection([
        ('full', 'Full Payment'),
        ('partial', 'Partial Payment')
    ], string="Payment Type")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    quotation_total_amount = fields.Monetary('Total Amount', currency_field="currency_id")
    payment_amount = fields.Monetary('Payment Amount', currency_field="currency_id")
    remaining_amount = fields.Monetary('Remaining Amount', currency_field="currency_id")

    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('upi', 'UPI/QR'),
        ('bank', 'Bank - NEFT'),
        ('pdc', 'Cheque'),
    ], string='Payment Mode')
    payee_name = fields.Char('Payee Name')
    payee_mobile = fields.Char('Payee Mobile')
    payment_datetime = fields.Datetime('Payment Date')
    payment_location = fields.Char('Place')
    agent_id = fields.Many2one('res.partner', string='Agent')
    tnx_id = fields.Char('Transaction ID')
    utr_no = fields.Char('UTR No')
    payment_media = fields.Selection([
        ('gpay', 'Google Pay'),
        ('phonepe', 'Phonepe'),
        ('paytm', 'Paytm'),
        ('upi', 'UPI'),
    ], string='Payment Media')
    payment_confirmation_file = fields.Binary('Attachments')
    sender_acc_no = fields.Char("Sender Acc No")
    micr_no = fields.Char('MICR No')
    acc_branch_name = fields.Char("Branch Name")
    ifsc = fields.Char("IFSC")
    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    siginig_authority = fields.Char('Signing Authority')

    qr_code_image = fields.Binary(string='QR Code Image', compute='_compute_qr_code')

    @api.depends('payment_amount')
    def _compute_qr_code(self):
        for record in self:
            upi_id = 'suriyaece1396-2@okhdfcbank'
            data = f"upi://{upi_id}?amount={record.payment_amount}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(upi_id)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # Convert the image to a binary representation
            qr_code_buffer = BytesIO()
            img.save(qr_code_buffer, format="PNG")
            record.qr_code_image = base64.b64encode(qr_code_buffer.getvalue())

    @api.onchange('payment_type')
    def onchange_payment_type(self):
        if self.payment_type == 'partial':
            self.payment_amount = 0.00
        elif self.payment_type == 'full':
            self.payment_amount = self.order_id.amount_total
        else:
            self.payment_amount = 0.00

    @api.onchange('payment_amount')
    def onchange_payment_amount(self):
        self.remaining_amount = self.quotation_total_amount - self.payment_amount

    def action_create_quotation_payment(self):
        if self.payment_amount == 0.00:
            raise UserError('Please enter the Payment Amount')
        else:
            active_id = self._context.get('active_ids')
            rec = self.env['account.move'].browse(active_id)
            name = rec.id
            # abc = self.env['account.']
            for recs in self:
                if recs.payment_type == 'full':
                    rec.payment_state = 'in_payment'
                elif recs.payment_type == 'partial':
                    rec.payment_state = 'partial'
            payment_values = {
                'payment_type': 'inbound',
                'partner_id': self.order_id.partner_id.id,
                'amount': self.payment_amount,
                # 'company_id': self.order_id.company_id.id,
                # 'sale_order_id': self.order_id.id,
            }

            new_payment_obj = self.env['account.payment'].create(payment_values)

            new_payment_obj.action_post()

            payment_info_create_obj = self.env['payment.informations.invoice'].create({
                'agent_id': self.agent_id.id,
                'invoice_id': name,
                'payment_type': self.payment_type,
                'payment_amount': self.payment_amount,
                'payment_mode': self.payment_mode,
                'payee_name': self.payee_name,
                'payee_mobile': self.payee_mobile,
                'payment_datetime': self.payment_datetime,
                'payment_location': self.payment_location,
                'tnx_id': self.tnx_id,
                'utr_no': self.utr_no,
                'payment_media': self.payment_media,
                'payment_confirmation_file': self.payment_confirmation_file,
                'sender_acc_no': self.sender_acc_no,
                'micr_no': self.micr_no,
                'bank_name': self.bank_name,
                'acc_branch_name': self.acc_branch_name,
                'ifsc': self.ifsc,
                'cheque_no': self.cheque_no,
                'cheque_date': self.cheque_date,
                'cheque_expiry_date': self.cheque_expiry_date,
                'siginig_authority': self.siginig_authority,
                # 'payment_information_id': self.order_id.id
            })
            rec.payment_details += payment_info_create_obj
            # active_id = self._context.get('active_ids')
            # rec = self.env['account.move'].browse(active_id)
            # for recs in self:
            #     if recs.payment_type == 'full':
            #         print(recs.payment_type)
            #         rec.payment_state = 'in_payment'
            #     elif recs.payment_type == 'partial':
            #         print(recs.payment_type)
            #         rec.payment_state = 'partial'

        # payment = self.env['account.move']
        # for rec in self:
        #
        #     print("abcddd")
        #     for recs in payment:
        #         if rec.payment_type == 'full':
        #             recs.payment_state = 'paid'
        #             print("done")
        #         elif rec.payment_type == 'partial':
        #             recs.payment_state = 'partial'
        #             print("not done")


            # self.order_id.cio_paid_amount += self.payment_amount

        # self.order_id.payment_mode = self.payment_mode
        # self.order_id.payee_name = self.payee_name
        # self.order_id.payee_mobile = self.payee_mobile
        # self.order_id.payment_datetime = self.payment_datetime
        # self.order_id.payment_location = self.payment_location
        # self.order_id.tnx_id = self.tnx_id
        # self.order_id.utr_no = self.utr_no
        # self.order_id.payment_media = self.payment_media
        # self.order_id.payment_confirmation_file = self.payment_confirmation_file
        # self.order_id.sender_acc_no = self.sender_acc_no
        # self.order_id.micr_no = self.micr_no
        # self.order_id.acc_branch_name = self.acc_branch_name
        # self.order_id.ifsc = self.ifsc
        # self.order_id.cheque_date = self.cheque_date
        # self.order_id.cheque_expiry_date = self.cheque_expiry_date
        # self.order_id.siginig_authority = self.siginig_authority

        return {'type': 'ir.actions.act_window_close'}


class PaymentInformations(models.Model):
    _name = 'payment.informations.invoice'

    payment_type = fields.Selection([
        ('full', 'Full Payment'),
        ('partial', 'Partial Payment')
    ], string="Payment Type")
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('upi', 'UPI/QR'),
        ('bank', 'Bank - NEFT'),
        ('pdc', 'Cheque'),
    ], string='Payment Mode')

    payee_name = fields.Char('Payee Name')
    payee_mobile = fields.Char('Payee Mobile')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_amount = fields.Monetary('Payment Amount', currency_field="currency_id")
    payment_datetime = fields.Datetime('Payment Date')
    payment_location = fields.Char('Place')
    agent_id = fields.Many2one('res.partner', string='Agent')
    tnx_id = fields.Char('Transaction ID')
    utr_no = fields.Char('UTR No')
    payment_media = fields.Selection([
        ('gpay', 'Google Pay'),
        ('phonepe', 'Phonepe'),
        ('paytm', 'Paytm'),
        ('upi', 'UPI'),
    ], string='Payment Media')
    payment_confirmation_file = fields.Binary('Attachments')
    sender_acc_no = fields.Char("Sender Acc No")
    micr_no = fields.Char('MICR No')
    bank_name = fields.Char("Bank Name")
    acc_branch_name = fields.Char("Branch Name")
    ifsc = fields.Char("IFSC")
    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')
    cheque_expiry_date = fields.Date('Cheque Expiry Date')
    siginig_authority = fields.Char('Signing Authority')
    payment_information_id = fields.Many2one('sale.order', string='Sale order ref')

    rio_no = fields.Char(string="CIO Reference")
    amount_due = fields.Monetary(string='Amount Due')
    cio_no = fields.Char(string="CIO Reference")
    invoice_id = fields.Many2one('account.move')
    payment_details = fields.Many2one('account.move')






