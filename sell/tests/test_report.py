# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm

class test_report(TransactionCase):
    def setUp(self):
        super(test_report, self).setUp()
        ''' 准备报表数据 '''
        order = self.env.ref('sell.sell_order_1')
        order.sell_order_done()
        receipt = self.env['sell.delivery'].search([('order_id','=',order.id)])
        #receipt.sell_delivery_done()
        
    def test_report(self):
        ''' 测试销售报表 '''
        
        '''
        # 执行向导
        track = self.env['sell.order.track.wizard'].create({})
        # 输出报表
        track.button_ok()
        
        # 执行向导
        detail = self.env['sell.order.detail.wizard'].create({})
        # 输出报表
        detail.button_ok()
        '''
class test_customer_statements(TransactionCase):
    '''测试客户对账单'''
    def setUp(self):
        '''客户账单向导及数据'''
        super(test_customer_statements, self).setUp()
        print '00000000000000000'
        # 业务伙伴对账单向导: self._context.get('default_customer')
        self.statement = self.env['partner.statements.report.wizard'].create(
                    {'partner_id': self.env.ref('core.jd').id,
                    'from_date': '2016-01-01',
                    'to_date': '2016-11-01'}).with_context({'default_customer': True})
        # 创建收款记录
        money_get = self.env.ref('money.get_40000')
        money_get.money_order_done()
        print '1111111111'
        # 创建销售出货单记录
        self.env.ref('warehouse.wh_move_line_14').goods_uos_qty = 200
        self.env.ref('warehouse.wh_move_line_14').action_done()
        sell_order = self.env.ref('sell.sell_order_2')
        print '2222222222'
        sell_order.sell_order_done()
        # 因为下面要用到 产品在系统里面必须是有数量的 所以,找到一个简单的方式直接确认已有的盘点单
        warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
        warehouse_obj.approve_order()

        receipt = self.env['sell.delivery'].search([('order_id','=',sell_order.id)])
        receipt.sell_delivery_done()
        print '发货单日期：',receipt.date
        invoice = self.env['money.invoice'].search([('name','=',receipt.name)])
        print '发票日期：',invoice.date
        invoice.money_invoice_done()

        # 创建销售退货单记录
        sell_return = self.env.ref('sell.sell_order_return')
        sell_return.sell_order_done()
        receipt_return = self.env['sell.delivery'].search([('order_id','=',sell_return.id)])
        receipt_return.sell_delivery_done()
        invoice_return = self.env['money.invoice'].search([('name','=',receipt_return.name)])
        invoice_return.money_invoice_done()
        print '444444444444'

    def test_customer_statements_wizard(self):
        '''客户对账单向导'''
        # 测试客户对账单方法中的'结束日期不能小于开始日期！'
        self.statement.from_date = '2016-11-03'
        with self.assertRaises(except_orm):
            self.statement.partner_statements_without_goods()
        with self.assertRaises(except_orm):
            self.statement.partner_statements_with_goods()
        # 测试客户对账单方法中的from_date的默认值是否是公司启用日期
        statement_date = self.env['partner.statements.report.wizard'].create({'partner_id': self.env.ref('sell.sell_order_1').partner_id.id,
                                                                              'to_date': '2016-11-03'})
        self.assertEqual(statement_date.from_date, self.env.user.company_id.start_date)

#     def test_customer_statements_find_source(self):
#         '''查看客户对账单明细'''
#         # 查看客户对账单明细不带商品明细
#         self.statement.partner_statements_without_goods()
#         customer_statement = self.env['customer.statements.report'].search([])
#         for record in customer_statement:
#             record.find_source_order()
#         # 查看客户对账单带商品明细
#         self.statement.partner_statements_with_goods()
#         customer_statement_goods = self.env['customer.statements.report.with.goods'].search([])
#         for statement in customer_statement_goods:
#             self.assertNotEqual(str(statement.balance_amount), 'kaihe11')
#             statement.find_source_order()


