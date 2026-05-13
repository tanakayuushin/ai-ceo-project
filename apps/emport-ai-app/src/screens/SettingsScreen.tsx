import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';

export default function SettingsScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>設定</Text>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* サービス情報 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>サービス</Text>
          <View style={styles.infoCard}>
            <View style={styles.planBadge}>
              <Ionicons name="sparkles" size={16} color={Colors.accent} />
              <Text style={styles.planText}>Emport AI 経営アドバイザー</Text>
            </View>
            <Text style={styles.planDesc}>
              AIが経営の悩みにいつでも回答。APIキー設定不要でそのままご利用いただけます。
            </Text>
          </View>
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
  infoCard: {
    gap: 8,
  },
  planBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  planText: {
    color: Colors.accent,
    fontSize: 15,
    fontWeight: '700',
  },
  planDesc: {
    color: Colors.textSecondary,
    fontSize: 13,
    lineHeight: 20,
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
