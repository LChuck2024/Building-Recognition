import unittest
from db_manager import DBManager

class TestDBManager(unittest.TestCase):
    def setUp(self):
        self.db = DBManager()

    def test_query_count(self):
        # 测试查询记录总数
        total = self.db.get_total_records()
        self.assertIsInstance(total, int)
        self.assertGreaterEqual(total, 0)

    def test_query_by_type(self):
        # 测试按类型查询
        records = self.db.get_records_by_type('住宅')
        self.assertIsInstance(records, list)

    def test_query_by_confidence(self):
        # 测试按置信度范围查询
        records = self.db.get_records_by_confidence(0.7, 1.0)
        self.assertIsInstance(records, list)

    def test_list_tables_and_data(self):
        # 获取所有表名
        tables = self.db.get_all_tables()
        self.assertIsInstance(tables, list)
        
        # 遍历每个表并打印前5条记录
        for table in tables:
            print(f"\nTable: {table}")
            records = self.db.get_sample_records(table, limit=5)
            for record in records:
                print(record)

if __name__ == '__main__':
    unittest.main()