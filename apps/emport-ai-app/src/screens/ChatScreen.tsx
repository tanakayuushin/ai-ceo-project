import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Message, sendMessage, getApiKey, SYSTEM_PROMPT } from '../services/ApiService';

const CHAT_COUNT_KEY = 'emport_chat_count';
import { useNavigation } from '@react-navigation/native';

const SUGGESTED_TOPICS = [
  '売上を増やすには？',
  '補助金の申請方法',
  '採用コストを下げたい',
  'SNSマーケティング入門',
  'AI導入の始め方',
  '資金繰りの改善策',
];

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user';
  return (
    <View style={[styles.messagRow, isUser ? styles.userRow : styles.aiRow]}>
      {!isUser && (
        <View style={styles.aiAvatar}>
          <Ionicons name="sparkles" size={16} color={Colors.accent} />
        </View>
      )}
      <View
        style={[
          styles.bubble,
          isUser ? styles.userBubble : styles.aiBubble,
        ]}
      >
        <Text style={[styles.bubbleText, isUser ? styles.userText : styles.aiText]}>
          {message.content}
        </Text>
      </View>
    </View>
  );
}

export default function ChatScreen() {
  const navigation = useNavigation<any>();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content:
        'こんにちは！Emport AIの経営アドバイザーです。\n\n経営・財務・マーケティング・補助金申請など、何でもご相談ください。どのようなお悩みがありますか？',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState<string | null>(null);
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    getApiKey().then(setApiKey);
  }, []);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, []);

  const handleSend = useCallback(async (text?: string) => {
    const content = (text || input).trim();
    if (!content || loading) return;

    if (!apiKey) {
      Alert.alert(
        'APIキーが必要です',
        '設定画面でClaude APIキーを入力してください。',
        [
          { text: 'キャンセル', style: 'cancel' },
          { text: '設定へ', onPress: () => navigation.navigate('Settings') },
        ]
      );
      return;
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    scrollToBottom();

    try {
      const raw = await AsyncStorage.getItem(CHAT_COUNT_KEY);
      const count = raw ? parseInt(raw, 10) + 1 : 1;
      await AsyncStorage.setItem(CHAT_COUNT_KEY, String(count));

      const reply = await sendMessage(newMessages, SYSTEM_PROMPT, apiKey);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (e: any) {
      Alert.alert('エラー', e.message || 'AIとの通信に失敗しました。');
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  }, [input, loading, apiKey, messages, navigation, scrollToBottom]);

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'padding'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      {/* ヘッダー */}
      <View style={styles.header}>
        <View style={styles.aiInfo}>
          <View style={styles.aiIcon}>
            <Ionicons name="sparkles" size={20} color={Colors.accent} />
          </View>
          <View>
            <Text style={styles.aiName}>経営AIアドバイザー</Text>
            <Text style={styles.aiStatus}>● オンライン</Text>
          </View>
        </View>
        <TouchableOpacity
          onPress={() => {
            setMessages([
              {
                id: '0',
                role: 'assistant',
                content: 'チャットをリセットしました。新しいご相談をどうぞ！',
                timestamp: new Date(),
              },
            ]);
          }}
        >
          <Ionicons name="refresh" size={22} color={Colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* メッセージ一覧 */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(m) => m.id}
        renderItem={({ item }) => <MessageBubble message={item} />}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={scrollToBottom}
        showsVerticalScrollIndicator={false}
        ListFooterComponent={
          loading ? (
            <View style={styles.typingIndicator}>
              <View style={styles.aiAvatar}>
                <Ionicons name="sparkles" size={16} color={Colors.accent} />
              </View>
              <View style={styles.typingBubble}>
                <ActivityIndicator size="small" color={Colors.accent} />
                <Text style={styles.typingText}>考え中...</Text>
              </View>
            </View>
          ) : null
        }
      />

      {/* 提案トピック（初回のみ） */}
      {messages.length <= 1 && (
        <View style={styles.suggestions}>
          <FlatList
            data={SUGGESTED_TOPICS}
            keyExtractor={(t) => t}
            horizontal
            showsHorizontalScrollIndicator={false}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => handleSend(item)}
              >
                <Text style={styles.suggestionText}>{item}</Text>
              </TouchableOpacity>
            )}
            contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
          />
        </View>
      )}

      {/* 入力欄 */}
      <View style={styles.inputArea}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="経営の相談を入力..."
          placeholderTextColor={Colors.textMuted}
          multiline
          maxLength={1000}
          returnKeyType="default"
        />
        <TouchableOpacity
          style={[styles.sendBtn, (!input.trim() || loading) && styles.sendBtnDisabled]}
          onPress={() => handleSend()}
          disabled={!input.trim() || loading}
        >
          <Ionicons
            name="send"
            size={20}
            color={!input.trim() || loading ? Colors.textMuted : Colors.accent}
          />
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 50,
    paddingBottom: 12,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  aiInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  aiIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: Colors.accent,
  },
  aiName: {
    color: Colors.text,
    fontSize: 15,
    fontWeight: '600',
  },
  aiStatus: {
    color: Colors.success,
    fontSize: 11,
  },
  messageList: {
    padding: 16,
    gap: 12,
  },
  messagRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    marginBottom: 8,
  },
  userRow: {
    justifyContent: 'flex-end',
  },
  aiRow: {
    justifyContent: 'flex-start',
    gap: 8,
  },
  aiAvatar: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.accent,
  },
  bubble: {
    maxWidth: '80%',
    borderRadius: 16,
    padding: 12,
  },
  userBubble: {
    backgroundColor: Colors.chatUser,
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    backgroundColor: Colors.chatAI,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  bubbleText: {
    fontSize: 14,
    lineHeight: 21,
  },
  userText: {
    color: Colors.text,
  },
  aiText: {
    color: Colors.text,
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 4,
  },
  typingBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: Colors.chatAI,
    borderRadius: 16,
    padding: 12,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  typingText: {
    color: Colors.textSecondary,
    fontSize: 13,
  },
  suggestions: {
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
  },
  suggestionChip: {
    backgroundColor: Colors.surface,
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  suggestionText: {
    color: Colors.accent,
    fontSize: 12,
  },
  inputArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.background,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingTop: 10,
    paddingBottom: 10,
    color: Colors.text,
    fontSize: 14,
    maxHeight: 120,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sendBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.surface,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.accent,
  },
  sendBtnDisabled: {
    borderColor: Colors.border,
  },
});
