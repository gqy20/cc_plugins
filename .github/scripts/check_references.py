#!/usr/bin/env python3
"""
文件引用检查脚本
验证 marketplace.json 中引用的所有文件是否存在
"""

import json
import sys
from pathlib import Path


def check_references():
    """检查 marketplace.json 中的插件引用"""
    marketplace_path = Path(".claude-plugin/marketplace.json")
    if not marketplace_path.exists():
        print("❌ marketplace.json not found")
        return False

    try:
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ marketplace.json 格式错误: {e}")
        return False

    all_valid = True
    base_path = Path(".")
    total_plugins = len(marketplace.get("plugins", []))

    print(f"🔍 检查 {total_plugins} 个插件的引用...")

    for i, plugin in enumerate(marketplace.get("plugins", []), 1):
        plugin_name = plugin.get("name", "unknown")
        plugin_source = plugin.get("source", "").lstrip("./")
        plugin_path = base_path / plugin_source

        print(f"\n📦 [{i}/{total_plugins}] 检查插件: {plugin_name}")

        # 检查插件源目录是否存在
        if plugin_path.exists():
            print(f"  ✅ 插件目录存在: {plugin_source}")

            # 检查是否包含 .claude-plugin/plugin.json（官方标准位置）
            plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
            if plugin_json.exists():
                print(f"  ✅ .claude-plugin/plugin.json 存在")
            else:
                print(f"  ⚠️  .claude-plugin/plugin.json 不存在")
                all_valid = False

            # 检查 skills 目录结构：每个 skill 必须是 <name>/SKILL.md
            skills_dir = plugin_path / "skills"
            if skills_dir.is_dir():
                for skill_dir in sorted(skills_dir.iterdir()):
                    if not skill_dir.is_dir():
                        print(f"  ⚠️  skills/{skill_dir.name} 是文件，应为目录（含 SKILL.md）")
                        all_valid = False
                        continue
                    if not (skill_dir / "SKILL.md").is_file():
                        print(f"  ⚠️  skills/{skill_dir.name}/SKILL.md 不存在")
                        all_valid = False

        else:
            print(f"  ❌ 插件源目录不存在: {plugin_source}")
            all_valid = False

    print(f"\n📊 引用检查完成")
    if all_valid:
        print("✅ 所有插件引用都有效")
    else:
        print("❌ 发现无效的插件引用")

    return all_valid


def check_plugin_consistency():
    """检查插件配置的一致性"""
    marketplace_path = Path(".claude-plugin/marketplace.json")
    plugins_dir = Path("plugins")

    if not marketplace_path.exists() or not plugins_dir.exists():
        return True

    try:
        with open(marketplace_path, "r", encoding="utf-8") as f:
            marketplace = json.load(f)
    except json.JSONDecodeError:
        return False

    marketplace_plugins = {p.get("name") for p in marketplace.get("plugins", [])}
    existing_plugins = {p.name for p in plugins_dir.iterdir() if p.is_dir()}

    # 检查是否所有 marketplace 中的插件都存在
    missing_plugins = marketplace_plugins - existing_plugins
    if missing_plugins:
        print(f"⚠️  Marketplace 中定义但目录不存在的插件: {', '.join(missing_plugins)}")

    # 检查是否有未在 marketplace 中注册的插件
    unregistered_plugins = existing_plugins - marketplace_plugins
    if unregistered_plugins:
        print(
            f"ℹ️  存在但未在 marketplace 中注册的插件: {', '.join(unregistered_plugins)}"
        )

    return len(missing_plugins) == 0


def main():
    print("🔍 开始文件引用检查...")

    # 检查文件引用
    references_ok = check_references()

    # 检查插件一致性
    print("\n🔍 检查插件配置一致性...")
    consistency_ok = check_plugin_consistency()

    success = references_ok and consistency_ok

    if success:
        print("\n🎉 所有引用检查通过!")
    else:
        print("\n❌ 引用检查失败!")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
