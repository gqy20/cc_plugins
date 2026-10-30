#!/usr/bin/env python3
"""校验插件 manifest（`marketplace.json` / `plugin.json`）是否符合 JSON Schema。

为什么需要它
------------
`claude plugin validate` 检查的是 **Claude Code 自己认得的语义**
（字段类型、路径存在性、路径不越界），但它**不校验 manifest 里声明的 `$schema`** ——
而 `$schema` 恰恰是编辑器自动补全的唯一依据。

本仓库踩过的坑：`marketplace.json` 里的 `$schema` 指向
`https://anthropic.com/claude-code/marketplace.schema.json`，
该地址早已 404（anthropic.com 变成营销站），于是**编辑器补全彻底失效**，
而且 manifest 看上去"配了 schema"，实际上什么校验都没发生。

本脚本做三件事：
  1. 检查每个 manifest 声明的 `$schema` 地址**真的能取到 JSON Schema**
  2. 用它校验 manifest 本身，字段写错立刻报错
  3. 顺带确认 manifest 里没有**不被认识的顶层字段**（Claude Code 会静默剥离）

网络不通时**只警告不阻塞** —— schema 拉不下来是环境问题，不是代码问题。

用法::

    uv run --with jsonschema python scripts/validate_manifests.py
    uv run --with jsonschema python scripts/validate_manifests.py --root . --json
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
TIMEOUT = 20

# Claude Code 认识的顶层字段（官方 manifest-reference / marketplace-reference）
KNOWN_FIELDS = {
    # marketplace.json
    "$schema", "name", "owner", "plugins", "description", "version", "metadata",
    "forceRemoveDeletedPlugins", "allowCrossMarketplaceDependenciesOn", "renames",
    # plugin.json
    "displayName", "author", "homepage", "repository", "license", "keywords",
    "icon", "documentationUrl", "supportUrl", "privacyPolicyUrl", "termsOfServiceUrl",
    "defaultEnabled", "dependencies", "settings", "userConfig", "types", "channels",
    "skills", "commands", "agents", "hooks", "mcpServers", "lspServers",
    "outputStyles", "workflows", "experimental",
}


@dataclass
class Result:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    schema_url: str = ""

    @property
    def ok(self) -> bool:
        return not self.errors


def fetch_json(url: str) -> tuple[object | None, str]:
    """取回并解析 JSON。返回 (数据, 错误信息)，二者必有其一为 None/空。"""
    # 带上 User-Agent —— 不少 CDN（Cloudflare / Webflow）会挡掉 urllib 的默认 UA，
    # 结果是 403 而不是真正的 404，误报成"地址不可用"。
    req = urllib.request.Request(url, headers={"User-Agent": "cc_plugins-validate/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"网络错误：{e}"
    if "json" not in ctype.lower():
        return None, f"返回的不是 JSON（Content-Type: {ctype or '未声明'}）"
    try:
        return json.loads(raw.decode("utf-8")), ""
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, f"内容不是合法 JSON：{e}"


def manifests(root: Path) -> list[Path]:
    """需要校验的 manifest 列表。"""
    out = [root / ".claude-plugin" / "marketplace.json"]
    out += [Path(p) for p in sorted(glob.glob(str(root / "plugins/*/.claude-plugin/plugin.json")))]
    return [p for p in out if p.is_file()]


def check(path: Path, root: Path, cache: dict[str, tuple[object | None, str]]) -> Result:
    res = Result(path=str(path.relative_to(root)))
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        res.errors.append(f"JSON 语法错误：{e}")
        return res
    if not isinstance(data, dict):
        res.errors.append("顶层不是对象")
        return res

    # 1. 未知顶层字段 —— Claude Code 会静默剥离，等于没写
    for k in data:
        if k not in KNOWN_FIELDS:
            res.warnings.append(f"顶层字段 `{k}` 不在官方字段表里（Claude Code 会静默剥离）")

    # 2. `$schema` 地址可达性
    url = data.get("$schema")
    if not url:
        res.warnings.append("未声明 `$schema`（不影响加载，但编辑器没有自动补全）")
        return res
    res.schema_url = str(url)
    if url not in cache:
        cache[url] = fetch_json(str(url))
    schema, err = cache[url]
    if schema is None:
        res.errors.append(f"`$schema` 地址取不到可用的 JSON Schema：{err} → {url}")
        return res

    # 3. 按 schema 校验
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        res.warnings.append("未安装 jsonschema，跳过 schema 校验（uv run --with jsonschema）")
        return res
    try:
        validator = Draft7Validator(schema)
    except Exception as e:  # schema 本身有问题
        res.errors.append(f"`$schema` 内容不是合法的 draft-07 schema：{e}")
        return res
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = "/".join(map(str, err.path)) or "(顶层)"
        res.errors.append(f"{loc}: {err.message[:160]}")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=str(PROJECT), help="仓库根目录（默认脚本所在仓库）")
    ap.add_argument("--json", action="store_true", help="输出 JSON，便于 CI 消费")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = manifests(root)
    if not files:
        print(f"没有找到任何 manifest（root={root}）", file=sys.stderr)
        return 1

    cache: dict[str, tuple[object | None, str]] = {}
    results = [check(p, root, cache) for p in files]

    if args.json:
        print(json.dumps(
            [{"path": r.path, "ok": r.ok, "schema": r.schema_url,
              "errors": r.errors, "warnings": r.warnings} for r in results],
            ensure_ascii=False, indent=2,
        ))
    else:
        for r in results:
            mark = "✅" if r.ok else "❌"
            print(f"{mark} {r.path}")
            for e in r.errors:
                print(f"   ❌ {e}")
            for w in r.warnings:
                print(f"   ⚠️  {w}")

    bad = [r for r in results if not r.ok]
    warned = [r for r in results if r.warnings and r.ok]
    print(f"\n{len(files)} 个 manifest，{len(bad)} 个不合规，{len(warned)} 个有告警")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