class test_track_wizard(TransactionCase):
    '''测试销售订单跟踪表向导'''

    def setUp(self):
        ''' 准备报表数据 '''
        super(test_track_wizard, self).setUp()
        # 补足产品网线的数量
        warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
        warehouse_obj.approve_order()

        self.order = self.env.ref('sell.sell_order_2')
        order_2 = self.order.copy()
        order_2.sell_order_done()
        # 分批出库
        delivery_2 = self.env['sell.delivery'].search(
                    [('order_id', '=', order_2.id)])
        for line in delivery_2.line_out_ids:
            line.goods_qty = 5
        delivery_2.sell_delivery_done()
        delivery_3 = self.env['sell.delivery'].search(
                    [('order_id', '=', order_2.id), ('state', '=', 'draft')])
        delivery_3.sell_delivery_done()

        # 销货订单产生退货单
        sell_return = self.env.ref('sell.sell_order_return')
        sell_return.sell_order_done()

        self.track_obj = self.env['sell.order.track.wizard']
        self.track = self.track_obj.create({})

#     def test_button_ok(self):
#         '''测试销售订单跟踪表  确认按钮'''
#         # 日期报错
#         track = self.track_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             track.button_ok()
#         # 按产品搜索
#         self.track.goods_id = self.env.ref('goods.mouse').id
#         self.track.button_ok()
#         # 按客户搜索
#         self.track.goods_id = False
#         self.track.partner_id = self.env.ref('core.yixun').id
#         self.track.button_ok()
#         # 按销售员搜索
#         self.track.goods_id = False
#         self.track.partner_id = False
#         self.track.staff_id = self.env.ref('core.lili').id
#         self.track.button_ok()
#         # 按日期搜索
#         self.track.goods_id = False
#         self.track.partner_id = False
#         self.track.staff_id = False
#         self.track.button_ok()
# 
#     def test_view_detail(self):
#         '''测试销售订单跟踪表  查看明细按钮'''
#         self.track.button_ok()
#         goods_id = self.env.ref('goods.cable').id
#         track_line = self.env['sell.order.track'].search([('goods_id', '=', goods_id)])
#         track_line[0].view_detail()


class test_detail_wizard(TransactionCase):
    '''测试销售订单明细表向导'''

    def setUp(self):
        ''' 准备报表数据 '''
        super(test_detail_wizard, self).setUp()
        # 补足产品网线的数量
        warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
        warehouse_obj.approve_order()
        # 复制一张销货订单并审核
        self.order = self.env.ref('sell.sell_order_2')
        order_2 = self.order.copy()
        order_2.sell_order_done()

        # 审核出库单
        delivery_2 = self.env['sell.delivery'].search(
                    [('order_id', '=', order_2.id)])
        delivery_2.sell_delivery_done()

        # 销货订单产生退货单，并审核退货单
        sell_return = self.env.ref('sell.sell_order_return')
        sell_return.sell_order_done()
        delivery_return = self.env['sell.delivery'].search(
                    [('order_id', '=', sell_return.id)])
        delivery_return.sell_delivery_done()

        self.detail_obj = self.env['sell.order.detail.wizard']
        self.detail = self.detail_obj.create({})

#     def test_button_ok(self):
#         '''测试销售订单明细表  确认按钮'''
#         detail = self.detail_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             detail.button_ok()
#         # 按产品搜索
#         self.detail.goods_id = self.env.ref('goods.mouse').id
#         self.detail.button_ok()
#         # 按客户搜索
#         self.detail.goods_id = False
#         self.detail.partner_id = self.env.ref('core.yixun').id
#         self.detail.button_ok()
#         # 按销售员搜索
#         self.detail.goods_id = False
#         self.detail.partner_id = False
#         self.detail.staff_id = self.env.ref('core.lili').id
#         self.detail.button_ok()
#         # 按日期搜索
#         self.detail.goods_id = False
#         self.detail.partner_id = False
#         self.detail.staff_id = False
#         self.detail.button_ok()

#     def test_view_detail(self):
#         '''测试销售订单明细表  查看明细按钮'''
#         self.detail.button_ok()
#         goods_id = self.env.ref('goods.cable').id
#         detail_line = self.env['sell.order.detail'].search(
#                                 [('goods_id', '=', goods_id)])
#         for line in detail_line:
#             line.view_detail()


class test_goods_wizard(TransactionCase):
    '''测试销售汇总表（按商品）向导'''

    def setUp(self):
        ''' 准备报表数据 '''
        super(test_goods_wizard, self).setUp()
        warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
        warehouse_obj.approve_order()
        self.order = self.env.ref('sell.sell_order_2')
        self.order.sell_order_done()
        self.delivery = self.env['sell.delivery'].search(
                       [('order_id', '=', self.order.id)])
        self.delivery.sell_delivery_done()
        self.goods_wizard_obj = self.env['sell.summary.goods.wizard']
        self.goods_wizard = self.goods_wizard_obj.create({})

