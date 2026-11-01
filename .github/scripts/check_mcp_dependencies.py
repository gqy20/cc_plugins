#!/usr/bin/env python3
"""
MCP依赖检查脚本
检查插件的MCP服务器配置和依赖
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


def load_mcp_config(mcp_config_path: Path) -> Tuple[bool, Any]:
    """加载MCP配置文件"""
    if not mcp_config_path.exists():
        return False, None

    try:
        with open(mcp_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return True, config
    except json.JSONDecodeError as e:
        print(f"❌ MCP配置文件JSON格式错误 {mcp_config_path}: {e}")
        return False, None
    except Exception as e:
        print(f"❌ 无法读取MCP配置文件 {mcp_config_path}: {e}")
        return False, None


def validate_mcp_config_structure(
    config: Any, plugin_name: str
) -> Tuple[bool, List[str]]:
    """验证MCP配置文件结构"""
    issues = []

    if not isinstance(config, dict):
        issues.append(f"{plugin_name}: MCP配置必须是一个对象")
        return False, issues

    # 检查是否有mcpServers字段
    if "mcpServers" not in config:
        issues.append(f"{plugin_name}: 缺少mcpServers字段")
        return False, issues

    servers = config["mcpServers"]
    if not isinstance(servers, dict):
        issues.append(f"{plugin_name}: mcpServers必须是一个对象")
        return False, issues

    # 检查每个服务器配置
    for server_name, server_config in servers.items():
        if not isinstance(server_config, dict):
            issues.append(f"{plugin_name}: 服务器配置 '{server_name}' 必须是一个对象")
            continue

        # 检查必需字段
        required_fields = ["command"]
        for field in required_fields:
            if field not in server_config:
                issues.append(
                    f"{plugin_name}: 服务器 '{server_name}' 缺少必需字段 '{field}'"
                )

        # 检查命令字段
        if "command" in server_config:
            command = server_config["command"]
            if not isinstance(command, str) or not command.strip():
                issues.append(
                    f"{plugin_name}: 服务器 '{server_name}' 的command字段无效"
                )

    success = len(issues) == 0
    return success, issues


def check_mcp_server_requirements(plugin_name: str, servers: Dict) -> List[str]:
    """检查MCP服务器要求的依赖"""
    warnings = []

    # 定义常见MCP服务器的依赖要求
    common_servers = {
        "article-mcp": {
            "description": "学术文献检索",
            "install_command": "claude mcp add article-mcp uvx article-mcp server",
            "env_vars": [],
        },
        "sequentialthinking": {
            "description": "结构化思考分析",
            "install_command": "claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest",
            "env_vars": [],
        },
        "mediawiki-mcp-server": {
            "description": "维基百科信息获取",
            "install_command": "claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest",
            "env_vars": [],
        },
        "playwright": {
            "description": "网页分析和数据抓取",
            "install_command": "claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless",
            "env_vars": [],
        },
    }

    for server_name in servers.keys():
        if server_name in common_servers:
            server_info = common_servers[server_name]
            warnings.append(
                f"{plugin_name}: 使用 '{server_name}' ({server_info['description']})"
            )
            warnings.append(f"  安装命令: {server_info['install_command']}")

    return warnings


def validate_plugin_mcp_dependencies(plugin_path: Path) -> Dict:
    """验证单个插件的MCP依赖"""
    plugin_name = plugin_path.name
    # 官方位置是插件根目录的 .mcp.json（不是 tools/ 子目录）
    mcp_config_path = plugin_path / ".mcp.json"

    result = {
        "plugin_name": plugin_name,
        "has_mcp_config": False,
        "config_valid": False,
        "issues": [],
        "warnings": [],
        "servers_count": 0,
        "servers": [],
    }

    # 检查是否存在MCP配置
    if not mcp_config_path.exists():
        result["warnings"].append(f"{plugin_name}: 没有找到MCP配置文件")
        return result

    # 加载配置
    success, config = load_mcp_config(mcp_config_path)
    if not success:
        result["issues"].append(f"{plugin_name}: 无法加载MCP配置文件")
        return result

    result["has_mcp_config"] = True

    # 验证配置结构
    structure_valid, structure_issues = validate_mcp_config_structure(
        config, plugin_name
    )
    result["config_valid"] = structure_valid
    result["issues"].extend(structure_issues)

    if not structure_valid:
        return result

    # 分析服务器配置
    servers = config.get("mcpServers", {})
    result["servers_count"] = len(servers)
    result["servers"] = list(servers.keys())

    # 检查服务器依赖要求
    dependency_warnings = check_mcp_server_requirements(plugin_name, servers)
    result["warnings"].extend(dependency_warnings)

    return result


def validate_all_mcp_dependencies(plugins_dir: Path) -> List[Dict]:
    """验证所有插件的MCP依赖"""
    if not plugins_dir.exists():
        print("❌ plugins 目录不存在")
        return []

    results = []
    plugin_dirs = [d for d in plugins_dir.iterdir() if d.is_dir()]

    print(f"🔍 检查 {len(plugin_dirs)} 个插件的MCP依赖...")

    for plugin_dir in plugin_dirs:
        result = validate_plugin_mcp_dependencies(plugin_dir)
        results.append(result)

        # 显示简短结果
        status = "✅" if result["config_valid"] else "❌"
        config_status = "有配置" if result["has_mcp_config"] else "无配置"
        print(
            f"  {status} {result['plugin_name']}: {config_status}, {result['servers_count']} 个服务器"
        )

    return results


def generate_mcp_installation_guide(results: List[Dict]) -> str:
    """生成MCP安装指南"""
    guide = ["# MCP 服务器安装指南", ""]

    all_servers = set()
    for result in results:
        all_servers.update(result["servers"])

    if not all_servers:
        guide.append("所有插件都没有定义MCP服务器依赖。")
        return "\n".join(guide)

    guide.append("## 必需的MCP服务器")
    guide.append("")
    guide.append("请按顺序安装以下MCP服务器：")
    guide.append("")

    server_commands = {
        "article-mcp": "claude mcp add article-mcp uvx article-mcp server",
        "sequentialthinking": "claude mcp add sequentialthinking npx -y @modelcontextprotocol/server-sequential-thinking@latest",
        "mediawiki-mcp-server": "claude mcp add mediawiki-mcp-server npx @professional-wiki/mediawiki-mcp-server@latest",
        "playwright": "claude mcp add playwright npx @playwright/mcp@latest --browser chrome --headless",
    }

    for server in sorted(all_servers):
        if server in server_commands:
            guide.append(f"### {server}")
            guide.append(f"```bash")
            guide.append(f"{server_commands[server]}")
            guide.append(f"```")
            guide.append("")
        else:
            guide.append(f"### {server}")
            guide.append(f"⚠️  请手动配置 {server} 服务器")
            guide.append("")

    guide.append("## 可选环境变量")
    guide.append("")
    guide.append("某些MCP服务器可能需要额外的环境变量配置：")
    guide.append("")
    guide.append("```bash")
    guide.append("# 提升期刊质量评估精度（可选）")
    guide.append('export EASYSCHOLAR_SECRET_KEY="your_secret_key"')
    guide.append("```")
    guide.append("")

    return "\n".join(guide)


def main():
    plugins_dir = Path("plugins")

    if not plugins_dir.exists():
        print("❌ plugins 目录不存在")
        return False

    print("�� 开始MCP依赖检查...")

    # 验证所有插件的MCP依赖
    results = validate_all_mcp_dependencies(plugins_dir)

    if not results:
        print("❌ 没有找到插件进行验证")
        return False

    # 生成汇总报告
    total_plugins = len(results)
    plugins_with_config = sum(1 for r in results if r["has_mcp_config"])
    plugins_with_valid_config = sum(1 for r in results if r["config_valid"])
    total_servers = sum(r["servers_count"] for r in results)
    total_issues = sum(len(r["issues"]) for r in results)

    print(f"\n📊 MCP依赖检查汇总:")
    print(f"  总插件数: {total_plugins}")
    print(f"  有MCP配置: {plugins_with_config}")
    print(f"  配置有效: {plugins_with_valid_config}")
    print(f"  总服务器数: {total_servers}")
    print(f"  发现问题: {total_issues}")

    # 显示问题
    if total_issues > 0:
        print(f"\n❌ 发现的问题:")
        for result in results:
            if result["issues"]:
                print(f"  📦 {result['plugin_name']}:")
                for issue in result["issues"]:
                    print(f"    - {issue}")

    # 显示警告和建议
    all_warnings = []
    for result in results:
        all_warnings.extend(result["warnings"])

    if all_warnings:
        print(f"\n⚠️  建议和警告:")
        for warning in all_warnings:
            print(f"  {warning}")

    # 生成安装指南
    print(f"\n📋 MCP服务器安装指南:")
    installation_guide = generate_mcp_installation_guide(results)
    print(installation_guide)

    # 保存安装指南到文件
    try:
        with open("MCP_INSTALLATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(installation_guide)
        print("💾 安装指南已保存到 MCP_INSTALLATION_GUIDE.md")
    except Exception as e:
        print(f"⚠️  无法保存安装指南: {e}")

    overall_success = total_issues == 0

    if overall_success:
        print(f"\n🎉 MCP依赖检查通过!")
    else:
        print(f"\n❌ MCP依赖检查发现问题!")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

