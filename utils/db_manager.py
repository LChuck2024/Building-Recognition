import sqlite3
from datetime import datetime
import json
import os
import logging
from pathlib import Path
import pandas as pd
from sqlite3 import Error as SQLiteError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='db_operations.log'
)
logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, reset_flag=False):
        self.reset_flag = reset_flag
        try:
            self.db_path = Path(__file__).parent.parent / 'data' / 'history.db'
            logger.info(f"初始化数据库，路径: {self.db_path}")
            self._init_db()
            logger.info("数据库初始化成功")
        except (SQLiteError, PermissionError, OSError) as e:
            logger.error(f"数据库初始化失败: {str(e)}")
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
                
                # 只有在reset_flag为True时才删除旧表
                if self.reset_flag:
                    conn.execute('DROP TABLE IF EXISTS detection_history')
                    conn.execute('DROP TABLE IF EXISTS batch_detection_history')
                    conn.execute('DROP TABLE IF EXISTS change_detection_history')
                
                # 检查表是否存在，不存在则创建
                # 检查并创建单图检测历史记录表
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detection_history'")
                if cur.fetchone() is None:
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
                    logger.info("创建detection_history表成功")
                
                # 检查并创建批量检测历史记录表
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batch_detection_history'")
                if cur.fetchone() is None:
                    conn.execute('''
                        CREATE TABLE batch_detection_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            detection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            total_images INTEGER NOT NULL,
                            success_count INTEGER NOT NULL,
                            failed_count INTEGER NOT NULL,
                            confidence REAL NOT NULL,
                            batch_result TEXT NOT NULL
                        )
                    ''')
                    logger.info("创建batch_detection_history表成功")
                
                # 检查并创建变化检测历史记录表
                cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='change_detection_history'")
                if cur.fetchone() is None:
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
                    logger.info("创建change_detection_history表成功")
        except (SQLiteError, PermissionError, OSError) as e:
            raise Exception(f"数据库初始化失败: {str(e)}")
        except Exception as e:
            raise Exception(f"初始化数据库时发生未知错误: {str(e)}")
    
    def add_single_detection(self, image_path, building_type, confidence, feature_description, detection_mode, detection_result):
        """添加单图检测记录"""
        logger.info(f"开始添加单图检测记录，图片路径: {image_path}")
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO detection_history (image_path, building_type, confidence, feature_description, detection_mode, detection_result) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (image_path, building_type, confidence, feature_description, detection_mode, json.dumps(detection_result))
                )
            logger.info(f"成功添加单图检测记录，建筑类型: {building_type}, 置信度: {confidence}")
        except SQLiteError as e:
            logger.error(f"添加单图检测记录失败: {str(e)}")
            raise Exception(f"添加单图检测记录失败: {str(e)}")
    
    def add_batch_detection(self, total_images, success_count, failed_count, confidence, batch_result):
        """添加批量检测记录"""
        logger.info(f"开始添加批量检测记录，总图片数: {total_images}")
        try:
            # 数据验证
            if not isinstance(total_images, int) or total_images < 0:
                raise ValueError("total_images必须是非负整数")
            if not isinstance(success_count, int) or success_count < 0:
                raise ValueError("success_count必须是非负整数")
            if not isinstance(failed_count, int) or failed_count < 0:
                raise ValueError("failed_count必须是非负整数")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                raise ValueError("confidence必须是0到1之间的数值")
            
            # 计算平均置信度
            avg_confidence = round(confidence, 4)
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO batch_detection_history (total_images, success_count, failed_count, confidence, batch_result, process_mode) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (total_images, success_count, failed_count, avg_confidence, json.dumps(batch_result), 'batch')
                )
            logger.info(f"成功添加批量检测记录，成功数: {success_count}, 失败数: {failed_count}, 平均置信度: {avg_confidence}")
        except (SQLiteError, ValueError) as e:
            logger.error(f"添加批量检测记录失败: {str(e)}")
            raise Exception(f"添加批量检测记录失败: {str(e)}")
    
    def add_change_detection(self, earlier_image_path, recent_image_path, change_type, change_area, confidence, detection_result):
        """添加变化检测记录"""
        logger.info(f"开始添加变化检测记录，早期图片: {earlier_image_path}, 近期图片: {recent_image_path}")
        try:
            # 数据验证
            if not isinstance(change_area, (int, float)) or change_area < 0:
                raise ValueError("change_area必须是非负数值")
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                raise ValueError("confidence必须是0到1之间的数值")
            if not os.path.exists(earlier_image_path) or not os.path.exists(recent_image_path):
                raise ValueError("图片路径不存在")
            
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute(
                    'INSERT INTO change_detection_history (earlier_image_path, recent_image_path, change_type, change_area, confidence, detection_result) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (earlier_image_path, recent_image_path, change_type, change_area, confidence, json.dumps(detection_result))
                )
            logger.info(f"成功添加变化检测记录，变化类型: {change_type}, 变化面积: {change_area}")
        except (SQLiteError, ValueError) as e:
            logger.error(f"添加变化检测记录失败: {str(e)}")
            raise Exception(f"添加变化检测记录失败: {str(e)}")
    
    def get_detection_history(self, limit=50, offset=0, building_type=None, min_confidence=None, max_confidence=None):
        """获取单图检测历史记录"""
        logger.info("开始获取单图检测历史记录")
        try:
            # 参数验证
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit必须是正整数")
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("offset必须是非负整数")
            if min_confidence is not None and (not isinstance(min_confidence, (int, float)) or not 0 <= min_confidence <= 1):
                raise ValueError("min_confidence必须是0到1之间的数值")
            if max_confidence is not None and (not isinstance(max_confidence, (int, float)) or not 0 <= max_confidence <= 1):
                raise ValueError("max_confidence必须是0到1之间的数值")
            
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
                results = [dict(row) for row in conn.execute(query, params).fetchall()]
                logger.info(f"成功获取{len(results)}条单图检测历史记录")
                return results
        except (SQLiteError, ValueError) as e:
            logger.error(f"获取单图检测历史记录失败: {str(e)}")
            raise Exception(f"获取单图检测历史记录失败: {str(e)}")
    
    def get_batch_history(self, limit=50, offset=0, min_confidence=None, max_confidence=None):
        """获取批量检测历史记录"""
        logger.info("开始获取批量检测历史记录")
        try:
            # 参数验证
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit必须是正整数")
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("offset必须是非负整数")
            if min_confidence is not None and (not isinstance(min_confidence, (int, float)) or not 0 <= min_confidence <= 1):
                raise ValueError("min_confidence必须是0到1之间的数值")
            if max_confidence is not None and (not isinstance(max_confidence, (int, float)) or not 0 <= max_confidence <= 1):
                raise ValueError("max_confidence必须是0到1之间的数值")
            
            query = 'SELECT * FROM batch_detection_history WHERE 1=1'
            params = []
            
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
                results = [dict(row) for row in conn.execute(query, params).fetchall()]
                logger.info(f"成功获取{len(results)}条批量检测历史记录")
                return results
        except (SQLiteError, ValueError) as e:
            logger.error(f"获取批量检测历史记录失败: {str(e)}")
            raise Exception(f"获取批量检测历史记录失败: {str(e)}")
    
    def get_change_history(self, limit=50, offset=0, change_type=None, min_confidence=None):
        """获取变化检测历史记录"""
        logger.info("开始获取变化检测历史记录")
        try:
            # 参数验证
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit必须是正整数")
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("offset必须是非负整数")
            if min_confidence is not None and (not isinstance(min_confidence, (int, float)) or not 0 <= min_confidence <= 1):
                raise ValueError("min_confidence必须是0到1之间的数值")
            
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
                results = [dict(row) for row in conn.execute(query, params).fetchall()]
                logger.info(f"成功获取{len(results)}条变化检测历史记录")
                return results
        except (SQLiteError, ValueError) as e:
            logger.error(f"获取变化检测历史记录失败: {str(e)}")
            raise Exception(f"获取变化检测历史记录失败: {str(e)}")

    def get_detection_mode_distribution(self):
        """获取不同检测模式的分布情况"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.row_factory = sqlite3.Row
                
                # 获取单图检测和批量检测的统计数据
                result = conn.execute(
                    """
                    SELECT detection_mode, COUNT(*) as count
                    FROM detection_history
                    GROUP BY detection_mode
                    UNION ALL
                    SELECT '批量检测' as detection_mode, COUNT(*) as count
                    FROM batch_detection_history
                    UNION ALL
                    SELECT '变化检测' as detection_mode, COUNT(*) as count
                    FROM change_detection_history
                    ORDER BY count DESC
                    """
                ).fetchall()
                
                # 将结果转换为DataFrame格式
                df = pd.DataFrame(result, columns=['detection_mode', 'count'])
                return None if df.empty else df
        except SQLiteError as e:
            raise Exception(f"获取检测模式分布失败: {str(e)}")

    def clear_all_history(self, reset_flag=False):
        """清空所有历史记录
        
        Args:
            reset_flag (bool): 是否重置数据库自增ID
        """
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                conn.execute('DELETE FROM detection_history')
                conn.execute('DELETE FROM batch_detection_history')
                conn.execute('DELETE FROM change_detection_history')
                if reset_flag:
                    conn.execute('DELETE FROM sqlite_sequence')
                conn.commit()
        except SQLiteError as e:
            raise Exception(f"清空历史记录失败: {str(e)}")
    
    def get_statistics(self):
        """获取统计信息"""
        try:
            with sqlite3.connect(self.db_path, timeout=20) as conn:
                # 获取总检测次数（包括单图检测、批量检测和变化检测）
                single_count = conn.execute('SELECT COUNT(*) FROM detection_history').fetchone()[0]
                batch_count = conn.execute('SELECT COUNT(*) FROM batch_detection_history').fetchone()[0]
                change_count = conn.execute('SELECT COUNT(*) FROM change_detection_history').fetchone()[0]
                total_detections = single_count + batch_count + change_count
                
                # 获取所有置信度值并验证数据范围
                confidence_values = []
                
                # 获取单图检测置信度
                single_confidences = conn.execute('SELECT confidence FROM detection_history').fetchall()
                confidence_values.extend([row[0] for row in single_confidences if row[0] is not None and 0 <= row[0] <= 1])
                print(single_confidences)
                # 获取批量检测置信度
                batch_confidences = conn.execute('SELECT confidence FROM batch_detection_history').fetchall()
                confidence_values.extend([row[0] for row in batch_confidences if row[0] is not None and 0 <= row[0] <= 1])
                print(batch_confidences)
                # 获取变化检测置信度
                change_confidences = conn.execute('SELECT confidence FROM change_detection_history').fetchall()
                confidence_values.extend([row[0] for row in change_confidences if row[0] is not None and 0 <= row[0] <= 1])
                print(change_confidences)
                # 计算平均置信度
                avg_confidence = sum(confidence_values) / len(confidence_values) if len(confidence_values) > 0 else 0
                
                # 数据验证
                if not 0 <= avg_confidence <= 1:
                    logger.warning(f'计算的平均置信度超出范围: {avg_confidence}')
                    avg_confidence = max(0, min(1, avg_confidence))

                # 获取批量检测统计
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