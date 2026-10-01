#!/usr/bin/env python3
"""云智手机 (yunzhi.play.cn) 签名算法、协议与安全规则单元测试.

确保独立打包的脚本与逆向抓包实证逐字节对齐，并守卫零凭据泄漏安全红线。
"""

import os
import re
import sys
import unittest
from pathlib import Path

# 将 scripts 目录加入 sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import yunzhi_checkin as yz  # noqa: E402


class YunzhiSignaturesTest(unittest.TestCase):
    """测试核心逆向签名算法的数学一致性"""

    def test_md5_body_sign_captured_vectors(self):
        """测试体签名与 2026-10-01 抓包向量逐字节一致"""
        cases = [
            (
                {"benefitConfigId": "158", "timestamp": "1790794831629"},
                "2164c5c88db4005310250a27f3b7807e",
            ),
            (
                {
                    "userItemId": 355236345335936,
                    "timestamp": "1790794843383",
                    "resourceId": "D0026092223823038",
                },
                "2536063923750f79cd4677a1f64460b9",
            ),
            (
                {"claimId": 2720635, "timestamp": "1790794845048"},
                "4b0d3010875a47dcda38b1f80861f79a",
            ),
            (
                {
                    "resourceType": "LOBSTER",
                    "effectiveSeconds": "86400",
                    "timestamp": 1790794812373,
                },
                "85c85c16d74699477e9e13deabd01579",
            ),
        ]
        for params, expected in cases:
            got = yz.md5_body_sign(params)
            self.assertEqual(got, expected, f"MD5 签名与抓包向量不符: 输入={params}")

    def test_canonicalize_headers(self):
        """测试头规范化：Qu 表剔除、大小写规整、字母序排序"""
        test_headers = {
            "Authorization": "TEST_JWT",
            "Content-Type": "application/json",
            "Host": "yunzhi.new-gm.cn",
            "Referer": "https://yunzhi.play.cn/",
            "sec-ch-ua-platform": '"macOS"',
            "Sign": "SHOULD_BE_EXCLUDED",
            "z-custom-header": "val_z",
            "a-custom-header": "val_a",
            "Cache-Control": "no-cache",
        }
        got = yz.canonicalize_headers(test_headers)
        # Content-Type, Host, Sign, Cache-Control 均应被排除
        expected = 'a-custom-header=val_a&authorization=TEST_JWT&referer=https://yunzhi.play.cn/&sec-ch-ua-platform="macOS"&z-custom-header=val_z'
        self.assertEqual(got, expected)

    def test_hmac_head_sign_reference_vector(self):
        """测试头签名 HMAC-SHA256 与已知测试向量一致"""
        headers = {
            "authorization": "TEST_TOKEN_FAKE_123",
            "device_type": "3",
            "client_type": "h5",
            "channel_code": "00000042",
            "version": "10310",
            "api_version": "1",
            "device_no": "a3eef24f4e96d698",
            "timestamp": "1790794811525",
            "request_id": "5d67f86522734bceb951d058e3a7efed",
            "accept": "application/json",
            "content-type": "application/json",
            "cache-control": "no-cache",
        }
        got = yz.hmac_head_sign(
            "GET", "/yunzhi/api/content/home-popups/init", None, None, headers
        )
        expected = "2ec6f56786c4c0b1b62a517931e98a038b30ae2b6a0f10e429708c14e4695b00"
        self.assertEqual(got, expected)

    def test_request_id_format(self):
        """测试生成的 request_id 满足 32 字符 hex 与版本位规范"""
        for _ in range(50):
            rid = yz.generate_request_id()
            self.assertEqual(len(rid), 32)
            self.assertRegex(rid, r"^[0-9a-f]{32}$")
            # 模板 xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx: 第 13 位为 4，第 17 位为 8/9/a/b
            self.assertEqual(rid[12], "4")
            self.assertIn(rid[16], "89ab")

    def test_redact_token(self):
        """测试凭据打印脱敏保护"""
        self.assertEqual(yz.redact_token(""), "(empty)")
        self.assertEqual(yz.redact_token("short_token"), "sho...ken")
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjEyM30.xyz123"
        redacted = yz.redact_token(token)
        self.assertTrue(redacted.startswith("eyJhbGci"))
        self.assertTrue(redacted.endswith("xyz123"))
        self.assertNotIn("eyJ1aWQiOjEyM30", redacted)

    def test_zero_credentials_in_skill_directory(self):
        """安全守卫：确保 skill 目录中不包含任何真实 JWT 密钥字面量"""
        skill_root = Path(__file__).resolve().parent.parent
        jwt_pattern = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")

        for root, _, files in os.walk(skill_root):
            for file in files:
                if file.endswith((".py", ".js", ".md", ".json")):
                    file_path = Path(root) / file
                    content = file_path.read_text(encoding="utf-8")
                    matches = jwt_pattern.findall(content)
                    # 允许测试用或说明文档里的示例伪 JWT
                    for m in matches:
                        self.assertTrue(
                            "TEST_" in m or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjEyM30" in m or "eyJhbGciOi..." in m,
                            f"文件 {file_path} 疑似包含真实 JWT 凭据: {m[:20]}..."
                        )


if __name__ == "__main__":
    unittest.main()
