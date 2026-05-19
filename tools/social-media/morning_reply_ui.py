"""
morning_reply_ui.py - 朝のリプライワークフロー（Streamlit ブラウザUI版）

起動: python -m streamlit run tools/social-media/morning_reply_ui.py
"""

import sys
import os
from pathlib import Path
import yaml
import streamlit as st

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

st.markdown("""
<style>
.tweet-box {
    background:#f0f7ff; border-left:4px solid #1d9bf0;
    padding:12px 16px; border-radius:6px; margin-bottom:4px;
    font-size:15px; line-height:1.7; white-space:pre-wrap;
}
.reply-option {
    background:#fff; border:1px solid #e1e8ed; border-radius:8px;
    padding:10px 14px; margin-bottom:4px;
    font-size:14px; line-height:1.7; white-space:pre-wrap;
}
.label-tag {
    font-size:11px; font-weight:bold; color:#888;
    background:#f0f0f0; padding:2px 6px; border-radius:4px;
    margin-right:6px;
}
</style>
""", unsafe_allow_html=True)

# ── 初期化 ────────────────────────────────────────────────────────────────────
mr.load_env()

def ss_init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ss_init("tweets_data", [])
ss_init("posted_ids",  set())
ss_init("skipped_ids", set())

# ── ヘッダー ──────────────────────────────────────────────────────────────────
st.title("🌅 朝のリプライワークフロー")
st.caption("Emport AI / アレン ─ ターゲットアカウントの最新ツイートにリプライして存在感を高める")

c1, c2, c3 = st.columns(3)
c1.metric("取得ツイート", len(st.session_state.tweets_data))
c2.metric("投稿済み",     len(st.session_state.posted_ids))
c3.metric("スキップ",     len(st.session_state.skipped_ids))
st.divider()

# ── ツイート取得 ──────────────────────────────────────────────────────────────
YAML_PATH = BASE_DIR / "target_accounts.yaml"

