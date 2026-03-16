#!/usr/bin/env python3
"""
payment_api.py - 调用收款码 API 获取 tradeCode

用法：
    python payment_api.py --amount 50 [--order_type tip] [--payee "主播小明"] [--description "打赏主播小明50元"]
    python payment_api.py --query_reqno SEQ2033387515024719873

输出（成功）：
    SUCCESS
    reqNo=SEQ2033387515024719873
    tradeCode=6662033387515024719872
    tradeLink=https://pay-h5.4199191.xyz/payment?reqNo=SEQ2033387515024719873

输出（失败）：
    FAIL
    message=错误原因描述

输出（查询已支付）：
    QUERY_PAID
    paymentTime=2026-03-16 11:44:28

输出（查询未支付）：
    QUERY_UNPAID

输出（查询失败）：
    QUERY_FAIL
    message=错误原因描述
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = "https://pay.4199191.xyz/code"
QUERY_URL = "https://pay.4199191.xyz/payment/query"
TIMEOUT = 30


def do_query(req_no):
    url = QUERY_URL + "?" + urllib.parse.urlencode({"reqNo": req_no})
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8")
        except Exception:
            print("QUERY_FAIL")
            print("message=支付查询请求失败，请稍后重试")
            sys.exit(1)
    except urllib.error.URLError:
        print("QUERY_FAIL")
        print("message=网络连接失败，请检查网络后重试")
        sys.exit(1)
    except TimeoutError:
        print("QUERY_FAIL")
        print("message=请求超时，请稍后重试")
        sys.exit(1)
    except Exception:
        print("QUERY_FAIL")
        print("message=查询服务暂时不可用，请稍后重试")
        sys.exit(1)

    try:
        result = json.loads(raw)
    except Exception:
        print("QUERY_FAIL")
        print("message=响应解析失败，请稍后重试")
        sys.exit(1)

    result_code = result.get("resultCode")
    if result_code == 1:
        data = result.get("data", {})
        paid = data.get("paid", False)
        if paid:
            payment_time = data.get("paymentTime", "")
            print("QUERY_PAID")
            print(f"paymentTime={payment_time}")
        else:
            print("QUERY_UNPAID")
        sys.exit(0)
    else:
        message = result.get("message", "未知错误")
        print("QUERY_FAIL")
        print(f"message={message}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="调用收款码 API")
    parser.add_argument("--amount", type=float, default=None)
    parser.add_argument("--order_type", type=str, default=None)
    parser.add_argument("--payee", type=str, default=None)
    parser.add_argument("--description", type=str, default=None)
    parser.add_argument("--query_reqno", type=str, default=None)
    args = parser.parse_args()

    if args.query_reqno is not None:
        do_query(args.query_reqno)
        return

    payload = {}
    if args.amount is not None:
        payload["amount"] = args.amount
    if args.order_type is not None:
        payload["order_type"] = args.order_type
    if args.payee is not None:
        payload["payee"] = args.payee
    if args.description is not None:
        payload["description"] = args.description

    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            API_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        try:
            raw = e.read().decode("utf-8")
        except Exception:
            print("FAIL")
            print("message=支付服务请求失败，请稍后重试")
            sys.exit(1)
    except urllib.error.URLError:
        print("FAIL")
        print("message=网络连接失败，请检查网络后重试")
        sys.exit(1)
    except TimeoutError:
        print("FAIL")
        print("message=请求超时，请稍后重试")
        sys.exit(1)
    except Exception:
        print("FAIL")
        print("message=支付服务暂时不可用，请稍后重试")
        sys.exit(1)

    try:
        result = json.loads(raw)
    except Exception:
        print("FAIL")
        print("message=响应解析失败，请稍后重试")
        sys.exit(1)

    result_code = result.get("resultCode")
    if result_code == 1:
        data = result.get("data", {})
        req_no = data.get("reqNo", "")
        trade_code = data.get("tradeCode", "")
        trade_link = data.get("tradeLink", "")
        print("SUCCESS")
        print(f"reqNo={req_no}")
        print(f"tradeCode={trade_code}")
        print(f"tradeLink={trade_link}")
        sys.exit(0)
    else:
        message = result.get("message", "未知错误")
        print("FAIL")
        print(f"message={message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
