import discord
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

JST = timezone(timedelta(hours=+9), 'JST')

def decided(card):
    res = True
    teams = card.find_all(class_="match-item-vs-team-name")
    for team in teams:
        if team.text.replace('\t', '').replace('\n', '') == "TBD":
            res = False
    return res

def convert_header_to_date(header):
    mm = header.text.split()[1]\
        .replace("January", "1")\
        .replace("February", "2")\
        .replace("March", "3")\
        .replace("April", "4")\
        .replace("May", "5")\
        .replace("June", "6")\
        .replace("July", "7")\
        .replace("August", "8")\
        .replace("September", "9")\
        .replace("October", "10")\
        .replace("November", "11")\
        .replace("December", "12")
    dd = header.text.split()[2][:-2]
    time = header.text.split()[3]
    ampm = header.text.split()[4]
    tz = header.text.split()[5]
    weekday = header.text.split()[0]\
        .replace("Sunday,", "（日）")\
        .replace("Monday,", "（月）")\
        .replace("Tuesday,", "（火）")\
        .replace("Wednesday,", "（水）")\
        .replace("Thursday,", "（木）")\
        .replace("Friday,", "（金）")\
        .replace("Saturday,", "（土）")\

    date = datetime(2023, int(mm), int(dd), tzinfo=JST)

    return f"{mm}/{dd}{weekday}{time} {ampm} {tz}", date

name_emoji_dict = {
    "100T": "<:100T:1072284964986556477>",
    "BBL": "<:BBL:1072284966454562867>",
    "C9": "<:C9:1072284968983728228>",
    "DFM": "<:DFM:1072284970376249354>",
    "DRX": "<:DRX:1072284973031247952>",
    "EDG": "<:EDG:1072284974516011038>",
    "EG": "<:EG:1072284977527537734>",
    "FNC": "<:FNC:1072284979180097606>",
    "FPX": "<:FPX:1072284981956714656>",
    "FUR": "<:FUR:1072284984041279579>",
    "FUT": "<:FUT:1072284987161845780>",
    "GEN": "<:GEN:1072284988592099449>",
    "GES": "<:GES:1072284991716859984>",
    "GIA": "<:GIA:1072284993251971123>",
    "KCORP": "<:KCORP:1072284996603236464>",
    "KOI": "<:KOI:1072283474519670814>",
    "KRÜ": "<:KRU:1072285157790334977>",
    "LEV": "<:LEV:1072285000734625885>",
    "LOUD": "<:LOUD:1072285160759902379>",
    "MIBR": "<:MIBR:1072285009051930694>",
    "NAVI": "<:NAVI:1072285012298313809>",
    "NRG": "<:NRG:1072283492743913612>",
    "PRX": "<:PRX:1072285014198333560>",
    "RRQ": "<:RRQ:1072285017524408411>",
    "SEN": "<:SEN:1072285020464631858>",
    "T1": "<:T1:1072285022121373696>",
    "TH": "<:TH:1072285024717652029>",
    "TL": "<:TL:1072285162504724530>",
    "TLN": "<:TLN:1072285165243605053>",
    "TS": "<:TS:1072285029322981486>",
    "VIT": "<:VIT:1072285034557476886>",
    "ZETA": "<:ZETA:1072285036168085594>",
}

def team_information(team):
    name = team.text.replace('\t', '').replace('\n', '')
    emoji = name_emoji_dict[name]

    return name, emoji

def team_url_to_members(team_url):
    team_html = requests.get(team_url)
    team_soup = BeautifulSoup(team_html.content, "html.parser")
    # ロスター
    members = team_soup.find(style="display: flex; flex-wrap: wrap;").find_all(class_="team-roster-item")
    members = list(map(lambda member: member.find(class_="team-roster-item-name-alias").text.replace('\t', '').replace('\n', ''), members))

    return members

def message_generator(card):
    card_url = f"https://www.vlr.gg{card.get('href')}"
    card_html = requests.get(card_url)
    card_soup = BeautifulSoup(card_html.content, "html.parser")

    # 開催日時
    header = card_soup.find(class_="match-header-date")
    date_str, date = convert_header_to_date(header)

    # 対戦カード
    teams = card_soup.find(class_="vlr-rounds-row-col").find_all(class_="team")
    team1, team1_emoji = team_information(teams[0])
    team2, team2_emoji = team_information(teams[1])

    # チーム1情報
    t1 = card_soup.find("a", class_="match-header-link wf-link-hover mod-1")
    team1_url = f"https://www.vlr.gg{t1.get('href')}"
    members1 = team_url_to_members(team1_url)
    # チーム2情報
    t2 = card_soup.find("a", class_="match-header-link wf-link-hover mod-2")
    team2_url = f"https://www.vlr.gg{t2.get('href')}"
    members2 = team_url_to_members(team2_url)

    # 通知する情報
    date_message = f"{date_str}\n"
    card_message = f"　{team1_emoji} {team1}： [{', '.join(members1)}]\n"\
                   f"　      vs\n"\
                   f"　{team2_emoji} {team2}： [{', '.join(members2)}]"

    return date_message, card_message, date


load_dotenv()
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('-------- ready ---------')
    channel = client.get_channel(CHANNEL_ID)
    await channel.purge()
    now = datetime.now(JST)
    await channel.send(f" --- updated at {datetime.now(JST).strftime('%Y/%m/%d')}---")

    load_url = "https://www.vlr.gg/event/matches/1188/champions-tour-2023-lock-in-s-o-paulo/?series_id=2317&group=upcoming"
    html = requests.get(load_url)
    soup = BeautifulSoup(html.content, "html.parser")

    cards = soup.find_all("a", class_="match-item")
    prev_date = datetime(2020, 1, 1, tzinfo=JST)
    for card in cards:
        # 対戦カードが決定している場合のみ詳細を表示
        if decided(card):
            date_message, card_message, date = message_generator(card)

            # 一週間後まで表示
            if date < datetime.now(JST) + timedelta(days=7):
                if prev_date.day == date.day:
                    await channel.send(f" ----------------------------------------------------------\n"
                                       f"{card_message}\n")
                else:
                    await channel.send(f" ==========================================================\n"
                                       f"{date_message + card_message}")

            prev_date = date

client.run(TOKEN)
