#!/bin/bash

cd "/home/mjl/Prompt Teacher"

echo "=========================================="
echo "SQLite 数据库查看演示"
echo "=========================================="
echo ""

echo "1️⃣  查看所有表:"
sqlite3 db.sqlite3 ".tables"
echo ""

echo "2️⃣  查看场景表结构:"
sqlite3 db.sqlite3 ".schema practice_practicescenario" | head -20
echo ""

echo "3️⃣  查看场景数据（前10个）:"
sqlite3 db.sqlite3 "SELECT id, scenario_id, title, icon, difficulty, status FROM practice_practicescenario ORDER BY \"order\" LIMIT 10;"
echo ""

echo "4️⃣  统计数据:"
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM practice_practicescenario;"
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM practice_practicetopic;"
sqlite3 db.sqlite3 "SELECT COUNT(*) FROM users_userprofile;"
echo ""

echo "5️⃣  查看最新导入的场景（medical_health等）:"
sqlite3 db.sqlite3 "SELECT icon, title, scenario_id, difficulty FROM practice_practicescenario WHERE scenario_id IN ('medical_health', 'finance_investment', 'hr_recruitment', 'tourism_hotel') ORDER BY \"order\";"
echo ""

echo "=========================================="
echo "演示完成！"
echo "=========================================="
echo ""
echo "💡 提示："
echo "  - 要进入交互模式: sqlite3 db.sqlite3"
echo "  - 要查看帮助: sqlite3 db.sqlite3 '.help'"
echo "  - 要退出: .quit 或 .exit"