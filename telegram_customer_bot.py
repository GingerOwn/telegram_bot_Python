import os
from datetime import timedelta
import redis
import yaml
from language_configuration import get_language_config
from telegram.ext import Updater  # 更新者
from telegram.ext import CommandHandler  # 注册处理器 一般用 回答用
from telegram.ext import MessageHandler, Filters  # Filters 过滤讯息
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import pymysql


def get_yaml_data(yaml_file):
    # 打开yaml文件
    if os.path.exists(yaml_path):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
            return True, cfg
    else:
        message = '配置文件不存在，请把目录下的 config.yaml 修改为 config.yaml'
        return False, message


yaml_path = './config.yaml'
flag, yaml_config = get_yaml_data(yaml_path)
if not flag:
    print(yaml_config)


def judge_exists(key, end_key, default):
    if key in yaml_config.keys():
        if yaml_config[key] is not None and yaml_config[key] != '' and yaml_config[key][end_key] is not None and \
                yaml_config[key][end_key] != '':
            return yaml_config[key][end_key]
    else:
        return default


redis_host = '192.168.2.20'
redis_port = 6381
redis_db = 8
redis_host = judge_exists('redis', 'host', redis_host)
redis_port = judge_exists('redis', 'port', redis_port)
redis_db = judge_exists('redis', 'db', redis_db)
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'telegram_bot_md'
mysql_pwd = 'cLaRKhZPG3XYyZS4'
mysql_charset = 'utf8mb4'
mysql_db = 'telegram_bot_md'
mysql_host = judge_exists('mysql', 'host', mysql_host)
mysql_port = judge_exists('mysql', 'port', mysql_port)
mysql_user = judge_exists('mysql', 'user', mysql_user)
mysql_pwd = judge_exists('mysql', 'pwd', mysql_pwd)
mysql_charset = judge_exists('mysql', 'charset', mysql_charset)
mysql_db = judge_exists('mysql', 'db', mysql_db)
language = 'pt-br'
token = '5795276092:AAHSIBAe3sH6NOu1OfI1050r6sWpKF2xlDs'
language = judge_exists('bot', 'language', language)
token = judge_exists('bot', 'bot_token', token)
conn = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pwd,
                       charset=mysql_charset, db=mysql_db)  # 连接mysql数据库，并指定编码格式
language_config = get_language_config(language)  # 调整语言  葡萄牙语(巴西) pt-br 中文 zh-cn
valid = 0
valid = judge_exists('proxy', 'valid', valid)
if valid == 1:
    print(r.hget('telegram:bot:config', 'proxy_url'))
    updater = Updater(token=token,
                      request_kwargs={'proxy_url': "http://127.0.0.1:7890"})  # 创建调度器
else:
    updater = Updater(token=token)
dp = updater.dispatcher


def message_button(update, context):  # 内联菜单按钮
    update.message.reply_text("这是测试",
                              reply_markup=InlineKeyboardMarkup(
                                  [[InlineKeyboardButton("data1", url='https://t.me/strongtest_bot'),
                                    InlineKeyboardButton("data2", url="https://www.google.com")],
                                   [InlineKeyboardButton("data3", url="https://www.google.com"),
                                    InlineKeyboardButton("data4", url="https://www.google.com")]])
                              )
    print(context.error)


def greet_command(update, context):  # 与键盘位置一致的点击按钮
    first_button1 = [[language_config[0], language_config[1]],
                     [language_config[2], language_config[3]],
                     [language_config[4], language_config[5]]]
    reply_markup = ReplyKeyboardMarkup(first_button1, resize_keyboard=True)
    update.message.reply_text(language_config[40], reply_markup=reply_markup)
    print(context.error)


def re_first_button(update, context):  # 点击二级菜单返回按钮后返回一级菜单按钮
    first_button1 = [[language_config[0], language_config[1]],
                     [language_config[2], language_config[3]],
                     [language_config[4], language_config[5]]]
    reply_markup = ReplyKeyboardMarkup(first_button1, resize_keyboard=True)
    update.message.reply_text(language_config[7], reply_markup=reply_markup)
    print(context.error)


