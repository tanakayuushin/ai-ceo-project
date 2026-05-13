import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from '../constants/colors';
import { useNavigation } from '@react-navigation/native';

const MEMO_KEY = 'emport_memos';
const CHAT_COUNT_KEY = 'emport_chat_count';

function KpiCard({
  label,
  value,
  unit,
  icon,
  color,
  badge,
}: {
  label: string;
  value: string | number;
  unit: string;
  icon: string;
  color: string;
  badge?: string;
}) {
  return (
    <View style={[styles.kpiCard, { borderTopColor: color }]}>
      <View style={styles.kpiHeader}>
        <View style={[styles.kpiIconBox, { backgroundColor: color + '22' }]}>
          <Ionicons name={icon as any} size={16} color={color} />
        </View>
        {badge && (
          <View style={[styles.badge, { backgroundColor: color + '33' }]}>
            <Text style={[styles.badgeText, { color }]}>{badge}</Text>
          </View>
        )}
      </View>
      <Text style={styles.kpiValue}>{value}</Text>
      <Text style={styles.kpiUnit}>{unit}</Text>
      <Text style={styles.kpiLabel}>{label}</Text>
    </View>
  );
}

function ProgressBar({ value, total, color }: { value: number; total: number; color: string }) {
  const pct = total === 0 ? 0 : Math.min(value / total, 1);
  return (
    <View style={styles.progressTrack}>
      <View style={[styles.progressFill, { width: `${pct * 100}%` as any, backgroundColor: color }]} />
    </View>
  );
}

function StatusItem({
  label,
  sub,
  status,
  onPress,
}: {
  label: string;
  sub: string;
  status: 'urgent' | 'warning' | 'done' | 'info';
  onPress: () => void;
}) {
  const statusMap = {
    urgent: { color: Colors.error, dot: '●', text: '要対応' },
    warning: { color: Colors.warning, dot: '●', text: '確認中' },
    done: { color: Colors.success, dot: '●', text: '完了' },
    info: { color: Colors.accent, dot: '●', text: '検討中' },
  };
  const s = statusMap[status];
  return (
    <TouchableOpacity style={styles.statusItem} onPress={onPress}>
      <Text style={[styles.statusDot, { color: s.color }]}>{s.dot}</Text>
      <View style={styles.statusBody}>
        <Text style={styles.statusLabel}>{label}</Text>
        <Text style={styles.statusSub}>{sub}</Text>
      </View>
      <View style={[styles.statusBadge, { backgroundColor: s.color + '22' }]}>
        <Text style={[styles.statusBadgeText, { color: s.color }]}>{s.text}</Text>
      </View>
    </TouchableOpacity>
  );
}

