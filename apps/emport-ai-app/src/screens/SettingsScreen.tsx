import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';
import { getApiKey, saveApiKey } from '../services/ApiService';

export default function SettingsScreen() {
  const [apiKey, setApiKey] = useState('');
  const [saved, setSaved] = useState(false);
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    getApiKey().then((k) => {
      if (k) setApiKey(k);
    });
  }, []);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      Alert.alert('エラー', 'APIキーを入力してください。');
      return;
    }
    await saveApiKey(apiKey.trim());
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>設定</Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* APIキー設定 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Claude API キー</Text>
          <View style={styles.inputRow}>
            <TextInput
              style={styles.input}
              value={apiKey}
              onChangeText={setApiKey}
              placeholder="sk-ant-api..."
              placeholderTextColor={Colors.textMuted}
              secureTextEntry={!showKey}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <TouchableOpacity
              style={styles.eyeBtn}
              onPress={() => setShowKey(!showKey)}
            >
              <Ionicons
                name={showKey ? 'eye-off' : 'eye'}
                size={20}
                color={Colors.textSecondary}
              />
            </TouchableOpacity>
          </View>
          <Text style={styles.hint}>
            Anthropic Console からAPIキーを取得してください
          </Text>
          <TouchableOpacity
            style={styles.linkBtn}
            onPress={() => Linking.openURL('https://console.anthropic.com/')}
          >
            <Ionicons name="open-outline" size={14} color={Colors.accent} />
            <Text style={styles.linkText}>console.anthropic.com を開く</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.saveBtn, saved && styles.saveBtnSuccess]}
            onPress={handleSave}
          >
            <Ionicons
              name={saved ? 'checkmark-circle' : 'save'}
              size={18}
              color={Colors.background}
            />
            <Text style={styles.saveBtnText}>{saved ? '保存しました！' : 'APIキーを保存'}</Text>
          </TouchableOpacity>
        </View>

        {/* アプリについて */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Emport AI について</Text>
          {[
            { label: 'バージョン', value: '1.0.0', icon: 'information-circle-outline' },
            { label: '開発', value: 'Emport AI 株式会社', icon: 'business-outline' },
            { label: 'サポート', value: 'support@emport-ai.com', icon: 'mail-outline' },
          ].map((item) => (
            <View key={item.label} style={styles.infoRow}>
              <Ionicons name={item.icon as any} size={18} color={Colors.textSecondary} />
              <Text style={styles.infoLabel}>{item.label}</Text>
              <Text style={styles.infoValue}>{item.value}</Text>
            </View>
          ))}
        </View>

        {/* リンク */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>リンク</Text>
          {[
            {
              label: 'プライバシーポリシー',
              url: 'https://emport-ai.vercel.app/',
              icon: 'shield-checkmark-outline',
            },
            {
              label: '利用規約',
              url: 'https://emport-ai.vercel.app/',
              icon: 'document-text-outline',
            },
            {
              label: 'Emport AIウェブサイト',
              url: 'https://emport-ai.vercel.app/',
              icon: 'globe-outline',
            },
          ].map((item) => (
            <TouchableOpacity
              key={item.label}
              style={styles.linkRow}
              onPress={() => Linking.openURL(item.url)}
            >
              <Ionicons name={item.icon as any} size={18} color={Colors.textSecondary} />
              <Text style={styles.linkRowText}>{item.label}</Text>
              <Ionicons name="chevron-forward" size={16} color={Colors.textMuted} />
            </TouchableOpacity>
          ))}
        </View>

        <View style={{ height: 50 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    paddingTop: 50,
    paddingBottom: 16,
    paddingHorizontal: 16,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerTitle: {
    color: Colors.text,
    fontSize: 22,
    fontWeight: 'bold',
  },
  section: {
    margin: 16,
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  sectionTitle: {
    color: Colors.textSecondary,
    fontSize: 12,
    fontWeight: '600',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
    marginBottom: 14,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.background,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    marginBottom: 8,
  },
  input: {
    flex: 1,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: Colors.text,
    fontSize: 14,
  },
  eyeBtn: {
    padding: 12,
  },
  hint: {
    color: Colors.textMuted,
    fontSize: 11,
    marginBottom: 8,
  },
  linkBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginBottom: 14,
  },
  linkText: {
    color: Colors.accent,
    fontSize: 12,
  },
  saveBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: Colors.accent,
    borderRadius: 10,
    paddingVertical: 12,
  },
  saveBtnSuccess: {
    backgroundColor: Colors.success,
  },
  saveBtnText: {
    color: Colors.background,
    fontSize: 14,
    fontWeight: '700',
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    gap: 10,
  },
  infoLabel: {
    color: Colors.textSecondary,
    fontSize: 13,
    flex: 1,
  },
  infoValue: {
    color: Colors.text,
    fontSize: 13,
  },
  linkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    gap: 10,
  },
  linkRowText: {
    color: Colors.text,
    fontSize: 13,
    flex: 1,
  },
});
