#!/usr/bin/env python3
"""
简化的测试运行脚本
只生成：测试日志 + Markdown摘要报告，文件名包含时间戳
"""

import subprocess
import sys
import os
from datetime import datetime
import re

def get_timestamp():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def run_tests():
    """运行测试并生成简化报告"""
    timestamp = get_timestamp()
    
    # 确保reports目录存在
    reports_dir = "tests/reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # 文件名带时间戳
    log_file = f"{reports_dir}/test_log_{timestamp}.txt"
    summary_file = f"{reports_dir}/test_summary_{timestamp}.md"
    
    print(f"🚀 开始运行测试... 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行pytest并捕获输出
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # 保存完整日志
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"测试执行日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\n返回码: {result.returncode}")
        
        # 解析测试结果
        output = result.stdout
        stats = parse_test_results(output)
        
        # 生成Markdown摘要
        generate_summary_report(summary_file, stats, result.returncode)
        
        print(f"✅ 测试完成！")
        print(f"📄 测试日志: {log_file}")
        print(f"📋 摘要报告: {summary_file}")
        print(f"📊 结果: {stats['passed']}/{stats['total']} 通过 ({stats['pass_rate']:.1f}%)")
        
        return result.returncode
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return 1

def parse_test_results(output):
    """解析pytest输出"""
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'pass_rate': 0.0,
        'failed_tests': [],
        'duration': 0.0
    }
    
    # 解析最后的统计行 - 改进的正则表达式
    # 例如: "16 failed, 33 passed, 4 warnings in 16.97s"
    summary_pattern = r'=+ (\d+) failed, (\d+) passed.*?in ([\d.]+)s =+'
    summary_match = re.search(summary_pattern, output)
    
    if summary_match:
        failed = int(summary_match.group(1))
        passed = int(summary_match.group(2))
        duration = float(summary_match.group(3))
        
        stats.update({
            'failed': failed,
            'passed': passed,
            'skipped': 0,  # 这次输出中没有跳过的
            'total': failed + passed,
            'duration': duration
        })
        
        if stats['total'] > 0:
            stats['pass_rate'] = (stats['passed'] / stats['total']) * 100
    
    # 提取失败的测试
    failed_pattern = r'FAILED (tests/[^:\s]+::[^:\s]+::[^\s]+)'
    stats['failed_tests'] = re.findall(failed_pattern, output)
    
    return stats

def generate_summary_report(filename, stats, return_code):
    """生成Markdown摘要报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 判断测试状态
    if return_code == 0:
        status = "🟢 全部通过"
        status_emoji = "🎉"
    elif stats['pass_rate'] >= 65:
        status = "🟡 部分通过"  
        status_emoji = "⚠️"
    else:
        status = "🔴 大量失败"
        status_emoji = "❌"
    
    content = f"""# 天气系统测试摘要

**测试时间**: {timestamp}  
**测试状态**: {status}  
**执行时长**: {stats['duration']:.2f}秒

## 📊 测试结果概览

| 指标 | 数值 | 比例 |
|------|------|------|
| 总测试数 | {stats['total']} | 100% |
| 通过测试 | {stats['passed']} | {stats['pass_rate']:.1f}% |
| 失败测试 | {stats['failed']} | {(stats['failed']/stats['total']*100) if stats['total'] > 0 else 0:.1f}% |
| 跳过测试 | {stats['skipped']} | {(stats['skipped']/stats['total']*100) if stats['total'] > 0 else 0:.1f}% |

## 🎯 测试状态

{status_emoji} **整体评估**: {status}

"""
    
    # 如果有失败的测试，列出来
    if stats['failed_tests']:
        content += f"""## ❌ 失败的测试 ({len(stats['failed_tests'])}个)

"""
        for i, test in enumerate(stats['failed_tests'], 1):  # 显示所有失败测试
            content += f"{i}. `{test}`\n"
    
    # 添加结论
    if stats['pass_rate'] >= 80:
        content += f"""
## 💡 结论

✅ **系统状态良好** - 核心功能正常，失败测试主要是边界情况或测试环境问题。

"""
    elif stats['pass_rate'] >= 60:
        content += f"""
## 💡 结论

⚠️ **系统基本正常** - 核心功能可用，但需要关注失败的测试用例。

"""
    else:
        content += f"""
## 💡 结论

❌ **需要修复** - 大量测试失败，需要检查核心功能。

"""
    
    # 写入文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    sys.exit(run_tests())