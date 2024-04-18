from odoo import models, fields, api


class Bankdetails(models.Model):
    _name = 'bank.details'

    bank_conditions = fields.Html(string="Bank Details & Terms and Conditions")
    web = fields.Text(string='Web Details')


class AmountToWords(models.Model):
    _inherit = 'account.move'

# The function is for to convert amount from numeric to text formate
    def amount_to_text_custm(self, amt):
        if self.currency_id.name == "INR":
            value = self.number_to_word(amt)
            if amt % 10:
                have = False
                for wrd in value.split(" "):
                    if 'And' in wrd:
                        have = True
                if not have:
                    new_val = ""
                    for r in value.split(" "):
                        if not r:
                            new_val += ' And'
                        else:
                            new_val += ' ' + r
                    value = new_val
            if not value:
                return "Rupees Zero Only"
            return value + " Only"
        else:
            value = self.number_to_word(amt)
            if not value:
                return self.currency_id.name + ' ' + "Zero Only"
            return self.currency_id.name + ' ' + value + " Only"

    def number_to_word(self, number):
        amt = number

        def get_word(n):
            words = {0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                     9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
                     16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty",
                     40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninty"}
            if n <= 20:
                return words[n]
            else:
                ones = n % 10
                tens = n - ones
                return words[tens] + " " + words[ones]

        def get_all_word(n):
            d = [100, 10, 100, 100]
            v = ["", "Hundred And", "Thousand", "Lakh"]
            w = []
            for i, x in zip(d, v):
                t = get_word(n % i)
                if t != "":
                    t += " " + x
                w.append(t.rstrip(" "))
                n = n // i
            w.reverse()
            w = ' '.join(w).strip()
            if w.endswith("And"):
                w = w[:-3]
            return w

        arr = str(number).split(".")
        number = int(arr[0])
        crore = number // 10000000
        number = number % 10000000
        word = ""
        if crore > 0:
            word += get_all_word(crore)
            word += " Crore "
        word += get_all_word(number).strip()
        if len(arr) > 1:
            if len(arr[1]) == 1:
                arr[1] += "0"
            if int(amt) == amt:
                word += get_all_word(int(arr[1]))
            else:
                word += " And " + get_all_word(int(arr[1])) + " Paisa"
        return word