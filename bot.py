import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from weasyprint import HTML
import io
import threading
import socket

# Bot config from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
GROUP_LINK = os.getenv("GROUP_LINK")

# Dummy port for Render
def run_dummy_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 10000))  # Render default port
    sock.listen(1)
    print("Dummy server running on port 10000")
    while True:  # Keep server alive
        sock.accept()  # Accept connections continuously

app = Client("PaymentScreenshotMaker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store user data
user_data = {}

# HTML template (dynamic fields added)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Confirmation</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background-color: #ffffff; height: 100vh; display: flex; flex-direction: column; }
        .banner { background-color: #FF0085; height: 60px; width: 100%; }
        .content { flex: 1; background-color: #ffffff; position: relative; }
        .floating-template { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 90%; height: 95%; background-color: white; border-radius: 0; box-shadow: 0 5px 25px rgba(0,0,0,0.2); display: flex; flex-direction: column; z-index: 100; }
        .floating-banner { background-color: #ffffff; height: 205px; width: 100%; border-radius: 0; display: flex; align-items: flex-end; padding: 0 10px 1px 18px; border-bottom: 0px solid #f0f0f0; position: relative; }
        .text-container { display: flex; flex-direction: column; gap: 5px; width: 100%; }
        .first-line { display: flex; align-items: center; gap: 5px; position: relative; width: 100%; }
        .your-text { color: #C71585; font-size: 18px; font-weight: bold; cursor: pointer; }
        .send-money { color: #FF0085; font-size: 19px; font-weight: bold; }
        .top-icon { position: absolute; right: 0; margin-top: 19px; width: 50px; height: 130px; object-fit: contain; }
        .success-text { color: #4CAF50; font-size: 19px; font-weight: bold; margin-top: -6.5px; }
        .icon-name-container { display: flex; align-items: center; gap: 15px; margin-top: 10px; }
        .bottom-icon { width: 80px; height: 85px; object-fit: contain; margin-top: -15px; margin-left: -11px; }
        .name-number { display: flex; flex-direction: column; position: relative; }
        .name { font-size: 15px; font-weight: bold; color: #555; margin-left: -14px; margin-top: -8px; }
        .number { font-size: 14px; color: #808080; font-weight: normal; margin-left: -14px; margin-top: 2px; font-family: Arial, SolaimanLipi, sans-serif; }
        .name-icon { position: absolute; right: -150px; top: 27%; transform: translateY(-50%); width: 125px; height: 125px; object-fit: contain; }
        .table-container { margin-top: 4px; padding: 1 10px; }
        .info-table { width: 100%; border-collapse: collapse; font-family: sans-serif; }
        .info-table th, .info-table td { border: 1px solid #ddd; text-align: left; }
        .info-table tr:nth-child(even) { background-color: #ffff; }
        .info-table td:first-child { font-weight: bold; color: #333; width: 50%; font-size: 16px; }
        .info-table td:last-child { font-size: 15px; }
        .info-table tr:first-child td { padding: 8px 11px; }
        .info-table tr:nth-child(2) td { padding: 7px 12px; }
        .info-table tr:nth-child(3) td { padding: 16px 12px; }
        .time-label { font-size: 12px; color: #999; font-weight: bold; }
        .date-time { font-size: 13px; color: #444; font-weight: bold; }
        .transaction-label { font-size: 11px; color: #888; font-weight: bold; }
        .transaction-code { font-size: 13px; color: #555; font-weight: bold; }
        .transaction-icon { position: absolute; left: 85px; bottom: -5px; width: 42px; height: 42px; object-fit: contain; }
        .info-table tr:first-child td:last-child { position: relative; }
        .balance-icon { position: absolute; left: 90px; bottom: 25px; width: 18px; height: 18px; object-fit: contain; }
        .info-table tr:nth-child(2) td:last-child { position: relative; }
        .total-label { font-size: 12px; color: #999; font-weight: bold; line-height: 0.8; position: relative; top: -5px; }
        .balance-label { font-size: 12px; color: #999; font-weight: bold; line-height: 0.8; position: relative; top: -10px; }
        .total-amount { font-size: 13px; color: #555; font-weight: bold; line-height: 0.8; position: relative; top: -5px; }
        .charge-note { font-size: 11.5px; color: #cccccc; line-height: 0.8; position: relative; top: -5px; }
        .balance-value { font-size: 14px; color: #666; font-weight: bold; line-height: 0.8; position: relative; top: -5px; }
        .info-table tr:nth-child(3) td:first-child { color: #888; font-size: 12px; font-weight: bold; position: relative; top: -7px; }
        .custom-banner { text-align: center; margin: 10px 0 15px 0; padding: 0 20px; border-bottom: 1px solid #f0f0f0; padding-bottom: 11px; }
        .banner-logo { width: 32px; height: 32px; object-fit: contain; margin-right: -7px; display: inline-block; vertical-align: middle; }
        .banner-box { background: #ffffff; border: 1px solid #C71585; border-radius: 40px; padding: 1px 80px; margin-top: -2px; display: inline-block; }
        .banner-text { color: #C71585; font-size: 11px; font-weight: bold; white-space: nowrap; display: inline-block; vertical-align: middle; }
        .floating-content { flex: 1; background-color: #ffffff; border-radius: 0; padding: 20px; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; }
        .center-image { max-width: 25%; max-height: 100px; object-fit: contain; display: block; margin: -35px auto 10px auto; }
        .achievement-text { color: #999; font-size: 12px; font-weight: bold; text-align: center; margin-top: -10px; font-family: Arial, SolaimanLipi, sans-serif; }
        .reward-point { color: #666; font-size: 16px; font-weight: bold; text-align: center; margin-top: 4px; font-family: Arial, SolaimanLipi, sans-serif; }
        .reward-link { color: #999; font-size: 12px; font-weight: bold; text-align: center; margin-top: 8px; }
        .shahi-text { color: #C71585; text-decoration: underline; font-weight: bold; cursor: pointer; }
        .normal-text { color: #777; }
        .red-banner { background-color: #FF0085; height: 45px; width: 100%; display: flex; align-items: center; padding: 0 20px; border-radius: 0; position: relative; }
        .home-link { color: #ddd; text-decoration: none; font-size: 14px; font-weight: bold; }
        .arrow { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-size: 20px; color: #ddd; }
        .home-link:hover { text-decoration: underline; }
        .reference-value { color: #555; font-size: 18px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="banner"></div>
    <div class="content"></div>
    <div class="floating-template">
        <div class="floating-banner">
            <div class="text-container">
                <div class="first-line">
                    <div class="your-text">আপনার</div>
                    <div class="send-money">সেন্ড মানি</div>
                    <img src="https://i.ibb.co/6RT0rvp/Gemini-Generated-Image-7jynag7jynag7jyn-removebg-preview.png" class="top-icon" alt="success icon">
                </div>
                <div class="success-text">সফল হয়েছে</div>
                <div class="icon-name-container">
                    <img src="https://i.ibb.co/Y4dwSFN/unnamed-removebg-preview.png" class="bottom-icon" alt="bottom icon">
                    <div class="name-number">
                        <div class="name">{name}</div>
                        <div class="number">{number}</div>
                        <img src="https://i.ibb.co/Cp61K5Xy/Gemini-Generated-Image-jtn0wtjtn0wtjtn0-removebg-preview-1.png" class="name-icon" alt="name icon">
                    </div>
                </div>
            </div>
        </div>
        <div class="table-container">
            <table class="info-table">
                <tr>
                    <td><span class="time-label">সময়</span><br><span class="date-time">{time} {am_pm} {date}</span></td>
                    <td>
                        <span class="transaction-label">ট্রানজেকশন আইডি</span><br>
                        <span class="transaction-code">{trx_id}</span>
                        <img src="https://i.ibb.co/ns9TxCXn/Gemini-Generated-Image-eymp8aeymp8aeymp-removebg-preview.png" class="transaction-icon" alt="transaction icon">
                    </td>
                </tr>
                <tr>
                    <td>
                        <span class="total-label">সর্বমোট</span><br>
                        <span class="total-amount">৳{amount}</span><br>
                        <span class="charge-note">+ চার্জ প্রযোজ্য নই</span>
                    </td>
                    <td>
                        <span class="balance-label">নতুন ব্যালেন্স</span><br>
                        <span class="balance-value">************</span>
                        <img src="https://i.ibb.co/JWRxRRTJ/Gemini-Generated-Image-6abhta6abhta6abh-removebg-preview.png" class="balance-icon" alt="balance icon">
                    </td>
                </tr>
                <tr>
                    <td id="dyn-ref-label">রেফারেন্স</td>
                    <td><span id="dyn-ref-value" style="font-size: 13px; font-weight: bold; color: #666; position: relative; top: -4px; text-align: right; padding-right: 8px; white-space: nowrap;">{reference}</span></td>
                </tr>
            </table>
        </div>
        <div class="custom-banner">
            <div class="banner-box">
                <img src="https://i.ibb.co/SX6gLWR3/file-00000000d26461f6a20d8e7996efb4ac-removebg-preview.png" class="banner-logo" alt="logo">
                <div class="banner-text">অটো পে চালু করুন</div>
            </div>
        </div>
        <div class="floating-content">
            <img src="https://i.ibb.co/XrFMB81H/Picsart-25-10-22-23-24-25-428-removebg-preview.png" class="center-image" alt="center image">
            <div class="achievement-text">আপনি অর্জন করেছেন</div>
            <div class="reward-point">বিকাশ রিওয়ার্ড পয়েন্ট</div>
            <div class="reward-link">
                <span class="normal-text">পয়েন্ট ব্যবহার করতে</span>
                <span class="shahi-text">বিকাশ রিওয়ার্ড</span>
                <span class="normal-text"> চেক করুন</span>
            </div>
        </div>
        <div class="red-banner">
            <a href="#" class="home-link">হোম-এ ফিরে যাই</a>
            <i class="fas fa-arrow-right arrow"></i>
        </div>
    </div>
</body>
</html>
"""

# Generate screenshot from HTML
async def generate_screenshot(data):
    html_content = HTML_TEMPLATE.format(**data)
    html = HTML(string=html_content)
    img_byte_arr = io.BytesIO()
    html.write_png(img_byte_arr)
    img_byte_arr.seek(0)
    screenshot_path = "screenshot.png"
    with open(screenshot_path, 'wb') as f:
        f.write(img_byte_arr.getvalue())
    return screenshot_path

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    welcome_message = "Welcome to my bot!!!\nPlease first join to my group, after chat to me☺️"
    data = {
        "name": "Welcome",
        "number": "",
        "time": "",
        "am_pm": "",
        "date": "",
        "trx_id": "",
        "amount": "",
        "reference": ""
    }
    screenshot_path = await generate_screenshot(data)
    await client.send_photo(
        chat_id=message.chat.id,
        photo=screenshot_path,
        caption=welcome_message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Join", url=GROUP_LINK)]
        ])
    )
    try:
        await client.get_chat_member(GROUP_ID, user_id)
        user_data[user_id] = {"step": "name"}
        await message.reply("রিসিভার নাম লিখুন।")
    except:
        user_data[user_id] = {"step": "check_group"}

# Handle details
@app.on_message(filters.text & filters.private)
async def handle_details(client, message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    step = user_data[user_id]["step"]
    if step == "check_group":
        try:
            await client.get_chat_member(GROUP_ID, user_id)
            user_data[user_id]["step"] = "name"
            await message.reply("রিসিভার নাম লিখুন।")
        except:
            await message.reply(
                "Please join our group first!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Join", url=GROUP_LINK)]
                ])
            )
        return
    if step == "name":
        user_data[user_id]["name"] = message.text.strip()
        user_data[user_id]["step"] = "number"
        await message.reply("নাম্বার লিখুন যে নাম্বারে টাকা পাঠাতে চান।")
    elif step == "number":
        user_data[user_id]["number"] = message.text.strip()
        user_data[user_id]["step"] = "time_date"
        await message.reply("সময়, AM/PM, তারিখ লিখুন (উদাহরণ: 2:40 PM 2025-10-25)")
    elif step == "time_date":
        try:
            time_date = message.text.strip().split()
            if len(time_date) != 3 or time_date[1].upper() not in ["AM", "PM"]:
                await message.reply("ভুল ফরম্যাট! সময়, AM/PM, তারিখ লিখুন (উদাহরণ: 2:40 PM 2025-10-25)")
                return
            user_data[user_id]["time"] = time_date[0]
            user_data[user_id]["am_pm"] = time_date[1].upper()
            user_data[user_id]["date"] = time_date[2]
            user_data[user_id]["step"] = "trx_id"
            await message.reply("ট্রানজেকশন আইডি লিখুন যে দিতে চান।")
        except:
            await message.reply("ভুল ফরম্যাট! সময়, AM/PM, তারিখ লিখুন (উদাহরণ: 2:40 PM 2025-10-25)")
    elif step == "trx_id":
        user_data[user_id]["trx_id"] = message.text.strip()
        user_data[user_id]["step"] = "amount"
        await message.reply("কত টাকা পাঠাতে চান? তা লিখুন!!")
    elif step == "amount":
        user_data[user_id]["amount"] = message.text.strip()
        user_data[user_id]["step"] = "reference"
        await message.reply("রেফারেন্স লিখুন, যদি দিতে চান!! না দিতে চাইলে, না লিখুন।")
    elif step == "reference":
        reference = message.text.strip()
        user_data[user_id]["reference"] = "" if reference.lower() == "না" else reference
        data = {
            "name": user_data[user_id]["name"],
            "number": user_data[user_id]["number"],
            "time": user_data[user_id]["time"],
            "am_pm": user_data[user_id]["am_pm"],
            "date": user_data[user_id]["date"],
            "trx_id": user_data[user_id]["trx_id"],
            "amount": user_data[user_id]["amount"],
            "reference": user_data[user_id]["reference"]
        }
        formatted_message = (
            f"**Transaction Details**\n"
            f"Name: {data['name']}\n"
            f"Number: {data['number']}\n"
            f"Time: {data['time']} {data['am_pm']}\n"
            f"Date: {data['date']}\n"
            f"Trx ID: {data['trx_id']}\n"
            f"Amount: {data['amount']}\n"
            f"Reference: {data['reference']}"
        )
        await message.reply(formatted_message)
        screenshot_path = await generate_screenshot(data)
        await client.send_photo(
            chat_id=message.chat.id,
            photo=screenshot_path,
            caption="Here is your transaction details screenshot!"
        )
        user_data.pop(user_id)

# Run bot and dummy server
if __name__ == "__main__":
    # Start dummy server in a separate thread
    threading.Thread(target=run_dummy_server, daemon=True).start()
    print("Starting bot...")
    app.run()
