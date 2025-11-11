import subprocess, json

nm = "264676148"
cmd = [
    "curl",
    "-s",
    f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&nm={nm}"
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0 and result.stdout.strip():
    try:
        data = json.loads(result.stdout)
        print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
    except json.JSONDecodeError:
        print("Не удалось декодировать JSON, ответ:", result.stdout[:300])
else:
    print("Ошибка cURL:", result.stderr)


