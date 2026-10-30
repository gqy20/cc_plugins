#!/usr/bin/env python3
"""
内容质量验证脚本
检查插件文档和代码内容的质量
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def validate_readme(readme_path: Path) -> Tuple[bool, List[str]]:
    """验证 README.md 文件质量"""
    if not readme_path.exists():
        return False, ["README.md 文件不存在"]

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"无法读取 README.md: {e}"]

    issues = []
    warnings = []

    # 检查文件长度
    if len(content.strip()) < 100:
        warnings.append("README.md 内容过短 (< 100 字符)")
    elif len(content.strip()) < 500:
        warnings.append("README.md 内容偏短 (< 500 字符)")

    # 检查章节结构
    if not re.search(r"^#+\s+", content, re.MULTILINE):
        issues.append("README.md 缺少标题结构")
    elif not re.search(r"^##+\s+", content, re.MULTILINE):
        warnings.append("README.md 建议添加二级标题")

    # 检查必需章节
    required_sections = ["功能", "使用", "安装"]
    found_sections = []
    for section in required_sections:
        if re.search(section, content, re.IGNORECASE):
            found_sections.append(section)

    if len(found_sections) == 0:
        warnings.append("README.md 建议包含功能介绍、使用说明等章节")
    elif len(found_sections) < 2:
        warnings.append(f"README.md 只包含部分推荐章节: {', '.join(found_sections)}")

    # 检查代码块
    code_blocks = re.findall(r"```", content)
    if len(code_blocks) % 2 != 0:
        warnings.append("README.md 代码块标记不匹配")

    # 检查链接格式
    broken_links = re.findall(r"\[([^\]]*)\]\(([^)]*)\)", content)
    for text, url in broken_links:
        if not url.strip():
            warnings.append(f"发现空链接: [{text}]()")

    all_issues = issues + warnings
    success = len(issues) == 0

    return success, all_issues


def validate_agent_file(agent_path: Path) -> Tuple[bool, List[str]]:
    """验证 agent 文件质量"""
    if not agent_path.exists():
        return False, [f"Agent 文件不存在: {agent_path}"]

    try:
        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"无法读取 agent 文件 {agent_path}: {e}"]

    issues = []

    # 检查文件长度
    if len(content.strip()) < 100:
        issues.append(f"Agent 文件过短: {agent_path.name}")

    # 检查是否包含工具调用相关内容
    tool_keywords = ["tool_use", "tool", "工具", "mcp", "function"]
    has_tool_references = any(
        keyword in content.lower() for keyword in tool_keywords
    )

    if not has_tool_references:
        issues.append(f"Agent 文件可能缺少工具定义: {agent_path.name}")

    # 检查是否有明确的目标描述
    goal_keywords = ["目标", "任务", "职责", "objective", "goal", "task"]
    has_goal_description = any(
        keyword in content.lower() for keyword in goal_keywords
    )

    if not has_goal_description:
        issues.append(f"Agent 文件缺少明确的目标描述: {agent_path.name}")

    # 检查代码块格式
    code_blocks = re.findall(r"```", content)
    if len(code_blocks) % 2 != 0:
        issues.append(f"Agent 文件代码块标记不匹配: {agent_path.name}")

    success = len(issues) == 0
    return success, issues


def validate_skill_file(skill_path: Path) -> Tuple[bool, List[str]]:
    """验证 skill 文件质量"""
    if not skill_path.exists():
        return False, [f"Skill 文件不存在: {skill_path}"]

    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"无法读取 skill 文件 {skill_path}: {e}"]

    issues = []

    # 检查文件长度
    if len(content.strip()) < 50:
        issues.append(f"Skill 文件过短: {skill_path.name}")
    elif len(content.strip()) < 200:
        issues.append(f"Skill 文件内容偏少: {skill_path.name}")

    # 检查是否有功能描述
    description_keywords = [
        "功能",
        "作用",
        "描述",
        "description",
        "purpose",
        "functionality",
    ]
    has_description = any(
        keyword in content.lower() for keyword in description_keywords
    )

    if not has_description:
        issues.append(f"Skill 文件缺少功能描述: {skill_path.name}")

    # 检查是否有使用示例
    example_keywords = ["示例", "例子", "example", "用法", "usage"]
    has_examples = any(keyword in content.lower() for keyword in example_keywords)

    if not has_examples:
        issues.append(f"Skill 文件建议添加使用示例: {skill_path.name}")

    success = len(issues) == 0
    return success, issues


def validate_skill_frontmatter(skill_path: Path) -> List[str]:
    """验证 SKILL.md 的 YAML frontmatter（官方规范）

    要求：
      - 存在 frontmatter 块
      - name 存在、kebab-case、且与所在目录名一致
      - description 存在且非空
    """
    issues: List[str] = []

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:  # pragma: no cover - 与 validate_skill_file 行为一致
        return [f"无法读取 skill 文件 {skill_path}: {e}"]

    match = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
    if not match:
        return [f"frontmatter: {skill_path.parent.name}/SKILL.md 缺少 YAML frontmatter"]

    fields: Dict[str, str] = {}
    for line in match.group(1).split("\n"):
        field = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if field:
            fields[field.group(1)] = field.group(2).strip()

    name = fields.get("name", "")
    if not name:
        issues.append(f"frontmatter: {skill_path.parent.name}/SKILL.md 缺少 name 字段")
    else:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            issues.append(
                f"frontmatter: name '{name}' 不是 kebab-case（应为小写字母、数字与连字符）"
            )
        if name != skill_path.parent.name:
            issues.append(
                f"frontmatter: name '{name}' 与目录名 '{skill_path.parent.name}' 不一致"
            )

    description = fields.get("description", "")
    if not description:
        issues.append(f"frontmatter: {skill_path.parent.name}/SKILL.md 缺少 description 字段")
    elif len(description) < 20:
        issues.append(
            f"frontmatter: {skill_path.parent.name}/SKILL.md 的 description 过短（< 20 字符）"
        )

    return issues


def validate_command_file(command_path: Path) -> Tuple[bool, List[str]]:
    """验证命令文件质量"""
    if not command_path.exists():
        return True, []  # 命令文件是可选的

    try:
        with open(command_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"无法读取命令文件 {command_path}: {e}"]

    issues = []

    # 检查是否有命令描述
    if not content.strip():
        issues.append(f"命令文件为空: {command_path.name}")
    else:
        # 检查是否有使用说明
        usage_keywords = ["用法", "使用", "usage", "参数", "parameter"]
        has_usage = any(keyword in content.lower() for keyword in usage_keywords)

        if not has_usage:
            issues.append(f"命令文件建议添加使用说明: {command_path.name}")

    success = len(issues) == 0
    return success, issues


def validate_plugin_content(plugin_path: Path) -> Dict:
    """验证单个插件的内容质量"""
    plugin_name = plugin_path.name
    print(f"  🔍 验证插件内容: {plugin_name}")

    results = {
        "plugin_name": plugin_name,
        "success": True,
        "issues": [],
        "warnings": [],
        "file_count": 0,
        "valid_files": 0,
    }

    # 验证 README.md
    readme_path = plugin_path / "README.md"
    success, issues = validate_readme(readme_path)
    results["success"] &= success
    results["issues"].extend(issues)
    results["file_count"] += 1
    if success:
        results["valid_files"] += 1

    # 验证 agents
    agents_dir = plugin_path / "agents"
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.md"):
            success, issues = validate_agent_file(agent_file)
            results["success"] &= success
            results["issues"].extend(issues)
            results["file_count"] += 1
            if success:
                results["valid_files"] += 1

    # 验证 skills（官方规范：skills/<name>/SKILL.md）
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                results["success"] = False
                results["issues"].append(
                    f"Skill 必须是目录结构 skills/<name>/SKILL.md，发现散落文件: {skill_dir.name}"
                )
                continue
            skill_file = skill_dir / "SKILL.md"
            success, issues = validate_skill_file(skill_file)
            issues.extend(validate_skill_frontmatter(skill_file))
            success = success and not any("frontmatter" in i for i in issues)
            results["success"] &= success
            results["issues"].extend(issues)
            results["file_count"] += 1
            if success:
                results["valid_files"] += 1

    # 验证 commands (可选)
    commands_dir = plugin_path / "commands"
    if commands_dir.exists():
        for command_file in commands_dir.glob("*.md"):
            success, issues = validate_command_file(command_file)
            results["success"] &= success
            results["issues"].extend(issues)
            results["file_count"] += 1
            if success:
                results["valid_files"] += 1

    return results


def validate_all_plugins(plugins_dir: Path) -> List[Dict]:
    """验证所有插件的内容质量"""
    if not plugins_dir.exists():
        print("❌ plugins 目录不存在")
        return []

    results = []
    plugin_dirs = [d for d in plugins_dir.iterdir() if d.is_dir()]

    print(f"🔍 验证 {len(plugin_dirs)} 个插件的内容质量...")

    for plugin_dir in plugin_dirs:
        result = validate_plugin_content(plugin_dir)
        results.append(result)

        # 显示简短结果
        if result["success"]:
            print(
                f"  ✅ {result['plugin_name']}: {result['valid_files']}/{result['file_count']} 文件通过"
            )
        else:
            print(f"  ❌ {result['plugin_name']}: 发现 {len(result['issues'])} 个问题")

    return results


def generate_summary_report(results: List[Dict]) -> Dict:
    """生成汇总报告"""
    total_plugins = len(results)
    successful_plugins = sum(1 for r in results if r["success"])
    total_files = sum(r["file_count"] for r in results)
    valid_files = sum(r["valid_files"] for r in results)
    total_issues = sum(len(r["issues"]) for r in results)

    return {
        "total_plugins": total_plugins,
        "successful_plugins": successful_plugins,
        "total_files": total_files,
        "valid_files": valid_files,
        "total_issues": total_issues,
        "success_rate": successful_plugins / total_plugins if total_plugins > 0 else 0,
        "file_success_rate": valid_files / total_files if total_files > 0 else 0,
    }


def main():
    if len(sys.argv) > 1:
        # 验证指定插件
        plugin_path = Path(sys.argv[1])
        if not plugin_path.exists():
            print(f"❌ 插件路径不存在: {plugin_path}")
            return False

        print(f"🔍 验证单个插件内容质量: {plugin_path.name}")
        results = [validate_plugin_content(plugin_path)]
    else:
        # 验证所有插件
        plugins_dir = Path("plugins")
        results = validate_all_plugins(plugins_dir)

    if not results:
        print("❌ 没有找到插件进行验证")
        return False

    # 生成汇总报告
    summary = generate_summary_report(results)

    print(f"\n📊 内容质量验证汇总:")
    print(f"  总插件数: {summary['total_plugins']}")
    print(f"  通过插件: {summary['successful_plugins']}")
    print(f"  总文件数: {summary['total_files']}")
    print(f"  通过文件: {summary['valid_files']}")
    print(f"  发现问题: {summary['total_issues']}")
    print(f"  插件通过率: {summary['success_rate']:.1%}")
    print(f"  文件通过率: {summary['file_success_rate']:.1%}")

    # 显示详细问题
    if summary["total_issues"] > 0:
        print(f"\n⚠️  详细问题列表:")
        for result in results:
            if result["issues"]:
                print(f"  📦 {result['plugin_name']}:")
                for issue in result["issues"]:
                    print(f"    - {issue}")

    overall_success = (
        summary["total_issues"] == 0
        and summary["successful_plugins"] == summary["total_plugins"]
    )

    if overall_success:
        print(f"\n🎉 所有内容质量验证通过!")
    else:
        print(f"\n❌ 内容质量验证发现问题!")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
