import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '../constants/colors';
import { useNavigation } from '@react-navigation/native';

const QuickAction = ({
  icon,
  label,
  onPress,
  color,
}: {
  icon: string;
  label: string;
  onPress: () => void;
  color: string;
}) => (
  <TouchableOpacity style={styles.quickAction} onPress={onPress}>
    <View style={[styles.quickActionIcon, { backgroundColor: color + '22' }]}>
      <Ionicons name={icon as any} size={26} color={color} />
    </View>
    <Text style={styles.quickActionLabel}>{label}</Text>
  </TouchableOpacity>
);

const InfoCard = ({
  title,
  value,
  subtitle,
  icon,
}: {
  title: string;
  value: string;
  subtitle: string;
  icon: string;
}) => (
  <View style={styles.infoCard}>
    <View style={styles.infoCardHeader}>
      <Text style={styles.infoCardTitle}>{title}</Text>
      <Ionicons name={icon as any} size={18} color={Colors.accent} />
    </View>
    <Text style={styles.infoCardValue}>{value}</Text>
    <Text style={styles.infoCardSubtitle}>{subtitle}</Text>
  </View>
);

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  const today = new Date();
  const dateStr = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />

      {/* ヘッダー */}
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View>
            <Text style={styles.headerGreeting}>おはようございます</Text>
            <Text style={styles.headerTitle}>Emport AI</Text>
            <Text style={styles.headerDate}>{dateStr}</Text>
          </View>
          <View style={styles.headerLogo}>
            <Ionicons name="briefcase" size={40} color={Colors.accent} />
          </View>
        </View>
      </View>

      <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>
        {/* クイックアクション */}
        <Text style={styles.sectionTitle}>クイックアクション</Text>
        <View style={styles.quickActions}>
          <QuickAction
            icon="chatbubbles"
            label="AI相談"
            onPress={() => navigation.navigate('Chat')}
            color={Colors.accent}
          />
          <QuickAction
            icon="cash"
            label="補助金"
            onPress={() => navigation.navigate('Subsidy')}
            color="#4CAF50"
          />
          <QuickAction
            icon="bar-chart"
            label="ツール"
            onPress={() => navigation.navigate('Tools')}
            color="#2196F3"
          />
          <QuickAction
            icon="settings"
            label="設定"
            onPress={() => navigation.navigate('Settings')}
            color={Colors.textSecondary}
          />
        </View>

        {/* 情報カード */}
        <Text style={styles.sectionTitle}>経営情報</Text>
        <View style={styles.infoCards}>
          <InfoCard
            title="AI相談"
            value="24時間対応"
            subtitle="経営・財務・マーケティング"
            icon="chatbubble-ellipses"
          />
          <InfoCard
            title="補助金情報"
            value="最大450万円"
            subtitle="デジタル化推進補助金2026"
            icon="cash"
          />
        </View>
        <View style={styles.infoCards}>
          <InfoCard
            title="対応業種"
            value="全業種対応"
            subtitle="製造・飲食・小売・サービス業"
            icon="business"
          />
          <InfoCard
            title="相談実績"
            value="累計1,000件+"
            subtitle="中小企業オーナー向け"
            icon="people"
          />
        </View>

        {/* 今日のTIP */}
        <Text style={styles.sectionTitle}>今日の経営TIP</Text>
        <TouchableOpacity
          style={styles.tipCard}
          onPress={() => navigation.navigate('Chat')}
        >
          <Ionicons name="bulb" size={24} color={Colors.accent} />
          <Text style={styles.tipTitle}>補助金申請のコツ</Text>
          <Text style={styles.tipBody}>
            2026年度のデジタル化推進補助金は申請枠が拡大されました。
            AI導入・システム構築費用の最大2/3が補助対象になります。
            まずAIに相談して、あなたの会社に合った申請計画を立てましょう。
          </Text>
          <View style={styles.tipAction}>
            <Text style={styles.tipActionText}>AIに相談する</Text>
            <Ionicons name="arrow-forward" size={16} color={Colors.accent} />
          </View>
        </TouchableOpacity>

        {/* よく使う機能 */}
        <Text style={styles.sectionTitle}>よく使われる相談テーマ</Text>
        {[
          { icon: 'trending-up', text: '売上を上げるにはどうすればいいか？', color: Colors.accent },
          { icon: 'people', text: '採用・人材育成の進め方', color: '#4CAF50' },
          { icon: 'phone-portrait', text: '自社のDX化・AI活用方法', color: '#2196F3' },
          { icon: 'cash-outline', text: '資金調達・補助金の申請方法', color: '#9C27B0' },
          { icon: 'document-text', text: '経営計画の作り方', color: '#FF9800' },
        ].map((item, idx) => (
          <TouchableOpacity
            key={idx}
            style={styles.themeItem}
            onPress={() => navigation.navigate('Chat')}
          >
            <View style={[styles.themeIcon, { backgroundColor: item.color + '22' }]}>
              <Ionicons name={item.icon as any} size={20} color={item.color} />
            </View>
            <Text style={styles.themeText}>{item.text}</Text>
            <Ionicons name="chevron-forward" size={16} color={Colors.textMuted} />
          </TouchableOpacity>
        ))}

        <View style={{ height: 30 }} />
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
    paddingBottom: 24,
    paddingHorizontal: 20,
    backgroundColor: Colors.primary,
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerGreeting: {
    color: Colors.textSecondary,
    fontSize: 13,
  },
  headerTitle: {
    color: Colors.text,
    fontSize: 28,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
  headerDate: {
    color: Colors.accentLight,
    fontSize: 12,
    marginTop: 2,
  },
  headerLogo: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: Colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: Colors.accent,
  },
  body: {
    flex: 1,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    color: Colors.textSecondary,
    fontSize: 13,
    fontWeight: '600',
    letterSpacing: 0.5,
    marginTop: 20,
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickAction: {
    alignItems: 'center',
    flex: 1,
  },
  quickActionIcon: {
    width: 56,
    height: 56,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 6,
  },
  quickActionLabel: {
    color: Colors.text,
    fontSize: 11,
    fontWeight: '500',
  },
  infoCards: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  infoCard: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 14,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  infoCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  infoCardTitle: {
    color: Colors.textSecondary,
    fontSize: 11,
  },
  infoCardValue: {
    color: Colors.text,
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  infoCardSubtitle: {
    color: Colors.textMuted,
    fontSize: 10,
  },
  tipCard: {
    backgroundColor: Colors.primary,
    borderRadius: 16,
    padding: 18,
    marginBottom: 4,
    borderWidth: 1,
    borderColor: Colors.secondary,
  },
  tipTitle: {
    color: Colors.accentLight,
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 8,
    marginBottom: 8,
  },
  tipBody: {
    color: Colors.textSecondary,
    fontSize: 13,
    lineHeight: 20,
    marginBottom: 14,
  },
  tipAction: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  tipActionText: {
    color: Colors.accent,
    fontSize: 13,
    fontWeight: '600',
  },
  themeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    gap: 12,
  },
  themeIcon: {
    width: 40,
    height: 40,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  themeText: {
    color: Colors.text,
    fontSize: 13,
    flex: 1,
  },
});