def set_mysql(update, button_type, index):  # 写入mysql数据库并打印出接收到的信息及插入数据库语句
    info = update.message  # 获取当前接收到的信息
    date_time = info['date']  # 获取发送时间
    date_time_stamp = int((date_time - timedelta(hours=3)).timestamp())   # 获取时间戳
    chat_id = info['chat']['id']  # 获取发送信息id
    last_name = info['chat']['last_name']  # 获取发送信息的姓
    first_name = info['chat']['first_name']  # 获取发送信息的名称
    sql = 'insert into click_button_count values(%s,%s,"%s",%s,%s,"%s","%s")' % (
        0, button_type, language_config[index], chat_id,
        date_time_stamp, last_name,
        first_name)
    print(info)
    print(sql)
    try:
        conn.ping(reconnect=True)
        cursor = conn.cursor()  # 创建连接游标
        cursor.execute(sql)  # 执行插入语句
        conn.commit()  # 提交插入语句
    except pymysql.Error as e:
        print(e)


# 游戏介绍点击后返回的二级按钮菜单
def game_info(update, context):
    second_button = [[language_config[8], language_config[9]],
                     [language_config[10], language_config[11]], [language_config[6]]]
    reply_markup = ReplyKeyboardMarkup(second_button, resize_keyboard=True)
    update.message.reply_text(language_config[42], reply_markup=reply_markup)
    set_mysql(update, 1, 0)
    print(context.error)


# 充值问题点击后返回的二级按钮菜单
def recharge_problem(update, context):
    second_button = [[language_config[12], language_config[13]],
                     [language_config[14], language_config[6]]]
    reply_markup = ReplyKeyboardMarkup(second_button, resize_keyboard=True)
    update.message.reply_text(language_config[43], reply_markup=reply_markup)
    set_mysql(update, 2, 1)
    print(context.error)


# 提现问题点击后返回的二级按钮菜单
def get_money(update, context):
    second_button = [[language_config[15], language_config[16]],
                     [language_config[17], language_config[18]],
                     [language_config[19], language_config[6]]]
    reply_markup = ReplyKeyboardMarkup(second_button, resize_keyboard=True)
    update.message.reply_text(language_config[44], reply_markup=reply_markup)
    set_mysql(update, 3, 2)
    print(context.error)


# 游戏问题点击后返回的二级按钮菜单
def game_problem(update, context):
    second_button = [[language_config[20], language_config[21]],
                     [language_config[22], language_config[6]]]
    reply_markup = ReplyKeyboardMarkup(second_button, resize_keyboard=True)
    update.message.reply_text(language_config[45], reply_markup=reply_markup)
    set_mysql(update, 4, 3)
    print(context.error)


# 二级菜单点击后
def platform_intro(update, context):
    # 平台介绍点击后的返回内容
    update.message.reply_text(language_config[23])
    set_mysql(update, 7, 8)
    print(context.error)


def get_money_rule(update, context):
    # 提现规则点击后的返回内容
    update.message.reply_text(language_config[24])
    set_mysql(update, 8, 9)
    print(context.error)


def recharge_rule(update, context):
    # 充值规则点击后的返回内容
    update.message.reply_text(language_config[25])
    set_mysql(update, 9, 10)
    print(context.error)


def game_vip(update, context):
    # VIP才能玩的游戏点击后的返回内容
    update.message.reply_text(language_config[26])
    set_mysql(update, 10, 11)
    print(context.error)


# 二级按钮充值问题点击后
def recharge_how(update, context):
    # 如何充值点击后的返回内容
    update.message.reply_video(video=open(r'recharge.mp4', 'rb'), caption=language_config[27])
    set_mysql(update, 11, 12)
    print(context.error)


def unable_recharge_page(update, context):
    # 无法打开充值页点击后的返回内容
    update.message.reply_text(language_config[28])
    set_mysql(update, 12, 13)
    print(context.error)


def recharge_not_get(update, context):
    # 充值不到账点击后的返回内容
    update.message.reply_text(language_config[29])
    set_mysql(update, 13, 14)
    print(context.error)