export default function HomeScreen() {
  const navigation = useNavigation<any>();
  const today = new Date();
  const dateStr = `${today.getFullYear()}/${today.getMonth() + 1}/${today.getDate()}`;
  const weekDay = ['日', '月', '火', '水', '木', '金', '土'][today.getDay()];

  const [memoCount, setMemoCount] = useState(0);
  const [chatCount, setChatCount] = useState(0);

  useEffect(() => {
    AsyncStorage.getItem(MEMO_KEY).then((raw) => {
      if (raw) setMemoCount(JSON.parse(raw).length);
    });
    AsyncStorage.getItem(CHAT_COUNT_KEY).then((raw) => {
      if (raw) setChatCount(parseInt(raw, 10));
    });
  }, []);

  const monthTarget = 10;

  return (
    <View style={styles.container}>
      {/* ヘッダー */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerDate}>{dateStr}（{weekDay}）</Text>
          <Text style={styles.headerTitle}>経営ダッシュボード</Text>
        </View>
        <TouchableOpacity
          style={styles.headerBtn}
          onPress={() => navigation.navigate('Chat')}
        >
          <Ionicons name="chatbubble-ellipses" size={22} color={Colors.accent} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.body} showsVerticalScrollIndicator={false}>

        {/* KPI カード */}
        <Text style={styles.sectionTitle}>今月のサマリー</Text>
        <View style={styles.kpiRow}>
          <KpiCard
            label="AI相談"
            value={chatCount}
            unit="件"
            icon="chatbubbles"
            color={Colors.accent}
            badge={chatCount > 0 ? `目標${monthTarget}件` : undefined}
          />
          <KpiCard
            label="メモ"
            value={memoCount}
            unit="件"
            icon="document-text"
            color="#2196F3"
          />
          <KpiCard
            label="補助金"
            value={3}
            unit="候補"
            icon="cash"
            color="#4CAF50"
            badge="最大450万"
          />
          <KpiCard
            label="アラート"
            value={2}
            unit="件"
            icon="alert-circle"
            color={Colors.error}
            badge="要対応"
          />
        </View>

        {/* 月次目標 */}
        <Text style={styles.sectionTitle}>今月の進捗</Text>
        <View style={styles.progressCard}>
          <View style={styles.progressRow}>
            <View>
              <Text style={styles.progressTitle}>AI相談 月次目標</Text>
              <Text style={styles.progressSub}>{chatCount} / {monthTarget} 件</Text>
            </View>
            <Text style={[styles.progressPct, { color: Colors.accent }]}>
              {Math.round((chatCount / monthTarget) * 100)}%
            </Text>
          </View>
          <ProgressBar value={chatCount} total={monthTarget} color={Colors.accent} />

          <View style={[styles.progressRow, { marginTop: 16 }]}>
            <View>
              <Text style={styles.progressTitle}>補助金申請準備</Text>
              <Text style={styles.progressSub}>2 / 3 件 書類整備中</Text>
            </View>
            <Text style={[styles.progressPct, { color: '#4CAF50' }]}>67%</Text>
          </View>
          <ProgressBar value={2} total={3} color="#4CAF50" />
        </View>

        {/* アクションリスト */}
        <Text style={styles.sectionTitle}>アクションリスト</Text>
        <View style={styles.statusCard}>
          <StatusItem
            label="デジタル化AI導入補助金"
            sub="締切 2026/6/30 — 申請書類未完"
            status="urgent"
            onPress={() => navigation.navigate('Subsidy')}
          />
          <View style={styles.divider} />
          <StatusItem
            label="小規模事業者持続化補助金"
            sub="締切 2026/5月 — 書類確認中"
            status="warning"
            onPress={() => navigation.navigate('Subsidy')}
          />
          <View style={styles.divider} />
          <StatusItem
            label="ものづくり補助金"
            sub="申請完了 — 結果待ち"
            status="done"
            onPress={() => navigation.navigate('Subsidy')}
          />
          <View style={styles.divider} />
          <StatusItem
            label="経営計画の見直し"
            sub="AIに相談して戦略を整理する"
            status="info"
            onPress={() => navigation.navigate('Chat')}
          />
        </View>

        {/* クイックアクション */}
        <Text style={styles.sectionTitle}>クイックアクション</Text>
        <View style={styles.quickGrid}>
          {[
            { icon: 'chatbubbles', label: 'AI相談', sub: '24時間対応', color: Colors.accent, screen: 'Chat' },
            { icon: 'cash', label: '補助金', sub: '最大450万円', color: '#4CAF50', screen: 'Subsidy' },
            { icon: 'document-text', label: '商談メモ', sub: `${memoCount}件保存中`, color: '#2196F3', screen: 'Memo' },
            { icon: 'settings', label: '設定', sub: 'APIキー管理', color: Colors.textSecondary, screen: 'Settings' },
          ].map((item) => (
            <TouchableOpacity
              key={item.screen}
              style={styles.quickCard}
              onPress={() => navigation.navigate(item.screen)}
            >
              <View style={[styles.quickIcon, { backgroundColor: item.color + '22' }]}>
                <Ionicons name={item.icon as any} size={24} color={item.color} />
              </View>
              <Text style={styles.quickLabel}>{item.label}</Text>
              <Text style={styles.quickSub}>{item.sub}</Text>
            </TouchableOpacity>
          ))}
        </View>

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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 52,
    paddingBottom: 16,
    paddingHorizontal: 20,
    backgroundColor: Colors.primary,
    borderBottomWidth: 1,
    borderBottomColor: Colors.secondary,
  },
  headerDate: {
    color: Colors.textMuted,
    fontSize: 12,
    marginBottom: 2,
  },
  headerTitle: {
    color: Colors.text,
    fontSize: 20,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  headerBtn: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.secondary,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: Colors.accent + '55',
  },
  body: {
    flex: 1,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    color: Colors.textMuted,
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 1,
    textTransform: 'uppercase',
    marginTop: 20,
    marginBottom: 10,
  },
  kpiRow: {
    flexDirection: 'row',
    gap: 8,
  },
  kpiCard: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 10,
    borderWidth: 1,
    borderColor: Colors.border,
    borderTopWidth: 3,
  },
  kpiHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  kpiIconBox: {
    width: 28,
    height: 28,
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badge: {
    borderRadius: 6,
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
  badgeText: {
    fontSize: 8,
    fontWeight: '700',
  },
  kpiValue: {
    color: Colors.text,
    fontSize: 22,
    fontWeight: '700',
    lineHeight: 26,
  },
  kpiUnit: {
    color: Colors.textSecondary,
    fontSize: 10,
    marginBottom: 2,
  },
  kpiLabel: {
    color: Colors.textMuted,
    fontSize: 10,
  },
  progressCard: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  progressRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    marginBottom: 10,
  },
  progressTitle: {
    color: Colors.text,
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 2,
  },
  progressSub: {
    color: Colors.textMuted,
    fontSize: 11,
  },
  progressPct: {
    fontSize: 20,
    fontWeight: '700',
  },
  progressTrack: {
    height: 6,
    backgroundColor: Colors.border,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: 6,
    borderRadius: 3,
  },
  statusCard: {
    backgroundColor: Colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: Colors.border,
    overflow: 'hidden',
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 12,
    gap: 10,
  },
  statusDot: {
    fontSize: 10,
  },
  statusBody: {
    flex: 1,
  },
  statusLabel: {
    color: Colors.text,
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 2,
  },
  statusSub: {
    color: Colors.textMuted,
    fontSize: 11,
  },
  statusBadge: {
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  statusBadgeText: {
    fontSize: 10,
    fontWeight: '700',
  },
  divider: {
    height: 1,
    backgroundColor: Colors.border,
    marginHorizontal: 14,
  },
  quickGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  quickCard: {
    width: '47.5%',
    backgroundColor: Colors.surface,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  quickIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickLabel: {
    color: Colors.text,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  quickSub: {
    color: Colors.textMuted,
    fontSize: 11,
  },
});
