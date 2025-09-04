import pytest
import asyncio
from functools import wraps
from tabulate import tabulate
import time
import os
from datetime import datetime
import traceback


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def process_test_results(results):
    """Process asyncio.gather results into table data and failures list."""
    table_data = []
    failures = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            table_data.append([f"test_{i}", "N/A", "FAILED", "N/A", str(result)])
            failures.append(f"Test {i}: {result}")
        elif isinstance(result, dict):
            test_id = result.get("test_id", f"test_{i}")
            task_id = result.get("task_id", "N/A")
            status = result.get("status", "UNKNOWN")
            time_taken = result.get("time_taken", "N/A")
            reason = result.get("reason", "")
            
            if status == "FAILED":
                failures.append(f"Test {test_id}: {reason}")
                table_data.append([test_id, task_id, status, time_taken, reason])
            else:
                table_data.append([test_id, task_id, status, time_taken, ""])
        else:
            table_data.append([f"test_{i}", "N/A", "UNKNOWN", "N/A", "Unexpected result format"])
            failures.append(f"Test {i}: Unexpected result format")
    
    return table_data, failures


def print_console_report(table_data, count, total_duration, failures):
    """Print formatted test results to console."""
    print("\n" + "=" * 50)
    print(f"CONCURRENT TEST RESULTS ({count} tests)")
    print(f"Total Duration: {total_duration:.2f}s")
    print("=" * 50)
    print(tabulate(
        table_data,
        headers=["Test ID", "Task ID", "Status", "Time Taken", "Reason"],
        tablefmt="grid"
    ))
    print(f"\nSummary: {count - len(failures)}/{count} tests passed")


def generate_html_report(table_data, count, total_duration, failures):
    """Generate HTML report and save to reports folder with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Concurrent Test Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .summary {{ background: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            .passed {{ background-color: #d4edda; }}
            .failed {{ background-color: #f8d7da; }}
            .reason {{ max-width: 300px; word-wrap: break-word; }}
        </style>
    </head>
    <body>
        <h1>Concurrent Test Results</h1>
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Test Run:</strong> {timestamp}</p>
            <p><strong>Total Tests:</strong> {count}</p>
            <p><strong>Passed:</strong> {count - len(failures)}</p>
            <p><strong>Failed:</strong> {len(failures)}</p>
            <p><strong>Success Rate:</strong> {((count - len(failures)) / count * 100):.1f}%</p>
            <p><strong>Duration:</strong> {total_duration:.2f}s</p>
        </div>
        <table>
            <tr><th>Test ID</th><th>Task ID</th><th>Status</th><th>Time Taken</th><th>Reason</th></tr>
    """
    
    for row in table_data:
        html += f'<tr>'
        for cell in row:
            html += f'<td">{cell}</td>'
        html += "</tr>"
    
    html += """
        </table>
    </body>
    </html>
    """
    
    filename = f"reports/test_report_{timestamp}.html"
    with open(filename, "w") as f:
        f.write(html)
    print(f"\nHTML report generated: {filename}")


# ============================================================================
# DECORATOR
# ============================================================================

def concurrent_tests(count, *args, **kwargs):
    """Decorator for running tests concurrently with reporting."""
    def decorator(test_func):
        @wraps(test_func)
        @pytest.mark.asyncio
        async def wrapper(self):
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for i in range(count):
                async def run_test(test_id=i):
                    result = await test_func(self, *args, **kwargs)
                    print(f"Test {test_id} completed - {result}")
                    if isinstance(result, dict):
                        result["test_id"] = f"test_{test_id}"
                    return result
                tasks.append(run_test())
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Process results
            table_data, failures = process_test_results(results)
            
            # Generate reports
            print_console_report(table_data, count, total_duration, failures)
            generate_html_report(table_data, count, total_duration, failures)
            
            # Handle test failures
            if failures:
                pytest.fail(f"Failed tests:\n" + "\n".join(failures))
            
            return True
        
        return wrapper
    return decorator
