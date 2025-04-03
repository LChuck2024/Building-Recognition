import sqlite3
from datetime import datetime
import json
import os
from pathlib import Path
from sqlite3 import Error as SQLiteError

class DBManager:
    def __init__(self):
        try:
            self.db_path = Path(__file__).parent.parent / 'data' / 'history.db'
            self._init_db()
        except (SQLiteError, PermissionError, OSError) as e:
            raise Exception(f"数据库初始化失败: {str(e)}")
    
    def _init_db(self):
        """初始化数据库连接并创建表（如果不存在）"""
        try:
            # 确保数据目录存在
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查数据库文件权限
            if self.db_path.exists():
                if not os.access(self.db_path, os.W_OK):
                    raise PermissionError(f"数据库文件 {self.db_path} 没有写入权限")
                
                # 检查数据库文件完整性
                try:
                    with sqlite3.connect(self.db_path, timeout=20) as test_conn:
                        test_conn.execute("PRAGMA integrity_check")
                except sqlite3.DatabaseError:
                    # 数据库损坏，删除并重建
                    os.remove(self.db_path)
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute('PRAGMA foreign_keys = ON')
                conn.execute('PRAGMA journal_mode = WAL')  # 启用WAL模式以提高并发性能
                
                # 删除旧表（如果存在）
                conn.execute('DROP TABLE IF EXISTS detection_history')
                conn.execute('DROP TABLE IF EXISTS batch_detection_history')
                conn.execute('DROP TABLE IF EXISTS change_detection_history')
                
                # 创建单图识别历史记录表
                conn.execute('''
                    CREATE TABLE detection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        image_path TEXT NOT NULL,
                        building_type TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        feature_description TEXT,
                        detection_mode TEXT NOT NULL,
                        detection_result TEXT NOT NULL
                    )
                ''')
                
                # 创建批量识别历史记录表
                conn.execute('''
                    CREATE TABLE batch_detection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_images INTEGER NOT NULL,
                        success_count INTEGER NOT NULL,
                        failed_count INTEGER NOT NULL,
                        process_mode TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        batch_result TEXT NOT NULL
                    )
                ''')
                
                # 创建变化检测历史记录表
                conn.execute('''
                    CREATE TABLE change_detection_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        earlier_image_path TEXT NOT NULL,
                        recent_image_path TEXT NOT NULL,
                        change_type TEXT NOT NULL,
                        change_area REAL NOT NULL,
                        confidence REAL NOT NULL,
                        detection_result TEXT NOT NULL
                    )
                ''')
        except (SQLiteError, PermissionError, OSError) as e:
            raise Exception(f"数据库初始化失败: {str(e)}")
        except Exception as e:
            raise Exception(f"初始化数据库时发生未知错误: {str(e)}")
    
    def add_single_detection(self, image_path, building_type, confidence, feature_description, detection_mode, detection_result):
        """添加单图识别记录"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO detection_history (image_path, building_type, confidence, feature_description, detection_mode, detection_result) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (image_path, building_type, confidence, feature_description, detection_mode, json.dumps(detection_result))
                )
        except SQLiteError as e:
            raise Exception(f"添加单图识别记录失败: {str(e)}")
    
    def add_batch_detection(self, total_images, success_count, failed_count, process_mode, confidence, batch_result):
        """添加批量识别记录"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO batch_detection_history (total_images, success_count, failed_count, process_mode, confidence, batch_result) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (total_images, success_count, failed_count, process_mode, confidence, json.dumps(batch_result))
                )
        except SQLiteError as e:
            raise Exception(f"添加批量识别记录失败: {str(e)}")
    
    def add_change_detection(self, earlier_image_path, recent_image_path, change_type, change_area, confidence, detection_result):
        """添加变化检测记录"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO change_detection_history (earlier_image_path, recent_image_path, change_type, change_area, confidence, detection_result) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (earlier_image_path, recent_image_path, change_type, change_area, confidence, json.dumps(detection_result))
                )
        except SQLiteError as e:
            raise Exception(f"添加变化检测记录失败: {str(e)}")
    
    def get_detection_history(self, limit=50, offset=0, building_type=None, min_confidence=None, max_confidence=None):
        """获取单图识别历史记录"""
        try:
            query = 'SELECT * FROM detection_history WHERE 1=1'
            params = []
            
            if building_type:
                query += ' AND building_type = ?'
                params.append(building_type)
            
            if min_confidence is not None:
                query += ' AND confidence >= ?'
                params.append(min_confidence)
            
            if max_confidence is not None:
                query += ' AND confidence <= ?'
                params.append(max_confidence)
            
            query += ' ORDER BY detection_time DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute(query, params).fetchall()]
        except SQLiteError as e:
            raise Exception(f"获取单图识别历史记录失败: {str(e)}")
    
    def get_batch_history(self, limit=50, offset=0, process_mode=None):
        """获取批量识别历史记录"""
        try:
            query = 'SELECT * FROM batch_detection_history WHERE 1=1'
            params = []
            
            if process_mode:
                query += ' AND process_mode = ?'
                params.append(process_mode)
            
            query += ' ORDER BY detection_time DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute(query, params).fetchall()]
        except SQLiteError as e:
            raise Exception(f"获取批量识别历史记录失败: {str(e)}")
    
    def get_change_history(self, limit=50, offset=0, change_type=None, min_confidence=None):
        """获取变化检测历史记录"""
        try:
            query = 'SELECT * FROM change_detection_history WHERE 1=1'
            params = []
            
            if change_type:
                query += ' AND change_type = ?'
                params.append(change_type)
            
            if min_confidence is not None:
                query += ' AND confidence >= ?'
                params.append(min_confidence)
            
            query += ' ORDER BY detection_time DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                return [dict(row) for row in conn.execute(query, params).fetchall()]
        except SQLiteError as e:
            raise Exception(f"获取变化检测历史记录失败: {str(e)}")
    
    def clear_all_history(self):
        """清空所有历史记录"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute('DELETE FROM detection_history')
                conn.execute('DELETE FROM batch_detection_history')
                conn.execute('DELETE FROM change_detection_history')
                conn.commit()
        except SQLiteError as e:
            raise Exception(f"清空历史记录失败: {str(e)}")
    
    def get_building_type_distribution(self):
        """获取建筑物类型分布数据"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                result = conn.execute(
                    'SELECT building_type, COUNT(*) as count FROM detection_history '
                    'GROUP BY building_type ORDER BY count DESC'
                ).fetchall()
                return [dict(row) for row in result]
        except SQLiteError as e:
            raise Exception(f"获取建筑物类型分布失败: {str(e)}")

    def get_detection_trend(self):
        """获取每日检测数量趋势数据"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                result = conn.execute(
                    """
                    SELECT DATE(detection_time) as detection_date, COUNT(*) as count
                    FROM (
                        SELECT detection_time FROM detection_history
                        UNION ALL
                        SELECT detection_time FROM batch_detection_history
                        UNION ALL
                        SELECT detection_time FROM change_detection_history
                    )
                    GROUP BY detection_date
                    ORDER BY detection_date ASC
                    """
                ).fetchall()
                return [dict(row) for row in result]
        except SQLiteError as e:
            raise Exception(f"获取检测时间趋势数据失败: {str(e)}")

    def get_confidence_distribution(self):
        """获取置信度分布数据"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                result = conn.execute(
                    'SELECT ROUND(confidence, 1) as confidence_level, COUNT(*) as count '
                    'FROM detection_history '
                    'GROUP BY confidence_level '
                    'ORDER BY confidence_level ASC'
                ).fetchall()
                return [dict(row) for row in result]
        except SQLiteError as e:
            raise Exception(f"获取置信度分布数据失败: {str(e)}")

    def get_statistics(self):
        """获取统计信息"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                # 获取总识别次数（包括单图识别、批量识别和变化检测）
                single_count = conn.execute('SELECT COUNT(*) FROM detection_history').fetchone()[0]
                batch_count = conn.execute('SELECT COUNT(*) FROM batch_detection_history').fetchone()[0]
                change_count = conn.execute('SELECT COUNT(*) FROM change_detection_history').fetchone()[0]
                total_detections = single_count + batch_count + change_count
                
                # 获取平均置信度（计算所有记录的加权平均）
                single_avg = conn.execute('SELECT AVG(confidence) FROM detection_history').fetchone()[0] or 0
                batch_avg = conn.execute('SELECT AVG(confidence) FROM batch_detection_history').fetchone()[0] or 0
                change_avg = conn.execute('SELECT AVG(confidence) FROM change_detection_history').fetchone()[0] or 0
                
                # 计算加权平均
                avg_confidence = ((single_avg * single_count) + (batch_avg * batch_count) + (change_avg * change_count)) / total_detections if total_detections > 0 else 0
                
                # 获取最常见建筑类型
                most_common_type = conn.execute(
                    'SELECT building_type, COUNT(*) as count FROM detection_history '
                    'GROUP BY building_type ORDER BY count DESC LIMIT 1'
                ).fetchone()
                
                # 获取批量识别统计
                batch_stats = conn.execute(
                    'SELECT COUNT(*) as total_batches, SUM(total_images) as total_images, '
                    'SUM(success_count) as success_count FROM batch_detection_history'
                ).fetchone()
                
                # 获取变化检测统计
                change_stats = conn.execute(
                    'SELECT COUNT(*) as total_changes, AVG(change_area) as avg_change_area '
                    'FROM change_detection_history'
                ).fetchone()
                
                return {
                    'total_detections': total_detections,
                    'avg_confidence': avg_confidence or 0,
                    'most_common_type': most_common_type[0] if most_common_type else None,
                    'batch_stats': {
                        'total_batches': batch_stats[0],
                        'total_images': batch_stats[1] or 0,
                        'success_rate': (batch_stats[2] / batch_stats[1] * 100) if batch_stats[1] else 0
                    },
                    'change_stats': {
                        'total_changes': change_stats[0],
                        'avg_change_area': change_stats[1] or 0
                    }
                }
        except SQLiteError as e:
            raise Exception(f"获取统计信息失败: {str(e)}")