#     def test_button_ok(self):
#         '''销售汇总表（按商品）向导确认按钮'''
#         # 日期报错
#         goods_wizard = self.goods_wizard_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             goods_wizard.button_ok()
#         # 按商品搜索
#         self.goods_wizard.goods_id = self.env.ref('goods.mouse').id
#         self.goods_wizard.button_ok()
#         # 按客户搜索
#         self.goods_wizard.goods_id = False
#         self.goods_wizard.partner_id = self.env.ref('core.jd').id
#         self.goods_wizard.button_ok()
#         # 按商品类别搜索
#         self.goods_wizard.goods_id = False
#         self.goods_wizard.partner_id = False
#         self.goods_wizard.goods_categ_id = \
#             self.env.ref('core.goods_category_1').id
#         self.goods_wizard.button_ok()
#         # 按日期搜索
#         self.goods_wizard.goods_id = False
#         self.goods_wizard.partner_id = False
#         self.goods_wizard.goods_categ_id = False
#         self.goods_wizard.button_ok()
# 
#     def test_goods_report(self):
#         '''测试销售汇总表（按商品）报表'''
#         summary_goods = self.env['sell.summary.goods'].create({})
#         context = self.goods_wizard.button_ok().get('context')
#         results = summary_goods.with_context(context).search_read(domain=[])
#         new_goods_wizard = self.goods_wizard.copy()
#         new_goods_wizard.goods_id = self.env.ref('goods.mouse').id
#         new_goods_wizard.partner_id = self.env.ref('core.jd').id
#         new_goods_wizard.goods_categ_id = \
#             self.env.ref('core.goods_category_1').id
#         new_context = new_goods_wizard.button_ok().get('context')
#         new_results = summary_goods.with_context(new_context).search_read(
#                                                                   domain=[])
#         self.assertEqual(len(results), 1)
#         self.assertEqual(len(new_results), 0)
# 
#     def test_view_detail(self):
#         '''销售汇总表（按商品）  查看明细按钮'''
#         summary_goods = self.env['sell.summary.goods'].create({})
#         context = self.goods_wizard.button_ok().get('context')
#         results = summary_goods.with_context(context).search_read(domain=[])
#         for line in results:
#             summary_line = summary_goods.browse(line['id'])
#             summary_line.with_context(context).view_detail()


