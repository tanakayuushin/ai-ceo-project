"""
morning_reply_ui.py - 朝のリプライワークフロー（Streamlit ブラウザUI版）

起動: streamlit run tools/social-media/morning_reply_ui.py
"""

import sys
import os
from pathlib import Path
import streamlit as st

# パス設定
BASE_DIR    = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent.parent
sys.path.insert(0, str(BASE_DIR))

import morning_reply as mr

# ── ページ設定 ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="朝のリプライ / Emport AI",
    page_icon="🌅",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.tweet-box {
    background: #f8f9fa;
    border-left: 4px solid #1d9bf0;
    padding: 12px 16px;
    border-radius: 4px;
    margin-bottom: 8px;
    font-size: 15px;
    line-height: 1.6;
}
.reply-card {
    background: #ffffff;
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 14px;
    line-height: 1.6;
}
.char-ok  { color: #2e7d32; font-weight: bold; font-size: 12px; }
.char-warn { color: #e65100; font-weight: bold; font-size: 12px; }
.posted-badge { color: #1d9bf0; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── 初期化 ────────────────────────────────────────────────────────────────────
mr.load_env()

if "tweets_data" not in st.session_state:
    st.session_state.tweets_data   = []   # [{account, tweet, replies}]
if "posted_ids" not in st.session_state:
    st.session_state.posted_ids    = set()
if "skipped_ids" not in st.session_state:
    st.session_state.skipped_ids   = set()
if "loading" not in st.session_state:
    st.session_state.loading       = False

# ── ヘッダー ─────────────────────────────────────────────────────────────────
st.title("🌅 朝のリプライワークフロー")
st.caption("Emport AI / アレン  ─  ターゲットアカウントの最新ツイートにリプライして存在感を高める")

col_stat1, col_stat2, col_stat3 = st.columns(3)
col_stat1.metric("取得ツイート", len(st.session_state.tweets_data))
col_stat2.metric("投稿済み",     len(st.session_state.posted_ids))
col_stat3.metric("スキップ",     len(st.session_state.skipped_ids))

st.divider()

# ── ツイート取得ボタン ────────────────────────────────────────────────────────
import yaml

YAML_PATH = BASE_DIR / "target_accounts.yaml"

def fetch_tweets():
    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    accounts_data = config.get("accounts", {})
    results = []

    for tier in ["tier_a", "tier_b"]:
        for acc in accounts_data.get(tier, []):
            username    = acc.get("username", "")
            name        = acc.get("name", username)
            reply_angle = acc.get("reply_angle", "")

            uid = mr.get_user_id(username)
            if not uid:
                continue

            tweets = mr.get_recent_tweets(uid, hours=48)
            for tweet in tweets[:3]:
                results.append({
                    "username":    username,
                    "name":        name,
                    "reply_angle": reply_angle,
                    "tweet_id":    tweet["id"],
                    "tweet_text":  tweet["text"],
                    "created_at":  tweet.get("created_at", "")[:16].replace("T", " "),
                    "replies":     None,  # 未生成
                })
    return results

col_fetch, col_clear = st.columns([2, 1])
with col_fetch:
    if st.button("📥 最新ツイートを取得する", type="primary", use_container_width=True):
        with st.spinner("ツイートを取得中..."):
            st.session_state.tweets_data = fetch_tweets()
            st.session_state.posted_ids  = set()
            st.session_state.skipped_ids = set()
        st.rerun()

with col_clear:
    if st.button("🔄 リセット", use_container_width=True):
        st.session_state.tweets_data = []
        st.session_state.posted_ids  = set()
        st.session_state.skipped_ids = set()
        st.rerun()

# ── ツイート一覧 ──────────────────────────────────────────────────────────────
if not st.session_state.tweets_data:
    st.info("「最新ツイートを取得する」を押してください")
    st.stop()

for idx, item in enumerate(st.session_state.tweets_data):
    tweet_id   = item["tweet_id"]
    tweet_text = item["tweet_text"]
    username   = item["username"]
    name       = item["name"]
    reply_angle = item["reply_angle"]
    created_at = item["created_at"]

    is_posted  = tweet_id in st.session_state.posted_ids
    is_skipped = tweet_id in st.session_state.skipped_ids

    # ── カード ──
    with st.container():
        # アカウント名・ツイートリンク
        header_col, badge_col = st.columns([4, 1])
        with header_col:
            st.markdown(f"**@{username}**  {name}  ·  {created_at}")
        with badge_col:
            if is_posted:
                st.markdown('<span class="posted-badge">✅ 投稿済み</span>', unsafe_allow_html=True)
            elif is_skipped:
                st.markdown("~~スキップ~~")

        # ツイート本文
        tc = mr.tweet_char_count(tweet_text)
        st.markdown(
            f'<div class="tweet-box">{tweet_text}'
            f'<br><small>🔗 <a href="https://x.com/{username}/status/{tweet_id}" target="_blank">元ツイートを開く</a></small></div>',
            unsafe_allow_html=True
        )

        if is_posted or is_skipped:
            st.divider()
            continue

        # リプライ案の生成・表示
        if item["replies"] is None:
            if st.button(f"✨ リプライ案を生成", key=f"gen_{idx}"):
                with st.spinner("Claude Haiku で生成中..."):
                    item["replies"] = mr.generate_replies(tweet_text, name, reply_angle)
                st.rerun()
        else:
            replies = item["replies"]
            labels  = ["フォーマル", "カジュアル", "質問特化"]

            selected_text = st.session_state.get(f"selected_{idx}", "")

            for ri, reply_text in enumerate(replies):
                cc     = mr.tweet_char_count(reply_text)
                cflag  = f'<span class="char-ok">{cc}/280</span>' if cc <= 280 else f'<span class="char-warn">⚠️ {cc}/280 文字超過</span>'
                label  = labels[ri] if ri < len(labels) else f"案{ri+1}"

                rcol1, rcol2 = st.columns([5, 1])
                with rcol1:
                    st.markdown(
                        f'<div class="reply-card"><b>{label}</b>　{cflag}<br>{reply_text}</div>',
                        unsafe_allow_html=True
                    )
                with rcol2:
                    if st.button(f"このまま投稿", key=f"post_{idx}_{ri}"):
                        st.session_state[f"selected_{idx}"] = reply_text

            # 自由編集欄
            edit_text = st.text_area(
                "✏️ 編集して投稿（上のボタンで自動入力、または直接入力）",
                value=st.session_state.get(f"selected_{idx}", ""),
                key=f"edit_{idx}",
                height=100,
            )
            if edit_text != st.session_state.get(f"selected_{idx}", ""):
                st.session_state[f"selected_{idx}"] = edit_text

            ec = mr.tweet_char_count(edit_text)
            if ec > 0:
                color = "#2e7d32" if ec <= 280 else "#e65100"
                st.markdown(f"<small style='color:{color}'>{ec}/280 文字</small>", unsafe_allow_html=True)

            pcol1, pcol2 = st.columns(2)
            with pcol1:
                if st.button("🚀 投稿する", key=f"submit_{idx}", type="primary",
                             disabled=(ec == 0 or ec > 280)):
                    with st.spinner("投稿中..."):
                        try:
                            result = mr.post_reply(edit_text, tweet_id)
                            new_id = result.get("data", {}).get("id", "?")
                            st.session_state.posted_ids.add(tweet_id)
                            st.success(f"✅ 投稿しました（ID: {new_id}）")
                        except Exception as e:
                            st.error(f"❌ エラー: {e}")
                    st.rerun()
            with pcol2:
                if st.button("スキップ", key=f"skip_{idx}"):
                    st.session_state.skipped_ids.add(tweet_id)
                    st.rerun()

        st.divider()

# ── フッター集計 ──────────────────────────────────────────────────────────────
total   = len(st.session_state.tweets_data)
posted  = len(st.session_state.posted_ids)
skipped = len(st.session_state.skipped_ids)
remain  = total - posted - skipped

st.markdown(f"### 本日の集計  ─  投稿 **{posted}** 件  /  スキップ {skipped}  /  残り {remain}")
if posted >= 15:
    st.success("🎉 今日の目標（15件）達成！")
elif posted >= 5:
    st.info(f"あと {15 - posted} 件で今日の最低目標（15件）達成")
