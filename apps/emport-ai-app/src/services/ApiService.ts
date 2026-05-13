import AsyncStorage from '@react-native-async-storage/async-storage';

const BACKEND_URL = 'https://web-production-487269.up.railway.app';
const MOBILE_API_TOKEN = 'emport-mobile-dev-2026';

const API_KEY_STORAGE = 'emport_api_key';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export async function getApiKey(): Promise<string | null> {
  return AsyncStorage.getItem(API_KEY_STORAGE);
}

export async function saveApiKey(key: string): Promise<void> {
  await AsyncStorage.setItem(API_KEY_STORAGE, key);
}

export async function sendMessage(
  messages: Message[],
  systemPrompt: string
): Promise<string> {
  const body = {
    messages: messages.map((m) => ({
      role: m.role,
      content: m.content,
    })),
    system: systemPrompt,
  };

  const res = await fetch(`${BACKEND_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${MOBILE_API_TOKEN}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API Error ${res.status}`);
  }

  const data = await res.json();
  return data.content;
}

export const SYSTEM_PROMPT = `あなたは「Emport AI」の経営AIアドバイザーです。
中小企業オーナーや起業家が抱える経営課題に対して、実践的で具体的なアドバイスを提供します。

【専門領域】
- 経営戦略・事業計画
- マーケティング・集客
- 財務・資金調達・補助金
- 人事・採用・組織運営
- DX推進・AI活用
- 営業・販路拡大

【回答スタイル】
- 簡潔で実行可能なアドバイス
- 具体的な数字や事例を使う
- 日本の中小企業の実情に合わせた提案
- 難しい専門用語は分かりやすく説明する
- 必要に応じて箇条書きや見出しを使う

常に経営者の立場に立ち、「今すぐできること」を中心にアドバイスしてください。`;
