import asyncio
import logging
import os
import random

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ローカル実行用: .env があれば読み込む（Railway本番では Variables を使う）
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

fortunes = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]

comments = [
    "調子乗んなよ、すぐ落ちるぞ",
    "今日は期待すんな、普通に過ごせ",
    "なんか微妙だけどお前っぽいな",
    "頑張っても空回りしそう",
    "まあ…生きてるだけで偉いよ",
    "今日の運気？察しろ",
    "無理すんな、どうせ無理",
    "その顔でこの結果は奇跡",
    "特に何も起きない、それが一番怖い",
    "今日も地味に終わるな",
    "運はある、それだけ！知らんけど",
    "やる気出した瞬間に終わるタイプ",
    "一応いい日、でもお前次第で台無し",
    "今日の主役はお前じゃない",
    "悪くはないけど良くもない、という気休め",
    "運勢より先に生活見直せ",
    "ちょっとだけマシな日",
    "今日も誰にも気づかれず終わる",
    "期待値ゼロからスタート",
    "ギリ耐えれる日",
    "今日は何もしないのが正解",
    "調子乗ると即終了",
    "まあまあ、でも油断するな",
    "運はあるけど色々台無し",
    "今日は静かにしとけって",
    "お前にしては上出来",
    "何も考えないほうがうまくいく",
    "逆に動くと失敗する日",
    "とりあえずクソして寝ろ",
    "今日は存在感薄めでいけ",
    "ワンチャンあるけど逃すタイプ",
    "小さな幸せ見逃すなよ",
    "普通にしてれば普通",
    "無理したら終わる",
    "今日の敵は自分",
    "なんとかなる、たぶん",
    "奇跡は起きない",
    "でも事故も起きない",
    "地味に平和",
    "刺激はないけど安全",
    "人生ってこんなもん",
    "一瞬いいことあるかも",
    "でもすぐ終わる",
    "チャンス来るけど気づかない",
    "惜しい一日",
    "ギリギリセーフ",
    "まあまあ耐え",
    "期待しすぎるな",
    "今日も通常運転。いい顔だな！",
    "悪くない、でもお前が悪い",
    "朝から顔が疲れてるぞ",
    "今日の判断力、ちょっと危ない",
    "頑張る前に深呼吸しろ",
    "勢いだけで動くな、事故る",
    "その自信どこから来たんだよ",
    "今日は余計な一言を飲み込め",
    "センスはないけど運はある",
    "勘違いしなければ勝てる",
    "急ぐな、どうせ間に合わない",
    "今日は目立つと損する",
    "存在感は薄いけど平和",
    "変なプライド捨てろ",
    "無理に笑うな、バレてる",
    "やる気だけは評価する",
    "結果は知らんが姿勢はいい",
    "今日は人のせいにするな",
    "だいたい自分のせい",
    "寝不足の顔で運試すな",
    "今日は黙ってるだけで吉",
    "しゃべるほど運が逃げる",
    "期待されてない分ラクだな",
    "変に頑張ると裏目に出る",
    "今日の幸運は小さすぎて見えない",
    "大丈夫、誰も見てない",
    "今日だけは謙虚にしとけ",
    "そのノリ、今日はキツイ",
    "運勢より他を気にしろ",
    "勝てない勝負に行くな",
    "今日は深追い禁止",
    "欲張ると全部こぼす",
    "小さく勝って帰れ",
    "なんか惜しい、いつも通り",
    "失敗してもネタにはなる",
    "今日のミスは笑ってごまかせ",
    "変な奇跡を期待するな",
    "運より準備しろ",
    "たぶん大丈夫、知らんけど",
    "自分を過信するな。クソして寝ろ",
    "今日のお前はまあまあ雑",
    "雑に生きるな、でも雑でいい、知らんけど",
    "たまにはちゃんとしろ",
    "今日は逃げても許す",
    "正面突破はやめとけ",
    "裏道を探せ、人生もな",
    "今日は無難が最強",
    "余計なことしなければ勝ち",
    "落ち着け、まだ何も始まってない",
    "やる前から疲れるな",
    "今日の敵は今日（謎）",
    "集中力が死んでます",
    "でもまあ、なんとかなる顔してる",
]