# 二级按钮提现问题点击后
def unable_get_money(update, context):
    # 无法发起提现点击后的返回内容
    update.message.reply_text(language_config[30])
    set_mysql(update, 14, 15)
    print(context.error)


def get_money_dead(update, context):
    # 提现失败点击后的返回内容
    update.message.reply_text(language_config[31])
    set_mysql(update, 15, 16)
    print(context.error)


def gold_not_return(update, context):
    # 提现失败金币未退回点击后的返回内容
    update.message.reply_text(language_config[32])
    set_mysql(update, 16, 17)
    print(context.error)


def get_money_examine(update, context):
    # 提现一直审核中点击后的返回内容
    update.message.reply_text(language_config[33])
    set_mysql(update, 17, 18)
    print(context.error)


def recharge_success_not_get(update, context):
    # 提现成功，但没到账点击后的返回内容
    update.message.reply_text(language_config[34])
    set_mysql(update, 18, 19)
    print(context.error)


# 二级按钮游戏问题点击后
def unable_login(update, context):
    # 无法注册和登录点击后的返回内容
    update.message.reply_text(language_config[35])
    set_mysql(update, 19, 20)
    print(context.error)


def unable_bet(update, context):
    # 无法下注，Crash无法回收点击后的返回内容
    update.message.reply_text(language_config[36])
    set_mysql(update, 20, 21)
    print(context.error)


def unable_load_game(update, context):
    # 无法加载游戏点击后的返回内容
    update.message.reply_text(language_config[37])
    set_mysql(update, 21, 22)
    print(context.error)


# 一级菜单按钮游戏建议
def game_suggestion(update, context):
    # 游戏建议点击后的返回内容
    str1 = language_config[38]
    update.message.reply_text(str1)
    set_mysql(update, 5, 4)
    print(context.error)


# 一级菜单按钮人工客服
def customer(update, context):
    # 人工客服点击后的返回内容
    update.message.reply_text(text=language_config[39], parse_mode='HTML',
                              disable_web_page_preview=True)
    set_mysql(update, 6, 5)
    print(context.error)


def get_all_data(update, context):
    # 用户输入任何内容时返回的内容
    print(context)
    print(update)
    update.message.reply_text(language_config[41])


def Filter_regex(val, way):  # 过滤器
    return dp.add_handler(MessageHandler(Filters.regex(val), way))


def main():
    dp.add_handler(CommandHandler("start", greet_command))  # 添加start作为初始命令
    Filter_regex(language_config[8], platform_intro)
    Filter_regex(language_config[9], get_money_rule)
    Filter_regex(language_config[10], recharge_rule)
    Filter_regex(language_config[11], game_vip)
    Filter_regex(language_config[12], recharge_how)
    Filter_regex(language_config[13], unable_recharge_page)
    Filter_regex(language_config[14], recharge_not_get)
    Filter_regex(language_config[15], unable_get_money)
    Filter_regex(language_config[17], gold_not_return)
    Filter_regex(language_config[16], get_money_dead)
    Filter_regex(language_config[18], get_money_examine)
    Filter_regex(language_config[19], recharge_success_not_get)
    Filter_regex(language_config[20], unable_login)
    Filter_regex(language_config[21], unable_bet)
    Filter_regex(language_config[22], unable_load_game)
    Filter_regex(language_config[0], game_info)
    Filter_regex(language_config[1], recharge_problem)
    Filter_regex(language_config[2], get_money)
    Filter_regex(language_config[3], game_problem)
    Filter_regex(language_config[4], game_suggestion)
    Filter_regex(language_config[5], customer)
    Filter_regex(language_config[6], re_first_button)
    dp.add_handler(MessageHandler(Filters.all, get_all_data))
    # 轮询模式
    updater.start_polling()
    # 回调模式
    # updater.start_webhook(listen='0.0.0.0', port=8443, url_path=token,
    #                       webhook_url='https://tgcallback.slotfree.xyz/' + token, force_event_loop=True)
    updater.idle()


if __name__ == '__main__':  # 程序入口
    main()
