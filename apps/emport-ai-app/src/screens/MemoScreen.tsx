import React, { useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, Alert, KeyboardAvoidingView, Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '../constants/colors';

interface Memo {
  id: string;
  title: string;
  body: string;
  company: string;
  createdAt: string;
  tag: string;
}

const MEMO_KEY = 'emport_memos';
const TAGS = ['商談', '補助金', '経営', 'アイデア', 'その他'];
const TAG_COLORS: Record<string, string> = {
  '商談': Colors.accent,
  '補助金': '#4CAF50',
  '経営': '#2196F3',
  'アイデア': '#9C27B0',
  'その他': Colors.textMuted,
};

export default function MemoScreen() {
  const [memos, setMemos] = useState<Memo[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [company, setCompany] = useState('');
  const [selectedTag, setSelectedTag] = useState('商談');
  const [search, setSearch] = useState('');

  useEffect(() => {
    loadMemos();
  }, []);

  const loadMemos = async () => {
    const raw = await AsyncStorage.getItem(MEMO_KEY);
    if (raw) setMemos(JSON.parse(raw));
  };

  const saveMemo = async () => {
    if (!title.trim()) { Alert.alert('タイトルを入力してください'); return; }
    const memo: Memo = {
      id: Date.now().toString(),
      title: title.trim(),
      body: body.trim(),
      company: company.trim(),
      createdAt: new Date().toLocaleDateString('ja-JP'),
      tag: selectedTag,
    };
    const updated = [memo, ...memos];
    setMemos(updated);
    await AsyncStorage.setItem(MEMO_KEY, JSON.stringify(updated));
    setTitle(''); setBody(''); setCompany(''); setShowForm(false);
  };

  const deleteMemo = (id: string) => {
    Alert.alert('削除確認', 'このメモを削除しますか？', [
      { text: 'キャンセル', style: 'cancel' },
      {
        text: '削除', style: 'destructive', onPress: async () => {
          const updated = memos.filter(m => m.id !== id);
          setMemos(updated);
          await AsyncStorage.setItem(MEMO_KEY, JSON.stringify(updated));
        }
      }
    ]);
  };

  const filtered = memos.filter(m =>
    m.title.includes(search) || m.company.includes(search) || m.body.includes(search)
  );

  return (
    <KeyboardAvoidingView style={styles.container} behavior="padding" keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>商談メモ</Text>
        <TouchableOpacity onPress={() => setShowForm(!showForm)}>
          <Ionicons name={showForm ? 'close' : 'add-circle'} size={28} color={Colors.accent} />
        </TouchableOpacity>
      </View>

      {showForm && (
        <View style={styles.form}>
          <TextInput style={styles.input} value={title} onChangeText={setTitle}
            placeholder="タイトル（例：山田建設 初回商談）" placeholderTextColor={Colors.textMuted} />
          <TextInput style={styles.input} value={company} onChangeText={setCompany}
            placeholder="会社名" placeholderTextColor={Colors.textMuted} />
          <View style={styles.tagRow}>
            {TAGS.map(t => (
              <TouchableOpacity key={t} onPress={() => setSelectedTag(t)}
                style={[styles.tagChip, { borderColor: TAG_COLORS[t], backgroundColor: selectedTag === t ? TAG_COLORS[t] + '33' : 'transparent' }]}>
                <Text style={[styles.tagChipText, { color: TAG_COLORS[t] }]}>{t}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <TextInput style={[styles.input, styles.bodyInput]} value={body} onChangeText={setBody}
            placeholder="メモ内容..." placeholderTextColor={Colors.textMuted} multiline />
          <TouchableOpacity style={styles.saveBtn} onPress={saveMemo}>
            <Text style={styles.saveBtnText}>保存する</Text>
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.searchRow}>
        <Ionicons name="search" size={16} color={Colors.textMuted} />
        <TextInput style={styles.searchInput} value={search} onChangeText={setSearch}
          placeholder="メモを検索..." placeholderTextColor={Colors.textMuted} />
      </View>

      <ScrollView showsVerticalScrollIndicator={false} style={styles.list}>
        {filtered.length === 0 && (
          <View style={styles.empty}>
            <Ionicons name="document-outline" size={48} color={Colors.textMuted} />
            <Text style={styles.emptyText}>メモがありません{'\n'}右上の＋から追加できます</Text>
          </View>
        )}
        {filtered.map(m => (
          <View key={m.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <View style={[styles.tag, { backgroundColor: TAG_COLORS[m.tag] + '22' }]}>
                <Text style={[styles.tagText, { color: TAG_COLORS[m.tag] }]}>{m.tag}</Text>
              </View>
              <Text style={styles.date}>{m.createdAt}</Text>
            </View>
            <Text style={styles.cardTitle}>{m.title}</Text>
            {m.company ? <Text style={styles.cardCompany}>🏢 {m.company}</Text> : null}
            {m.body ? <Text style={styles.cardBody} numberOfLines={3}>{m.body}</Text> : null}
            <TouchableOpacity style={styles.deleteBtn} onPress={() => deleteMemo(m.id)}>
              <Ionicons name="trash-outline" size={16} color={Colors.textMuted} />
            </TouchableOpacity>
          </View>
        ))}
        <View style={{ height: 40 }} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingTop: 50, paddingBottom: 16, paddingHorizontal: 16,
    backgroundColor: Colors.surface, borderBottomWidth: 1, borderBottomColor: Colors.border,
  },
  headerTitle: { color: Colors.text, fontSize: 22, fontWeight: 'bold' },
  form: {
    backgroundColor: Colors.surface, padding: 16,
    borderBottomWidth: 1, borderBottomColor: Colors.border,
  },
  input: {
    backgroundColor: Colors.background, borderRadius: 10, padding: 12,
    color: Colors.text, fontSize: 14, borderWidth: 1, borderColor: Colors.border, marginBottom: 10,
  },
  bodyInput: { height: 80, textAlignVertical: 'top' },
  tagRow: { flexDirection: 'row', gap: 8, flexWrap: 'wrap', marginBottom: 10 },
  tagChip: {
    paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1,
  },
  tagChipText: { fontSize: 12, fontWeight: '600' },
  saveBtn: {
    backgroundColor: Colors.accent, borderRadius: 10, padding: 12, alignItems: 'center',
  },
  saveBtnText: { color: Colors.background, fontWeight: '700', fontSize: 14 },
  searchRow: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    paddingHorizontal: 16, paddingVertical: 10,
    backgroundColor: Colors.surface, borderBottomWidth: 1, borderBottomColor: Colors.border,
  },
  searchInput: { flex: 1, color: Colors.text, fontSize: 14 },
  list: { flex: 1, padding: 16 },
  empty: { alignItems: 'center', paddingTop: 60, gap: 12 },
  emptyText: { color: Colors.textMuted, fontSize: 14, textAlign: 'center', lineHeight: 22 },
  card: {
    backgroundColor: Colors.surface, borderRadius: 14, padding: 14,
    marginBottom: 12, borderWidth: 1, borderColor: Colors.border,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  tag: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: 20 },
  tagText: { fontSize: 11, fontWeight: '600' },
  date: { color: Colors.textMuted, fontSize: 11 },
  cardTitle: { color: Colors.text, fontSize: 15, fontWeight: '600', marginBottom: 4 },
  cardCompany: { color: Colors.textSecondary, fontSize: 12, marginBottom: 6 },
  cardBody: { color: Colors.textSecondary, fontSize: 13, lineHeight: 20 },
  deleteBtn: { position: 'absolute', top: 14, right: 14 },
});