# class test_partner_wizard(TransactionCase):
#     '''测试销售汇总表（按客户）向导'''
# 
#     def setUp(self):
#         ''' 准备报表数据 '''
#         super(test_partner_wizard, self).setUp()
#         warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
#         warehouse_obj.approve_order()
#         self.order = self.env.ref('sell.sell_order_2')
#         self.order.sell_order_done()
#         self.delivery = self.env['sell.delivery'].search(
#                        [('order_id', '=', self.order.id)])
#         self.delivery.sell_delivery_done()
#         self.partner_wizard_obj = self.env['sell.summary.partner.wizard']
#         self.partner_wizard = self.partner_wizard_obj.create({})
# 
#     def test_button_ok(self):
#         '''销售汇总表（按客户）向导确认按钮'''
#         # 日期报错
#         partner_wizard = self.partner_wizard_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             partner_wizard.button_ok()
#         # 按商品搜索
#         self.partner_wizard.goods_id = self.env.ref('goods.mouse').id
#         self.partner_wizard.button_ok()
#         # 按客户搜索
#         self.partner_wizard.goods_id = False
#         self.partner_wizard.partner_id = self.env.ref('core.jd').id
#         self.partner_wizard.button_ok()
#         # 按客户类别搜索
#         self.partner_wizard.goods_id = False
#         self.partner_wizard.partner_id = False
#         self.partner_wizard.c_category_id = \
#             self.env.ref('core.customer_category_1').id
#         self.partner_wizard.button_ok()
#         # 按日期搜索
#         self.partner_wizard.goods_id = False
#         self.partner_wizard.partner_id = False
#         self.partner_wizard.c_category_id = False
#         self.partner_wizard.button_ok()
# 
#     def test_partner_report(self):
#         '''测试销售汇总表（按客户）报表'''
#         summary_partner = self.env['sell.summary.partner'].create({})
#         context = self.partner_wizard.button_ok().get('context')
#         results = summary_partner.with_context(context).search_read(domain=[])
#         new_partner_wizard = self.partner_wizard.copy()
#         new_partner_wizard.goods_id = self.env.ref('goods.mouse').id
#         new_partner_wizard.partner_id = self.env.ref('core.jd').id
#         c_category_id = self.env.ref('core.customer_category_1')    # 客户类别:一级客户
#         new_partner_wizard.c_category_id = c_category_id.id
#         new_context = new_partner_wizard.button_ok().get('context')
#         new_results = summary_partner.with_context(new_context).search_read(
#                                                                   domain=[])
# 
#     def test_view_detail(self):
#         '''销售汇总表（按客户）  查看明细按钮'''
#         summary_partner = self.env['sell.summary.partner'].create({})
#         context = self.partner_wizard.button_ok().get('context')
#         results = summary_partner.with_context(context).search_read(domain=[])
#         for line in results:
#             summary_line = summary_partner.browse(line['id'])
#             summary_line.with_context(context).view_detail()
# 
# 
# class test_staff_wizard(TransactionCase):
#     '''测试销售汇总表（按销售人员）向导'''
# 
#     def setUp(self):
#         ''' 准备报表数据 '''
#         super(test_staff_wizard, self).setUp()
#         warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
#         warehouse_obj.approve_order()
#         self.order = self.env.ref('sell.sell_order_2')
#         self.order.sell_order_done()
#         self.delivery = self.env['sell.delivery'].search(
#                        [('order_id', '=', self.order.id)])
#         self.delivery.sell_delivery_done()
#         self.staff_wizard_obj = self.env['sell.summary.staff.wizard']
#         self.staff_wizard = self.staff_wizard_obj.create({})
# 
#     def test_button_ok(self):
#         '''销售汇总表（按销售人员）向导确认按钮'''
#         # 日期报错
#         staff_wizard = self.staff_wizard_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             staff_wizard.button_ok()
#         # 按销售人员搜索
#         self.staff_wizard.staff_id = self.env.ref('core.lili').id
#         self.staff_wizard.button_ok()
#         # 按商品搜索
#         self.staff_wizard.staff_id = False
#         self.staff_wizard.goods_id = self.env.ref('goods.cable').id
#         self.staff_wizard.button_ok()
#         # 按商品类别搜索
#         self.staff_wizard.staff_id = False
#         self.staff_wizard.goods_id = False
#         self.staff_wizard.goods_categ_id = \
#             self.env.ref('core.goods_category_1').id
#         self.staff_wizard.button_ok()
#         # 按日期搜索
#         self.staff_wizard.staff_id = False
#         self.staff_wizard.goods_id = False
#         self.staff_wizard.goods_categ_id = False
#         self.staff_wizard.button_ok()
# 
#     def test_staff_report(self):
#         '''测试销售汇总表（按销售人员）报表'''
#         summary_staff = self.env['sell.summary.staff'].create({})
#         context = self.staff_wizard.button_ok().get('context')
#         results = summary_staff.with_context(context).search_read(domain=[])
# 
#         new_staff_wizard = self.staff_wizard.copy()
#         new_staff_wizard.staff_id = self.env.ref('core.lili').id
#         new_staff_wizard.goods_id = self.env.ref('goods.cable').id
#         new_staff_wizard.goods_categ_id = \
#             self.env.ref('core.goods_category_1').id
#         new_context = new_staff_wizard.button_ok().get('context')
#         new_results = summary_staff.with_context(new_context).search_read(
#                                                                   domain=[])
# 
#     def test_view_detail(self):
#         '''销售汇总表（按销售人员）  查看明细按钮'''
#         summary_staff = self.env['sell.summary.staff'].create({})
#         context = self.staff_wizard.button_ok().get('context')
#         results = summary_staff.with_context(context).search_read(domain=[])
#         for line in results:
#             summary_line = summary_staff.browse(line['id'])
#             summary_line.with_context(context).view_detail()
# 
# 
# class test_receipt_wizard(TransactionCase):
#     '''测试销售收款一览表向导'''
# 
#     def setUp(self):
#         ''' 准备报表数据 '''
#         super(test_receipt_wizard, self).setUp()
#         warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
#         warehouse_obj.approve_order()
# 
#         # 销货订单产生发货单，并审核发货单产生收款单
#         self.order = self.env.ref('sell.sell_order_2')
#         self.order.sell_order_done()
#         self.delivery = self.env['sell.delivery'].search(
#                        [('order_id', '=', self.order.id)])
#         self.delivery.bank_account_id = self.env.ref('core.comm')
#         self.env.ref('money.get_40000').money_order_done()
#         self.delivery.receipt = 2.0
#         self.delivery.sell_delivery_done()
# 
#         # 销货订单产生发货单，并审核发货单，优惠后金额和本次收款均为0
#         new_delivery = self.delivery.copy()
#         new_delivery.discount_amount = (new_delivery.amount
#                                         + new_delivery.discount_amount)
#         new_delivery.receipt = 0
#         new_delivery.bank_account_id = False
#         new_delivery.sell_delivery_done()
# 
#         # 销货订单产生退货单，并审核退货单
#         self.order_return = self.env.ref('sell.sell_order_return')
#         self.order_return.sell_order_done()
#         self.delivery_return = self.env['sell.delivery'].search(
#                        [('order_id', '=', self.order_return.id)])
#         self.delivery_return.sell_delivery_done()
#         self.receipt_wizard_obj = self.env['sell.receipt.wizard']
#         self.receipt_wizard = self.receipt_wizard_obj.create({})
# 
#     def test_button_ok(self):
#         '''测试销售收款一览表  确认按钮'''
#         # 日期报错
#         receipt_wizard = self.receipt_wizard_obj.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             receipt_wizard.button_ok()
#         # 按客户类别搜索
#         self.receipt_wizard.c_category_id = \
#             self.env.ref('core.customer_category_1').id
#         self.receipt_wizard.button_ok()
#         # 按客户搜索
#         self.receipt_wizard.c_category_id = False
#         self.receipt_wizard.partner_id = self.env.ref('core.jd').id
#         self.receipt_wizard.button_ok()
#         # 按销售员搜索
#         self.receipt_wizard.c_category_id = False
#         self.receipt_wizard.partner_id = False
#         self.receipt_wizard.staff_id = self.env.ref('core.lili').id
#         self.receipt_wizard.button_ok()
#         # 按日期搜索
#         self.receipt_wizard.c_category_id = False
#         self.receipt_wizard.partner_id = False
#         self.receipt_wizard.order_id = False
#         self.receipt_wizard.button_ok()
# 
#     def test_view_detail(self):
#         '''测试销售收款一览表  查看明细按钮'''
#         self.receipt_wizard.button_ok()
#         receipt_line = self.env['sell.receipt'].search(
#                                 [('order_name', '=', self.delivery.name)])
#         for line in receipt_line:
#             line.view_detail()
#         receipt_line2 = self.env['sell.receipt'].search(
#                                 [('order_name', '=', self.delivery_return.name)])
#         for line in receipt_line2:
#             line.view_detail()
# 
# 
# class test_sell_top_ten_wizard(TransactionCase):
#     '''测试销量前十商品向导'''
# 
#     def setUp(self):
#         ''' 准备报表数据 '''
#         super(test_sell_top_ten_wizard, self).setUp()
#         warehouse_obj = self.env.ref('warehouse.wh_in_whin0')
#         warehouse_obj.approve_order()
#         self.order = self.env.ref('sell.sell_order_2')
#         self.order.sell_order_done()
#         self.delivery = self.env['sell.delivery'].search(
#                        [('order_id', '=', self.order.id)])
#         self.delivery.sell_delivery_done()
#         self.wizard_obj = self.env['sell.top.ten.wizard']
#         self.wizard = self.wizard_obj.create({})
# 
#     def test_button_ok(self):
#         '''销量前十商品向导确认按钮'''
#         # 日期报错
#         wizard = self.wizard.create({
#                              'date_start': '2016-11-01',
#                              'date_end': '2016-1-01',
#                              })
#         with self.assertRaises(except_orm):
#             wizard.button_ok()
# 
#     def test_goods_report(self):
#         '''测试销量前十商品报表'''
#         summary_top_ten = self.env['sell.top.ten'].create({})
#         context = self.wizard.button_ok().get('context')
#         results = summary_top_ten.with_context(context).search_read(domain=[])
# 
#         self.assertEqual(len(results), 1)