def fetch_all_tweets():
    with open(YAML_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    results = []
    for tier in ["tier_a", "tier_b"]:
        for acc in config.get("accounts", {}).get(tier, []):
            username    = acc.get("username", "")
            name        = acc.get("name", username)
            reply_angle = acc.get("reply_angle", "")
            uid = mr.get_user_id(username)
            if not uid:
                continue
            for tweet in mr.get_recent_tweets(uid, hours=48)[:3]:
                results.append({
                    "username":    username,
                    "name":        name,
                    "reply_angle": reply_angle,
                    "tweet_id":    tweet["id"],
                    "tweet_text":  tweet["text"],
                    "created_at":  tweet.get("created_at", "")[:16].replace("T", " "),
                    "replies":     None,
                })
    return results

btn_col, clr_col = st.columns([3, 1])
with btn_col:
    if st.button("📥 最新ツイートを取得する", type="primary", use_container_width=True):
        with st.spinner("取得中..."):
            st.session_state.tweets_data = fetch_all_tweets()
            st.session_state.posted_ids  = set()
            st.session_state.skipped_ids = set()
        st.rerun()
with clr_col:
    if st.button("🔄 リセット", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if not st.session_state.tweets_data:
    st.info("「最新ツイートを取得する」を押してください")
    st.stop()

# ── ツイートカード ────────────────────────────────────────────────────────────
LABELS = ["フォーマル", "カジュアル", "質問特化"]

for idx, item in enumerate(st.session_state.tweets_data):
    tweet_id   = item["tweet_id"]
    tweet_text = item["tweet_text"]
    username   = item["username"]
    name       = item["name"]
    reply_angle = item["reply_angle"]
    created_at = item["created_at"]

    is_posted  = tweet_id in st.session_state.posted_ids
    is_skipped = tweet_id in st.session_state.skipped_ids

    with st.container():
        h1, h2 = st.columns([5, 1])
        with h1:
            st.markdown(f"**@{username}**  {name}  · {created_at}")
        with h2:
            if is_posted:
                st.success("✅ 投稿済み")
            elif is_skipped:
                st.caption("スキップ")

        st.markdown(
            f'<div class="tweet-box">{tweet_text}'
            f'<br><small>🔗 <a href="https://x.com/{username}/status/{tweet_id}" target="_blank">元ツイートを開く</a></small></div>',
            unsafe_allow_html=True,
        )

        if is_posted or is_skipped:
            st.divider()
            continue

        # ── リプライ案生成 ──
        if item["replies"] is None:
            if st.button("✨ リプライ案を生成", key=f"gen_{idx}"):
                with st.spinner("Claude Haiku で生成中..."):
                    item["replies"] = mr.generate_replies(tweet_text, name, reply_angle)
                st.rerun()
            if st.button("スキップ", key=f"skip_before_{idx}"):
                st.session_state.skipped_ids.add(tweet_id)
                st.rerun()
        else:
            replies = item["replies"]

            # ── 案の表示と選択 ──
            # session_state に直接書き込んでテキストエリアを制御
            edit_key = f"edit_body_{idx}"
            ss_init(edit_key, "")

            st.markdown("**リプライ案を選んでください：**")
            for ri, rtext in enumerate(replies):
                cc    = mr.tweet_char_count(rtext)
                label = LABELS[ri] if ri < len(LABELS) else f"案{ri+1}"
                cflag = f"✅ {cc}/280" if cc <= 280 else f"⚠️ {cc}/280"

                r1, r2 = st.columns([5, 1])
                with r1:
                    st.markdown(
                        f'<div class="reply-option"><span class="label-tag">{label}</span>'
                        f'<small>{cflag}</small><br>{rtext}</div>',
                        unsafe_allow_html=True,
                    )
                with r2:
                    if st.button(f"選択", key=f"sel_{idx}_{ri}"):
                        st.session_state[edit_key] = rtext
                        st.rerun()

            # ── 編集テキストエリア ──
            st.markdown("**編集・確認してから投稿：**")
            body = st.text_area(
                label="リプライ本文",
                key=edit_key,
                height=110,
                label_visibility="collapsed",
                placeholder="上の「選択」ボタンで自動入力、または直接ここに入力",
            )
            ec = mr.tweet_char_count(body)
            color = "green" if ec <= 280 else "red"
            st.markdown(f"<small style='color:{color}'>{ec} / 280 文字</small>", unsafe_allow_html=True)

            # ── 投稿・スキップボタン ──
            p1, p2 = st.columns(2)
            with p1:
                post_disabled = (ec == 0 or ec > 280)
                if st.button(
                    "🚀 投稿する" + ("　（文字数エラー）" if ec > 280 else "　（本文を入力してください）" if ec == 0 else ""),
                    key=f"post_btn_{idx}",
                    type="primary",
                    disabled=post_disabled,
                    use_container_width=True,
                ):
                    with st.spinner("X に投稿中..."):
                        try:
                            result  = mr.post_reply(body, tweet_id)
                            new_id  = result.get("data", {}).get("id", "?")
                            st.session_state.posted_ids.add(tweet_id)
                            st.success(f"✅ 投稿しました！ ID: {new_id}")
                        except Exception as e:
                            st.error(f"❌ 投稿エラー: {e}")
                    st.rerun()
            with p2:
                if st.button("スキップ", key=f"skip_{idx}", use_container_width=True):
                    st.session_state.skipped_ids.add(tweet_id)
                    st.rerun()

        st.divider()

# ── 集計フッター ──────────────────────────────────────────────────────────────
total  = len(st.session_state.tweets_data)
posted = len(st.session_state.posted_ids)
remain = total - posted - len(st.session_state.skipped_ids)

st.markdown(f"### 本日の集計 ─ 投稿 **{posted}** 件 / 残り {remain} 件")
if posted >= 15:
    st.success("🎉 今日の目標（15件）達成！")
elif posted > 0:
    st.info(f"あと {max(0, 15 - posted)} 件で目標（15件）達成")
