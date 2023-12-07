# -*- coding: utf-8 -*-


from odoo import models, fields, api

FIELDS_TO_CLEAR = ['final_incentive_percent', 'work_hrs', 'extra_hrs', 'rewards', 'bouns',
                    'commission', 'allowances', 'transportation', 'management_allowance', 
                    'mobile_bills', 'inability', 'withdrawals', 'taxes', 'indebtedness',
                    'payments', 'subtraction', 'insurance', 'mistakes', 'deductions', 'penalty']

class hrEmployee(models.Model):
    _inherit = "hr.employee"

    public_target = fields.Float('Public Target')
    unpublic_target = fields.Float('Non Public Target')
    hour_price = fields.Float('Hour Price')
    work_hrs = fields.Float('Work Hours')
    incentive_hour = fields.Float('Incentive Hour')
    lab_target = fields.Float('Lab Target')
    cosmo_target = fields.Float('Cosmo Target')
    chronic_target = fields.Float('Chronic Target')
    allowances = fields.Float('بدلات')
    extra_hrs = fields.Float('الساعات اﻹضافية')
    rewards = fields.Float('المكافأت')
    bouns = fields.Float('الحافز')
    commission = fields.Float('العمولة')
    deductions = fields.Float('استقطاعات')
    penalty = fields.Float('جزاءات')
    mobile_bills = fields.Float('جوال')
    inability = fields.Float('عجز خزينة')
    withdrawals = fields.Float('مسحوبات ادوية')
    taxes = fields.Float('ضريبة')
    indebtedness = fields.Float('مديونية مجدولة')
    payments = fields.Float('سلف')
    payment_date = fields.Date('تاريخ السلفة')
    payment_qty = fields.Float('قيمة السلفة')
    payment_period = fields.Float('مدة السلفة')
    payment_installment = fields.Float('قسط السلفة', compute='_compute_payment_installment')
    subtraction = fields.Float('استقطاع اداره الجوده')
    insurance = fields.Float('تامينات')
    mistakes = fields.Float('اخطاء تعاقدات')
    final_incentive_percent = fields.Float('Final Incentive Percent %')   
    transportation = fields.Float('إنتقالات')
    management_allowance = fields.Float('بدلات إدارية')
    has_vacancy = fields.Boolean('Has Vacancy')
    regular_vacation = fields.Integer('إجازات إعتيادية', default=14)
    casual_vacation = fields.Integer('إجازات عارضة', default=7)
    total_vacancy_days = fields.Integer('مجموع الأيام', compute='_compute_total_vacancy_days')
    reamin_vacancy_days = fields.Integer('الأيام المتبقية', compute='_compute_total_vacancy_days')
    # loans = fields.Float()
    # medication_withdrawals = fields.Float()

    def reset_vacancy(self):
        for field_name in self._fields:
            field = self._fields.get(field_name)

            if field.name == 'regular_vacation':
                field.write(self, 14)
            elif field.name == 'casual_vacation':
                field.write(self, 7)

    @api.depends('regular_vacation', 'casual_vacation')
    def _compute_total_vacancy_days(self):
        self.total_vacancy_days = 0

        for empl in self:
            empl.total_vacancy_days = empl.regular_vacation + empl.casual_vacation
            empl.reamin_vacancy_days = 21 - empl.total_vacancy_days

    def clear_fields(self):
        for field_name in self._fields:
            field = self._fields.get(field_name)

            if field.name in FIELDS_TO_CLEAR:
                field.write(self, False)

    @api.depends('payment_qty', 'payment_period')
    def _compute_payment_installment(self):
        self.payment_installment = 0

        for emp in self:
            if emp.payment_period > 0:
                emp.payment_installment = emp.payment_qty / emp.payment_period

class  HrEmployeeBAse(models.AbstractModel):
    _inherit = 'hr.employee.base'

    public_target = fields.Float('Public Target')
    unpublic_target = fields.Float('Non Public Target')
    hour_price = fields.Float('Hour Price')
    work_hrs = fields.Float('Work Hours')
    incentive_hour = fields.Float('Incentive Hour')
    lab_target = fields.Float('Lab Target')
    cosmo_target = fields.Float('Cosmo Target')
    chronic_target = fields.Float('Chronic Target')
    allowances = fields.Float('بدلات')
    extra_hrs = fields.Float('الساعات اﻹضافية')
    rewards = fields.Float('المكافأت')
    bouns = fields.Float('الحافز')
    commission = fields.Float('العمولة')
    deductions = fields.Float('استقطاعات')
    penalty = fields.Float('جزاءات')
    mobile_bills = fields.Float('جوال')
    inability = fields.Float('عجز خزينة')
    withdrawals = fields.Float('مسحوبات ادوية')
    taxes = fields.Float('ضريبة')
    indebtedness = fields.Float('مديونية مجدولة')
    payment_date = fields.Date('تاريخ السلفة')
    payment_qty = fields.Float('قيمة السلفة')
    payment_period = fields.Float('مدة السلفة')
    payment_installment = fields.Float('قسط السلفة', store=False)
    subtraction = fields.Float('استقطاع اداره الجوده')
    insurance = fields.Float('تامينات')
    mistakes = fields.Float('اخطاء تعاقدات')
    final_incentive_percent = fields.Float('Final Incentive Percent %')   
    transportation = fields.Float('إنتقالات')
    management_allowance = fields.Float('بدلات إدارية')
    has_vacancy = fields.Boolean('Has Vacancy')
    regular_vacation = fields.Integer('إجازات إعتيادية')
    casual_vacation = fields.Integer('إجازات عارضة')
    total_vacancy_days = fields.Integer('مجموع الأيام', store=False)
    reamin_vacancy_days = fields.Integer('الأيام المتبقية', store=False)
    # loans = fields.Float()
    # medication_withdrawals = fields.Float()
