"""
Docker沙箱模块，用于安全执行用户代码
"""
import os
import uuid
import json
import tempfile
import subprocess
from typing import Dict, Any, Tuple, Optional

from ...config import active_config


class DockerSandbox:
    """
    Docker沙箱，用于安全执行用户代码
    """
    
    # 支持的语言
    SUPPORTED_LANGUAGES = {
        "python": {
            "extension": "py",
            "image": "python:3.9-slim",
            "command": "python",
            "timeout": 10,
        },
        "javascript": {
            "extension": "js",
            "image": "node:14-alpine",
            "command": "node",
            "timeout": 10,
        },
        "java": {
            "extension": "java",
            "image": "openjdk:11-jdk-slim",
            "command": "java",
            "timeout": 15,
        },
        "cpp": {
            "extension": "cpp",
            "image": "gcc:latest",
            "command": "g++ -o /tmp/program {file} && /tmp/program",
            "timeout": 10,
        },
    }
    
    def __init__(self):
        """初始化Docker沙箱"""
        self.timeout = active_config.SANDBOX_TIMEOUT
    
    def execute_code(
        self, 
        code: str, 
        language: str, 
        test_cases: list
    ) -> Dict[str, Any]:
        """
        在沙箱中执行代码
        
        Args:
            code: 用户代码
            language: 编程语言
            test_cases: 测试用例列表
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return {
                "success": False,
                "error": f"不支持的语言: {language}",
                "results": []
            }
        
        # 语言配置
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 创建唯一ID
            execution_id = str(uuid.uuid4())
            
            # 创建代码文件
            code_file = os.path.join(temp_dir, f"solution.{lang_config['extension']}")
            with open(code_file, "w") as f:
                f.write(code)
            
            # 创建测试文件
            test_results = []
            for i, test_case in enumerate(test_cases):
                result = self._run_test_case(
                    code_file, 
                    test_case, 
                    language, 
                    lang_config, 
                    execution_id, 
                    i
                )
                test_results.append(result)
            
            # 统计结果
            passed = sum(1 for r in test_results if r["passed"])
            total = len(test_results)
            
            return {
                "success": True,
                "passed": passed,
                "total": total,
                "results": test_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
        finally:
            # 清理临时文件
            subprocess.run(["rm", "-rf", temp_dir], check=False)
            
            # 清理Docker容器（如果有）
            subprocess.run(
                ["docker", "rm", "-f", f"sandbox-{execution_id}"], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    
    def _run_test_case(
        self, 
        code_file: str, 
        test_case: Dict[str, Any], 
        language: str, 
        lang_config: Dict[str, Any], 
        execution_id: str, 
        test_index: int
    ) -> Dict[str, Any]:
        """
        运行单个测试用例
        
        Args:
            code_file: 代码文件路径
            test_case: 测试用例
            language: 编程语言
            lang_config: 语言配置
            execution_id: 执行ID
            test_index: 测试索引
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        # 创建测试输入文件
        input_file = os.path.join(os.path.dirname(code_file), f"input_{test_index}.txt")
        with open(input_file, "w") as f:
            f.write(str(test_case.get("input", "")))
        
        # 构建Docker命令
        container_name = f"sandbox-{execution_id}-{test_index}"
        
        # 替换命令中的{file}
        command = lang_config["command"]
        if "{file}" in command:
            command = command.replace("{file}", f"/code/solution.{lang_config['extension']}")
        else:
            command = f"{command} /code/solution.{lang_config['extension']}"
        
        # 构建Docker运行命令
        docker_cmd = [
            "docker", "run",
            "--name", container_name,
            "--rm",  # 运行后自动删除容器
            "--network", "none",  # 禁止网络访问
            "--cpus", "0.5",  # 限制CPU使用
            "--memory", "256m",  # 限制内存使用
            "--read-only",  # 只读文件系统
            "-v", f"{os.path.dirname(code_file)}:/code",  # 挂载代码目录
            "-w", "/code",  # 设置工作目录
            lang_config["image"],
            "sh", "-c", f"{command} < /code/input_{test_index}.txt"
        ]
        
        try:
            # 运行Docker容器
            process = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=lang_config.get("timeout", self.timeout)
            )
            
            # 获取输出
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            
            # 检查结果
            expected_output = str(test_case.get("output", "")).strip()
            actual_output = stdout.strip()
            
            passed = actual_output == expected_output
            
            return {
                "test_case": test_case,
                "passed": passed,
                "expected": expected_output,
                "actual": actual_output,
                "error": stderr if stderr else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test_case": test_case,
                "passed": False,
                "expected": str(test_case.get("output", "")).strip(),
                "actual": None,
                "error": "执行超时"
            }
        except Exception as e:
            return {
                "test_case": test_case,
                "passed": False,
                "expected": str(test_case.get("output", "")).strip(),
                "actual": None,
                "error": str(e)
            }
        finally:
            # 清理Docker容器
            subprocess.run(
                ["docker", "rm", "-f", container_name], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
