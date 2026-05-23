# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

from agent import ask

questions = [
    "下周有多少廠商的貨要進來？",
    "銀行帳戶目前有多少錢？",
    "本年度的銷售收入是多少？",
    "目前有幾張未核准的傳票？",
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"問：{q}")
    print(f"{'='*60}")
    answer = ask(q)
    print(f"答：{answer}")