lucky_people = [
    "前髪だけ完璧な人",
    "ずっと同じ服の人",
    "Wi-Fi弱い家の人",
    "やたら早口な店員",
    "片手だけ冷たい人",
    "声だけデカい人",
    "微妙に遅刻する人",
    "リアクション薄い人",
    "無駄にポジティブな人",
    "ずっとスマホ見てる人",
    "謎に運がいい人",
    "やたら詳しい人",
    "なんでも否定する人",
    "空気読まない人",
    "テンションだけ高い人",
    "ずっと眠そうな人",
    "話長い人",
    "急に静かになる人",
    "ちょっとズレてる人",
    "意味不明なこと言う人",
    "毎回同じ話する人",
    "笑い方クセ強い人",
    "無駄に丁寧な人",
    "やたら距離近い人",
    "なんかいい匂いする人",
    "無言で圧かける人",
    "常に汗かいてる人",
    "タイミング悪い人",
    "なぜかモテる人",
    "いつも忙しい風の実は暇な人",
    "無駄に声小さい人",
    "なんでも知ってる風の人",
    "反応遅い人",
    "ちょっと天然な人",
    "話途中で変える人",
    "同じミス繰り返す人",
    "急に元気になる人",
    "やたら謝る人",
    "無駄に自信ある人",
    "ずっとニヤニヤしてる人",
    "なんか疲れてる人",
    "静かにキレてる人",
    "エピソードトークしたがる人",
    "説明長い人",
    "無駄にフットワーク軽い人",
    "方向音痴な人",
    "何でも写真撮る人",
    "急に歌い出す人",
    "弁当の話したら止まらない人",
    "なぜか毎回いる人",
    "カバンが常にパンパンな人",
    "充電器を毎回借りる人",
    "財布をよく忘れる人",
    "傘を持つと雨が止む人",
    "声が通りすぎる人",
    "唐突に真面目になる人",
    "謎の健康法をすすめる人",
    "絵文字だけで会話する人",
    "既読だけ早い人",
    "未読で生きてる人",
    "予定を詰め込みすぎる人",
    "朝だけ機嫌悪い人",
    "夜だけ元気な人",
    "ずっと何か食べてる人",
    "水をやたら飲む人",
    "靴だけ派手な人",
    "金持ちぶってる貧乏人",
    "前髪を気にしすぎる人",
    "笑うタイミングが遅い人",
    "拍手が一人だけ長い人",
    "注文がやたら遅い人",
    "メニューを決められない人",
    "エレベーターで気まずい人",
    "改札で止まる人",
    "小銭を探し続ける人",
    "声に出して考える人",
    "急に哲学っぽいこと言う人",
    "謎に姿勢がいい人",
    "やたら猫背な人",
    "スマホの画面バキバキな人",
    "イヤホン片方なくす人",
    "通知音がデカい人",
    "アラームを何個もかける人",
    "寝癖が強い人",
    "荷物が少なすぎる人",
    "コンビニに詳しい人",
    "新商品にすぐ飛びつく人",
    "スタンプだけ送る人",
    "語尾が独特な人",
    "返事が全部『たしかに』の人",
    "いつも寒そうな人",
    "いつも暑そうな人",
    "なぜか道を聞かれる人",
    "レジで焦る人",
    "電車で寝過ごす人",
    "階段でつまずく人",
    "ドアに押し負ける人",
    "自販機の前で悩む人",
    "写真を撮る角度が独特な人",
    "なぜか今日だけ優しい人",
]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """使い方を案内する /start"""
    await update.message.reply_text(
        "おみくじBOTです。\n\n"
        "使い方:\n"
        "/omikuji または /おみくじ を送ると、おみくじを引けます。"
    )


async def run_omikuji(update: Update) -> None:
    """おみくじの演出と結果送信"""
    await update.message.reply_text("🙏")
    await asyncio.sleep(1)
    await update.message.reply_text("⛩")
    await asyncio.sleep(1)

    fortune = random.choice(fortunes)
    comment = random.choice(comments)
    lucky_person = random.choice(lucky_people)
    await update.message.reply_text(
        f"{fortune}\n{comment}\n\nラッキーパーソン：{lucky_person}"
    )


async def omikuji_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_omikuji(update)


async def omikuji_japanese_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await run_omikuji(update)


def main() -> None:
    token_raw = os.getenv("TELEGRAM_BOT_TOKEN")
logger.info("ENV CHECK: TELEGRAM_BOT_TOKEN exists=%s len=%s", token_raw is not None, len(token_raw or ""))
token = (token_raw or "").strip()

    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN が設定されていません。"
            " RailwayのVariablesまたはローカルの .env に設定してください。"
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("omikuji", omikuji_command))
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(r"^/おみくじ(?:@\w+)?$"),
            omikuji_japanese_command,
        )
    )

    logger.info("Bot started. Waiting for commands...")
    app.run_polling()


if __name__ == "__main__":
    main()
