"""
山田建設 専用 AI アシスタント（RAG デモ）
ChromaDB + Claude API
"""

import os
import chromadb
import anthropic

# ========== 学習データ ==========
DOCUMENTS = [
    {
        "id": "doc_01",
        "text": "外壁塗装の単価は1平方メートルあたり2500円〜3500円です。",
        "metadata": {"category": "料金", "service": "外壁塗装"},
    },
    {
        "id": "doc_02",
        "text": "外壁塗装の工期は通常5日〜7日です。天候や建物の状態によって前後する場合があります。",
        "metadata": {"category": "工期", "service": "外壁塗装"},
    },
    {
        "id": "doc_03",
        "text": "塗膜の保証期間は10年です。施工後10年以内に塗膜の剥がれや著しい色あせが発生した場合は無償で対応します。",
        "metadata": {"category": "保証", "service": "全般"},
    },
    {
        "id": "doc_04",
        "text": "対応エリアは宇部市・山口市・防府市・下関市です。上記エリア外はご相談ください。",
        "metadata": {"category": "対応エリア", "service": "全般"},
    },
    {
        "id": "doc_05",
        "text": "築15年・2階建て住宅の外壁塗装費用の目安は85万円〜120万円です。面積や使用塗料によって変わります。",
        "metadata": {"category": "料金", "service": "外壁塗装"},
    },
    {
        "id": "doc_06",
        "text": "屋根修理の費用は15万円〜50万円です。破損箇所の範囲・屋根材の種類によって異なります。",
        "metadata": {"category": "料金", "service": "屋根修理"},
    },
    {
        "id": "doc_07",
        "text": "外構工事（フェンス・駐車場・庭など）の費用は50万円〜200万円です。工事内容・範囲によって異なります。",
        "metadata": {"category": "料金", "service": "外構工事"},
    },
    {
        "id": "doc_08",
        "text": "支払い方法は工事完了後の銀行振込です。分割払いや事前払いは対応しておりません。",
        "metadata": {"category": "支払い", "service": "全般"},
    },
    {
        "id": "doc_09",
        "text": "無料見積もりに対応しています。お電話またはメールでお気軽にお申し込みください。費用は一切かかりません。",
        "metadata": {"category": "見積もり", "service": "全般"},
    },
    {
        "id": "doc_10",
        "text": "営業時間は平日8時〜17時です。土日祝日はお休みです。緊急の場合はメールにてご連絡ください。",
        "metadata": {"category": "営業情報", "service": "全般"},
    },
]

COLLECTION_NAME = "yamada_kensetsu"


# ========== ChromaDB セットアップ ==========
def setup_vectordb() -> chromadb.Collection:
    """ChromaDB にドキュメントを登録して Collection を返す"""
    client = chromadb.Client()  # インメモリ（永続化不要のデモ用）

    # 既存コレクションがあれば削除してリセット
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION_NAME)

    collection.add(
        ids=[d["id"] for d in DOCUMENTS],
        documents=[d["text"] for d in DOCUMENTS],
        metadatas=[d["metadata"] for d in DOCUMENTS],
    )

    print(f"[DB] {len(DOCUMENTS)} 件のドキュメントを登録しました。\n")
    return collection


# ========== 検索 ==========
def search(collection: chromadb.Collection, query: str, n_results: int = 3) -> list[dict]:
    """質問に関連するドキュメントを検索して返す"""
    result = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append({
            "text": doc,
            "category": meta.get("category", ""),
            "service": meta.get("service", ""),
            "score": round(1 - dist, 3),  # コサイン類似度に変換
        })
    return hits


# ========== Claude で回答生成 ==========
def generate_answer(query: str, hits: list[dict]) -> str:
    """検索結果をコンテキストとして Claude に回答させる"""
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY を環境変数から読む

    context = "\n".join(
        f"・{h['text']}" for h in hits
    )

    prompt = f"""あなたは山田建設の専門AIアシスタントです。
以下の「参照情報」だけをもとに、お客様の質問に丁寧かつ正確に回答してください。
参照情報に含まれない内容については「詳細はお問い合わせください」と案内してください。

【参照情報】
{context}

【お客様の質問】
{query}

【回答】"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


# ========== メイン ==========
def main():
    print("=" * 50)
    print("  山田建設 AI アシスタント（RAG デモ）")
    print("=" * 50)

    # API キー確認
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\n[エラー] ANTHROPIC_API_KEY が設定されていません。")
        print("  set ANTHROPIC_API_KEY=sk-ant-xxxxx  (Windows)")
        return

    # DB 初期化
    collection = setup_vectordb()

    # 対話ループ
    print("質問を入力してください。終了するには 'q' を入力してください。\n")
    while True:
        query = input("あなた: ").strip()
        if not query:
            continue
        if query.lower() in ("q", "quit", "exit"):
            print("終了します。")
            break

        # 検索
        hits = search(collection, query)

        # 根拠表示
        print("\n─── 検索結果（根拠） ───")
        for i, h in enumerate(hits, 1):
            print(f"  [{i}] {h['text']}")
            print(f"       カテゴリ: {h['category']} ／ 類似度: {h['score']}")
        print("─────────────────────────\n")

        # 回答生成
        answer = generate_answer(query, hits)
        print(f"AI: {answer}\n")


if __name__ == "__main__":
    main()
